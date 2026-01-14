import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, insert, update, delete
from sqlalchemy.exc import IntegrityError
from app.db.models import User, Referral, TrialSubscription, PaidSubscription, PromoBonusDays, PromoDiscount, PromoUse, SpecialSubscription, ExpiredSubscriptionNotification, NotificationMeta
from app.db.dealer import async_session_maker
from sqlalchemy.exc import SQLAlchemyError
from config import CHANNEL_ID

from aiogram.enums.chat_member_status import ChatMemberStatus


# 🔹 Проверка существования пользователя
async def user_exists(tg_id: int) -> bool:
    async with async_session_maker() as session:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None


# 🔹 Генерация реферального кода
def generate_ref_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# 🔹 Добавление пользователя
async def add_user(tg_id: int, username: str, full_name: str, referred_by: str | None = None):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        # Если пользователь новый — создаём
        if not user:
            user = User(
                tg_id=tg_id,
                username=username,
                full_name=full_name,
                created_at=datetime.now(),
            )
            session.add(user)
            await session.flush()

        # Генерация реферального кода (если нет)
        if not user.ref_code:
            while True:
                new_ref_code = generate_ref_code()
                exists = await session.execute(select(User).where(User.ref_code == new_ref_code))
                if not exists.scalar_one_or_none():
                    user.ref_code = new_ref_code
                    break

        # Если пользователь пришёл по реферальному коду
        if referred_by:
            result = await session.execute(select(User).where(User.ref_code == referred_by))
            referrer = result.scalar_one_or_none()

            if referrer and referrer.tg_id != tg_id:
                # Проверяем, нет ли уже связки реферал → реферер
                exists = await session.execute(
                    select(Referral).where(
                        and_(Referral.referrer_id == referrer.id,
                             Referral.referred_id == user.id)
                    )
                )

                if not exists.scalar_one_or_none():
                    # Создаём новую запись в реферальной таблице (лог записи)
                    new_ref = Referral(
                        referrer_id=referrer.id,
                        referred_id=user.id,
                        created_at=datetime.now(),
                    )
                    session.add(new_ref)

                    # ✅ Начисляем бонусные дни рефереру
                    referrer.bonus_days_balance = (referrer.bonus_days_balance or 0) + 2

                    # Запоминаем, кто пригласил
                    user.referred_by = referred_by

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


# 🔹 Получение реферального кода пользователя
async def get_ref_code(tg_id: int) -> str | None:
    async with async_session_maker() as session:
        query = select(User.ref_code).where(User.tg_id == tg_id)
        result = await session.execute(query)
        ref_code = result.scalar_one_or_none()
        return ref_code


# 🔹 Получение количества приглашённых пользователей
async def get_invited_count(tg_id: int) -> int:
    """
    Считает, сколько пользователей пришли по реферальной ссылке данного пользователя.
    """
    async with async_session_maker() as session:
        # Получаем ID пользователя
        query_user = select(User.id).where(User.tg_id == tg_id)
        result_user = await session.execute(query_user)
        user_id = result_user.scalar_one_or_none()
        if not user_id:
            return 0

        # Считаем количество приглашённых
        query_count = select(func.count()).where(Referral.referrer_id == user_id)
        result_count = await session.execute(query_count)
        count = result_count.scalar_one()
        return count
    

# 🔹 Проверяет, существует ли указанный реферальный код.
# 🔹 Возвращает True, если код найден, иначе False.
async def is_valid_ref_code(ref_code: str) -> bool:
    if not ref_code:
        return False

    async with async_session_maker() as session:
        query = select(User).where(User.ref_code == ref_code)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
    

# --- Проверка наличия пробного периода ---
async def has_trial(user_tg_id: int) -> bool:
    """
    Проверяет, активировал ли пользователь пробный период хотя бы один раз.
    Возвращает True, если запись существует, иначе False.
    """
    async with async_session_maker() as session:
        # Получаем ID пользователя
        user_id_query = await session.execute(select(User.id).where(User.tg_id == user_tg_id))
        user_id = user_id_query.scalar_one_or_none()
        if not user_id:
            return False

        # Проверяем наличие записей о пробном периоде
        trial_query = await session.execute(
            select(func.count(TrialSubscription.id)).where(TrialSubscription.user_id == user_id)
        )
        trial_count = trial_query.scalar_one()

        return trial_count > 0


# --- Активация пробного периода ---
async def activate_trial(user_tg_id: int) -> None:
    """
    Активирует пробный период для пользователя (создаёт запись в trial_subscriptions).
    Если пользователь не найден или уже активировал — ничего не делает.
    """
    async with async_session_maker() as session:
        # Получаем ID пользователя
        user_id_query = await session.execute(select(User.id).where(User.tg_id == user_tg_id))
        user_id = user_id_query.scalar_one_or_none()
        if not user_id:
            raise ValueError("Пользователь не найден в таблице users")

        # Проверяем, не активировал ли уже
        trial_exists_query = await session.execute(
            select(func.count(TrialSubscription.id)).where(TrialSubscription.user_id == user_id)
        )
        trial_exists = trial_exists_query.scalar_one() > 0
        if trial_exists:
            return  # уже активировал — ничего не делаем

        # Создаём новую запись
        trial = TrialSubscription(
            user_id=user_id,
            activated_at=datetime.utcnow()
        )
        session.add(trial)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise


# --- Проверка активной подписки ---
async def get_active_subscription_type(tg_id: int) -> str | None:
    """
    Проверяет, есть ли у пользователя активная подписка.
    Возвращает:
    - 'trial' — если пробная активна (3 дня с момента активации не прошли)
    - 'paid' — если активна платная подписка
    - None — если нет подписок
    """
    now = datetime.utcnow()

    async with async_session_maker() as session:
        # --- Проверяем платную подписку ---
        paid_query = await session.execute(
            select(PaidSubscription)
            .where(PaidSubscription.tg_id == tg_id, PaidSubscription.active == True)
            .order_by(PaidSubscription.id.desc())
            .limit(1)
        )
        paid = paid_query.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if paid and paid.expire_date:
            try:
                if paid.expire_date > now:
                    return "paid"
            except Exception:
                pass

        # --- Проверяем пробную подписку ---
        user_query = await session.execute(select(User.id).where(User.tg_id == tg_id))
        user_id = user_query.scalar_one_or_none()
        if not user_id:
            return None

        trial_query = await session.execute(
            select(TrialSubscription.activated_at)
            .where(TrialSubscription.user_id == user_id)
            .order_by(TrialSubscription.id.desc())
            .limit(1)
        )
        activated_at = trial_query.scalar_one_or_none()

        if activated_at:
            end_date = activated_at + timedelta(days=3)
            if now < end_date:
                return "trial"

        return None
    

async def add_paid_subscription(
    tg_id: int,
    plan_name: str,
    amount: float = 0,
    currency: str = "RUB",
    days: int = 30,
    uuid: str | None = None
):
    """Создаёт или продлевает платную подписку пользователя."""

    async with async_session_maker() as session:
        try:
            now = datetime.utcnow()

            result = await session.execute(
                select(PaidSubscription)
                .where(PaidSubscription.tg_id == tg_id, PaidSubscription.active == True)
                .order_by(PaidSubscription.id.desc())
                .limit(1)
            )
            active_sub = result.scalar_one_or_none()

            if active_sub:
                # Продление подписки
                new_expire = (active_sub.expire_date or now) + timedelta(days=days)
                await session.execute(
                    update(PaidSubscription)
                    .where(PaidSubscription.id == active_sub.id)
                    .values(
                        expire_date=new_expire,
                        plan_name=plan_name,
                        amount=amount,
                        currency=currency,
                    )
                )
            else:
                # Создание новой подписки
                expire_date = now + timedelta(days=days)
                session.add(PaidSubscription(
                    tg_id=tg_id,
                    plan_name=plan_name,
                    amount=amount,
                    currency=currency,
                    start_date=now,
                    expire_date=expire_date,
                    active=True,
                    uuid=uuid,
                ))

            await session.commit()

        except SQLAlchemyError:
            await session.rollback()
            raise

async def add_special_subscription(
    tg_id: int,
    plan_name: str,
    amount: float = 0,
    currency: str = "RUB",
    days: int = 30,
    uuid: str | None = None
):
    async with async_session_maker() as session:
        try:
            now = datetime.utcnow()

            result = await session.execute(
                select(SpecialSubscription)
                .where(SpecialSubscription.tg_id == tg_id, SpecialSubscription.active == True)
                .order_by(SpecialSubscription.id.desc())
                .limit(1)
            )
            active_sub = result.scalar_one_or_none()

            if active_sub:
                # Продление подписки
                new_expire = (active_sub.expire_date or now) + timedelta(days=days)
                await session.execute(
                    update(SpecialSubscription)
                    .where(SpecialSubscription.id == active_sub.id)
                    .values(
                        expire_date=new_expire,
                        plan_name=plan_name,
                        amount=amount,
                        currency=currency,
                    )
                )

            else:
                # Создание новой подписки
                expire_date = now + timedelta(days=days)
                session.add(SpecialSubscription(
                    tg_id=tg_id,
                    plan_name=plan_name,
                    amount=amount,
                    currency=currency,
                    start_date=now,
                    expire_date=expire_date,
                    active=True,
                    uuid=uuid
                ))

            await session.commit()

        except SQLAlchemyError:
            await session.rollback()
            raise

async def get_active_paid_subscription(tg_id: int):
    """Возвращает активную платную подписку пользователя (или None)."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(PaidSubscription)
            .where(PaidSubscription.tg_id == tg_id, PaidSubscription.active == True)
            .limit(1)
        )
        sub = result.scalar_one_or_none()

        if sub:
            return {
                "uuid": sub.uuid,
                "expire_date": sub.expire_date,
                "plan_name": sub.plan_name,
                "days": (sub.expire_date - sub.start_date).days if sub.start_date and sub.expire_date else None
            }
        return None
    
async def get_active_special_subscription(tg_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(SpecialSubscription)
            .where(SpecialSubscription.tg_id == tg_id, SpecialSubscription.active == True)
            .limit(1)
        )
        sub = result.scalar_one_or_none()

        if sub:
            return {
                "uuid": sub.uuid,
                "expire_date": sub.expire_date,
                "plan_name": sub.plan_name,
                "days": (
                    (sub.expire_date - sub.start_date).days
                    if sub.start_date and sub.expire_date
                    else None
                )
            }

        return None

# Возвращает UUID подписки, дату окончания, и бонусные дни
async def get_user_subscription_and_bonus(tg_id: int):
    async with async_session_maker() as session:
        # Получаем пользователя
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        # Получаем активную платную подписку
        result = await session.execute(
            select(PaidSubscription.uuid, PaidSubscription.expire_date)
            .where(PaidSubscription.tg_id == tg_id, PaidSubscription.active == True)
            .order_by(PaidSubscription.id.desc())
            .limit(1)
        )
        sub = result.first()
        if not sub:
            return None

        uuid, expire_date = sub

        return {
            "uuid": uuid,
            "expire_date": expire_date,
            "bonus_days": user.bonus_days_balance or 0
        }
    
# Обнуление бонусных дней полсе обновления подписки
async def reset_referral_bonuses(user_id: int):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.tg_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.bonus_days_balance = 0
            await session.commit()


async def get_latest_plan_name(tg_id: int) -> str | None:
    async with async_session_maker() as session:
        query = await session.execute(
            select(PaidSubscription.plan_name)
            .where(PaidSubscription.tg_id == tg_id, PaidSubscription.active == True)
            .order_by(PaidSubscription.id.desc())
            .limit(1)
        )
        result = query.scalar_one_or_none()
        return result
    
async def get_latest_special_plan_name(tg_id: int) -> str | None:
    async with async_session_maker() as session:
        query = await session.execute(
            select(SpecialSubscription.plan_name)
            .where(SpecialSubscription.tg_id == tg_id, SpecialSubscription.active == True)
            .order_by(SpecialSubscription.id.desc())
            .limit(1)
        )
        return query.scalar_one_or_none()
    
async def get_all_users():
    async with async_session_maker() as session:
        result = await session.execute(select(User.tg_id))
        return [row[0] for row in result.all()]
    
# Удаление записи о платной подписке из базы
async def remove_paid_subscription_by_uuid(uuid: str):
    async with async_session_maker() as session:
        result = await session.execute(
            delete(PaidSubscription).where(PaidSubscription.uuid == uuid)
        )
        await session.commit()

        return result.rowcount > 0 
    
# Удаление записи о специальной подписке из базы
async def remove_special_subscription_by_uuid(uuid: str):
    async with async_session_maker() as session:
        result = await session.execute(
            delete(SpecialSubscription).where(SpecialSubscription.uuid == uuid)
        )
        await session.commit()

        return result.rowcount > 0
    

# Создание промокода-скидки
async def create_discount_promo(promo_code: str, percent: int, max_uses: int):
    async with async_session_maker() as session:
        promo = PromoDiscount(
            promo_code=promo_code,
            discount_percent=percent,
            max_uses=max_uses,
        )
        session.add(promo)
        await session.commit()

# Создание промокода-бонусных дней
async def create_bonus_promo(promo_code: str, bonus_days: int, max_uses: int):
    async with async_session_maker() as session:
        promo = PromoBonusDays(
            promo_code=promo_code,
            bonus_days=bonus_days,
            max_uses=max_uses,
        )
        session.add(promo)
        await session.commit()

async def get_discount_promo(promo_code: str):
    promo_code = promo_code.upper().strip()
    async with async_session_maker() as session:
        result = await session.execute(
            select(PromoDiscount).where(PromoDiscount.promo_code == promo_code)
        )
        promo = result.scalar_one_or_none()

        if not promo or promo.active_uses >= promo.max_uses:
            return None

        return promo



async def use_discount_promo(promo, user_id):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.tg_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        # ✅ Сохраняем активную скидку в профиле
        user.active_discount_code = promo.promo_code
        user.active_discount_value = promo.discount_percent

        promo.active_uses += 1

        session.add(user)
        session.add(promo)

        await session.commit()
        return True


async def get_bonus_promo(promo_code: str):
    promo_code = promo_code.upper().strip()
    async with async_session_maker() as session:
        result = await session.execute(
            select(PromoBonusDays).where(PromoBonusDays.promo_code == promo_code)
        )
        promo = result.scalar_one_or_none()

        if not promo or promo.active_uses >= promo.max_uses:
            return None

        return promo


async def use_bonus_promo(promo, user_id):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.tg_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        # ✅ Добавляем бонусные дни на баланс пользователя
        user.bonus_days_balance += promo.bonus_days

        promo.active_uses += 1

        session.add(user)
        session.add(promo)

        await session.commit()
        return True

async def promo_exists(promo_code: str) -> bool:
    async with async_session_maker() as session:
        # Проверяем таблицу скидок
        q1 = await session.execute(
            select(PromoDiscount).where(PromoDiscount.promo_code == promo_code)
        )
        if q1.scalar_one_or_none():
            return True

        # Проверяем таблицу бонусных дней
        q2 = await session.execute(
            select(PromoBonusDays).where(PromoBonusDays.promo_code == promo_code)
        )
        if q2.scalar_one_or_none():
            return True
    
        return False
    

async def save_promo_use(tg_user_id: int, promo_id: int):
    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == tg_user_id)
        )

        record = PromoUse(user_id=user.id, promo_id=promo_id)
        session.add(record)
        await session.commit()

async def user_used_promo(tg_user_id: int, promo_id: int) -> bool:
    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == tg_user_id)
        )
        if not user:
            return False

        result = await session.scalar(
            select(PromoUse).where(
                PromoUse.user_id == user.id,
                PromoUse.promo_id == promo_id
            )
        )
        return result is not None
    
# Получение информации об активной скидке    
async def get_active_discount(tg_id: int):
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user and user.active_discount_value:
            return user.active_discount_value
        return None

# Удаляет активную скидку у пользователя после оплаты.
async def reset_user_discount(tg_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.active_discount_code = None
        user.active_discount_value = None
        await session.commit()
        return True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Проверка подписки
async def is_user_subscribed(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ("left", "kicked")
    except Exception:
        return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

async def get_trial_subscription(tg_id: int):
    """Возвращает запись TrialSubscription по Telegram ID пользователя."""
    async with async_session_maker() as session:
        stmt = (
            select(TrialSubscription)
            .join(User)
            .where(User.tg_id == tg_id)
        )
        return await session.scalar(stmt)


async def mark_trial_reminder_sent(tg_id: int):
    """Отмечает, что уведомление о Trial уже было отправлено."""
    async with async_session_maker() as session:
        stmt = (
            select(TrialSubscription)
            .join(User)
            .where(User.tg_id == tg_id)
        )
        trial = await session.scalar(stmt)
        if trial:
            trial.trial_reminder_sent = True
            await session.commit()

# Получение RP пользователя
async def get_rp_balance(tg_id: int) -> int:
    async with async_session_maker() as session:
        result = await session.execute(select(User.bonus_days_balance).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        return user or 0

# Конвертация RP в дни или ГБ с проверкой лимитов
async def convert_rp(tg_id: int, rp_amount: int, target: str) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        # Проверяем, что RP достаточно
        if user.bonus_days_balance < rp_amount:
            return False

        if target == "days":
            # Проверка лимита копилки дней
            if user.rp_days_balance + rp_amount > user.rp_days_limit:
                return False
            user.bonus_days_balance -= rp_amount
            user.rp_days_balance += rp_amount

        elif target == "gb":
            gb_amount = rp_amount * 1.5  # конвертация 1 RP = 1.5 GB
            # Проверка лимита копилки GB
            if user.rp_gb_balance + gb_amount > user.rp_gb_limit:
                return False
            user.bonus_days_balance -= rp_amount
            user.rp_gb_balance += gb_amount

        else:
            return False

        await session.commit()
        return True
    
# баланс конвертированных дней в БД
async def get_rp_days_balance(tg_id: int) -> int:
    async with async_session_maker() as session:
        result = await session.execute(select(User.rp_days_balance).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        return user or 0
    
# баланс конвертированных гигов в БД
async def get_rp_gb_balance(tg_id: int) -> int:
    async with async_session_maker() as session:
        result = await session.execute(select(User.rp_gb_balance).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        return user or 0

# Проверка активной платной подписки + наличия RP-дней
async def check_paid_subscription_and_days(tg_id: int):
    async with async_session_maker() as session:
        # Получаем пользователя и баланс дней
        user_res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = user_res.scalar_one_or_none()

        if not user or (user.rp_days_balance or 0) <= 0:
            return None

        # Ищем последнюю активную ПЛАТНУЮ подписку
        sub_res = await session.execute(
            select(PaidSubscription.uuid, PaidSubscription.expire_date)
            .where(PaidSubscription.tg_id == tg_id, PaidSubscription.active == True)
            .order_by(PaidSubscription.id.desc())
            .limit(1)
        )
        sub = sub_res.first()
        if not sub:
            return None

        uuid, expire_date = sub

        return {
            "uuid": uuid,
            "expire_date": expire_date,
            "balance": user.rp_days_balance
        }

# Проверка баланса + действующей подписки Обход Whitelists
async def check_special_subscription_and_gb(tg_id: int):
    async with async_session_maker() as session:
        # Пользователь
        user_res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = user_res.scalar_one_or_none()

        if not user or (user.rp_gb_balance or 0) <= 0:
            return None

        # Активная спец-подписка
        sub_res = await session.execute(
            select(SpecialSubscription.uuid)
            .where(SpecialSubscription.tg_id == tg_id, SpecialSubscription.active == True)
            .order_by(SpecialSubscription.id.desc())
            .limit(1)
        )
        sub = sub_res.first()
        if not sub:
            return None

        uuid = sub[0]

        return {
            "uuid": uuid,
            "balance": user.rp_gb_balance
        }

async def update_special_subscription_after_gb_apply(tg_id: int, used_gb: float):
    async with async_session_maker() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one_or_none()

        if not user:
            return False

        # Списываем использованные гигабайты
        user.rp_gb_balance -= used_gb
        if user.rp_gb_balance < 0:
            user.rp_gb_balance = 0

        await session.commit()
        return True
    
# Обнуление RP-дней после обновления подписки
async def update_paid_subscription_with_rp_days(tg_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.rp_days_balance = 0
        await session.commit()

        return True

# Удаление RP (списание с баланса)
async def remove_rp(tg_id: int, amount: int, reason: str = None):
    async with async_session_maker() as session:
        async with session.begin():
            user = await session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if not user:
                return False

            # Проверяем, что хватает RP
            if user.bonus_days_balance < amount:
                return False

            # Списываем
            user.bonus_days_balance -= amount

        await session.commit()

    return True

# Получить запись уведомлений пользователя
async def get_notification_row(tg_id: int):
    async with async_session_maker() as session:
        return await session.get(ExpiredSubscriptionNotification, tg_id)
    

# Создать запись, если её нет
async def get_or_create_notification_row(tg_id: int):
    async with async_session_maker() as session:
        row = await session.get(ExpiredSubscriptionNotification, tg_id)
        if row:
            return row

        row = ExpiredSubscriptionNotification(telegram_id=tg_id)
        session.add(row)
        await session.commit()
        return row
    

# Проверка: уведомляли ли по типу
async def was_notified(tg_id: int, sub_type: str) -> bool:
    row = await get_notification_row(tg_id)
    if not row:
        return False

    return {
        "trial": row.notified_trial,
        "paid": row.notified_paid,
        "special": row.notified_special
    }.get(sub_type, False)


# Пометить уведомление как отправленное
async def mark_notified(tg_id: int, sub_type: str):
    async with async_session_maker() as session:
        row = await session.get(ExpiredSubscriptionNotification, tg_id)
        if not row:
            row = ExpiredSubscriptionNotification(telegram_id=tg_id)
            session.add(row)

        if sub_type == "trial":
            row.notified_trial = True
        elif sub_type == "paid":
            row.notified_paid = True
        elif sub_type == "special":
            row.notified_special = True

        await session.commit()


# Сброс уведомлений (раз в 7 дней)
async def reset_expired_notifications():
    async with async_session_maker() as session:
        await session.execute(
            update(ExpiredSubscriptionNotification).values(
                notified_trial=False,
                notified_paid=False,
                notified_special=False
            )
        )

        meta = await session.get(NotificationMeta, 1)
        if meta:
            meta.last_reset_at = datetime.utcnow()
        else:
            session.add(NotificationMeta(
                id=1,
                last_reset_at=datetime.utcnow()
            ))

        await session.commit()


# Проверка — пора ли делать reset
async def should_reset_notifications():
    async with async_session_maker() as session:
        meta = await session.get(NotificationMeta, 1)
        if not meta:
            return True
        return datetime.utcnow() - meta.last_reset_at >= timedelta(days=7)
