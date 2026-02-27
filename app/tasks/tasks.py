from datetime import datetime, timedelta, timezone
from aiogram.types import FSInputFile
from sqlalchemy import select

from app.services import remnawave_api as rm
from app import helpers as hp
from app.db.dealer import async_session_maker
from app.db.models import Subscriptions
from app import keyboards as kb
from aiogram import Bot
from config import TOKEN


# =========================
# CLEANUP EXPIRED SUBSCRIPTIONS
# =========================

async def cleanup_expired_subscriptions():
    try:
        users = await rm.get_all_users()
        now = datetime.now(timezone.utc)

        async with async_session_maker() as session:
            for user in users:
                desc = (user.get("description") or "").lower()
                status = (user.get("status") or "").lower()
                expire_at = user.get("expireAt")
                uuid = user.get("uuid")

                if status != "expired":
                    continue

                if not expire_at or not uuid:
                    continue

                expire_time = datetime.fromisoformat(
                    expire_at.replace("Z", "+00:00")
                )

                if now <= expire_time + timedelta(hours=10):
                    continue

                if "paid" in desc:
                    sub_type = "base"
                elif "special" in desc:
                    sub_type = "bypass"
                elif "multi" in desc:
                    sub_type = "multi"
                else:
                    continue

                stmt = select(Subscriptions).where(
                    getattr(Subscriptions, f"{sub_type}_uuid") == uuid
                )
                result = await session.execute(stmt)
                subscription = result.scalar_one_or_none()

                if not subscription:
                    continue

                if has_other_active(subscription, sub_type):
                    reset_subscription_type(subscription, sub_type)
                    await session.commit()
                else:
                    await session.delete(subscription)
                    await session.commit()

                await rm.delete_user(uuid)

    except Exception as e:
        print(f"[CLEANUP ERROR] {e}")


def reset_subscription_type(subscription, sub_type: str):
    prefix = f"{sub_type}_"

    setattr(subscription, f"{prefix}plan_name", None)
    setattr(subscription, f"{prefix}amount", None)
    setattr(subscription, f"{prefix}start_date", None)
    setattr(subscription, f"{prefix}expire_date", None)
    setattr(subscription, f"{prefix}active", False)
    setattr(subscription, f"{prefix}uuid", None)
    setattr(subscription, f"{prefix}devices_extra", 0)


def has_other_active(subscription, current_type: str) -> bool:
    types = ["base", "bypass", "multi"]

    for t in types:
        if t == current_type:
            continue

        if getattr(subscription, f"{t}_active"):
            return True

    return False


# =========================
# CLEANUP EXPIRED TRIALS
# =========================

async def cleanup_expired_trials():
    try:
        users = await rm.get_all_users()
        now = datetime.now(timezone.utc)

        for user in users:
            desc = (user.get("description") or "").lower()
            status = (user.get("status") or "").lower()
            expire_at = user.get("expireAt")
            uuid = user.get("uuid")

            if "trial" not in desc or status != "expired" or not expire_at:
                continue

            expire_time = datetime.fromisoformat(
                expire_at.replace("Z", "+00:00")
            )

            if now > expire_time + timedelta(hours=2):
                await rm.delete_user(uuid)

    except Exception as e:
        print(f"[cleanup_expired_trials] Ошибка: {e}")


# =========================
# EXPIRED SUBSCRIPTION NOTIFIER
# =========================

async def expired_subscriptions_notifier1(bot: Bot):
    try:
        users = await rm.get_all_users()

        for u in users:
            if u.get("status") != "EXPIRED":
                continue

            tg_id = u.get("telegramId")
            if not tg_id:
                continue

            desc = (u.get("description") or "").lower()

            if desc.startswith("trial"):
                sub_type = "trial"
            elif desc.startswith("paid"):
                sub_type = "paid"
            elif desc.startswith("special"):
                sub_type = "special"
            else:
                continue

            if await hp.was_notified(tg_id, sub_type):
                continue

            if sub_type == "trial":
                text = (
                    "⏳ <b>Ваш пробный доступ закончился!</b>\n\n"
                    "Надеюсь, протестировав наш VPN 🚀, вы смогли увидеть его преимущества.\n\n"
                    "🔐 <i>Но ничего не машает вам продлить доступ, оформив платную подписку</i> 👇"
                )
                key = kb.expired_trial_kb
            elif sub_type == "paid":
                text = (
                    "🛑 <b>Ваша подписка 'Базовый VPN 🪴' истекла!</b>\n\n"
                    "<b>Доступ к VPN временно приостановлен.</b>\n\n"
                    "<i>🌐 Продлите подписку, чтобы снова пользоваться VPN без ограничений</i> 👇"
                )
                key = kb.expired_paid_kb
            else:
                text = (
                    "🛑 <b>Ваша подписка 'Обход Whitelists 🥷' истекла!</b>\n\n"
                    "<b>Доступ к серверам был временно приостановлен.</b>\n\n"
                    "<i>⚠️ Продлите подписку, чтобы восстановить доступ</i> 👇"
                )
                key = kb.expired_special_kb

            await bot.send_photo(
                chat_id=tg_id,
                photo=FSInputFile("./assets/failure_knight.jpg"),
                caption=text,
                parse_mode="HTML",
                reply_markup=key
            )

            await hp.mark_notified(tg_id, sub_type)

        if await hp.should_reset_notifications():
            await hp.reset_expired_notifications()

    except Exception as e:
        print("[EXPIRED NOTIFIER ERROR]", e)


# =========================
# TRIAL REMINDER TASK
# =========================

async def trial_reminder_task(bot: Bot):
    try:
        users = await rm.get_all_users()
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=1)

        for u in users:
            if u.get("description") != "Trial":
                continue
            if u.get("firstConnectedAt") is not None:
                continue
            if not u.get("telegramId") or not u.get("createdAt"):
                continue

            created_at = datetime.fromisoformat(
                u["createdAt"].replace("Z", "+00:00")
            )

            if created_at > day_ago:
                continue

            trial = await hp.get_trial_subscription(u["telegramId"])
            if not trial or trial.trial_reminder_sent:
                continue

            try:
                await bot.send_photo(
                    chat_id=u["telegramId"],
                    photo=FSInputFile("./assets/help_knight.jpg"),
                    caption=(
                        "⚠️ <b>Вы ещё не активировали свою пробную подписку!</b>\n\n"
                        "Если возникли трудности — откройте инструкцию и следуйте шагам "
                        "или напишите в поддержку 💬"
                    ),
                    parse_mode="HTML",
                    reply_markup=kb.help,
                )
                await hp.mark_trial_reminder_sent(u["telegramId"])

            except Exception as e:
                print(f"[Ошибка отправки {u.get('telegramId')}] {e}")

    except Exception as e:
        print(f"[trial_reminder_task] Ошибка выполнения задачи: {e}")