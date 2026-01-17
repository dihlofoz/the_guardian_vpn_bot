from aiogram import F, Router
from aiogram import Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputMediaAnimation
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import types
from datetime import datetime, timedelta
import requests
import time 
import random, string
import asyncio
import math

# Внутрянка
import app.keyboards as kb
import app.helpers as hp
from app.services import cryptobot_api as cb
from app.services import yookassa_api as yoo
from app.services import remnawave_api as rm
from config import BOT_USERNAME, TARIFFS, ADMIN_IDS, DEFAULT_DEVICES, DEVICES_MAX, DEVICES_MIN, DEVICES_STEP
from app.states import CreatePromo, PromoActivate, ConvertRPStates
from app.tasks import pay_notify as pn

return_url = 'https://t.me/GrdVPNbot'
router = Router()

ACTIVE_INVOICES = {}
TEMP_MAILING = {}
user_device_choice = {}

SPECIAL_TARIFFS = {
    "7 дней (25 GB)",
    "14 дней (50 GB)",
    "30 дней (100 GB)"
}

# Начало работы бота
@router.message(CommandStart())
async def start(message: Message):
    # Разбираем /start <ref_code>
    parts = message.text.split(maxsplit=1)
    ref_code = parts[1].strip() if len(parts) > 1 else None

    tg_id = message.from_user.id
    user_exists = await hp.user_exists(tg_id)

    if not user_exists:
        # Передаём referred_by в add_user — она сама начислит реф-бонус, если код валиден
        await hp.add_user(
            tg_id,
            message.from_user.username,
            message.from_user.full_name,
            referred_by=ref_code
        )

    photo_path = "./assets/start_knight.jpg"
    photo = FSInputFile(photo_path)

    await message.answer_photo(
        photo=photo,
        caption=(
            "👋 <b>Добро пожаловать в The Guardian VPN🔐 - ваш главный интернет-защитник!</b>\n\n"
            "<b>Это место, где твоя безопасность и свобода в сети становятся реальностью.</b>\n\n"
            "<i>Нажми кнопку ниже, чтобы начать</i>👇"
        ),
        parse_mode="HTML",
        reply_markup=kb.continue_btn_new if not user_exists else kb.continue_btn_existing
    )

# Кнопка "Продолжить" после /start
@router.callback_query(F.data == 'continue_new')
async def continue_new(callback: CallbackQuery):

    photo_path = "./assets/news_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "📢 <b>Прежде чем пользоваться ботом, пожалуйста подпишитесь на канал.</b>\n\n"
                "🛡️ Там публикуются новости, обновления, промокоды и важные уведомления\n\n"
                "<i>После подписки нажми кнопку '✅ Проверить подписку' </i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.subscribe_check
    )
    await callback.answer()


# Кнопка "Проверить подписку"
@router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: CallbackQuery):
    tg_id = callback.from_user.id

    if not await hp.is_user_subscribed(callback.bot, tg_id):
        await callback.answer("❌ Вы ещё не подписались на канал")
        return

    # Если подписан — показываем пользовательское соглашение
    await show_info(callback)

# Пользовательское соглашение
async def show_info(callback: CallbackQuery):
    await callback.answer()

    photo_path = "./assets/policy_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
            "🛡️ <b>Отлично!</b>\n"
            "Добро пожаловать в <b>The Guardian VPN🔐</b> — твой личный защитник в цифровом мире.\n\n"
            "🔒 <b>Безопасность превыше всего</b>\n"
            "Шифруем весь трафик, защищаем данные и не храним логи. Твоя приватность — под нашей защитой.\n\n"
            "⚙️ <b>Сделано вручную</b>\n"
            "Проект создан одним разработчиком с акцентом на стабильность, простоту и честность.\n\n"
            "🌍 <b>Надёжные узлы</b>\n"
            "Подключайся через проверенные сервера:\n🇺🇸 | 🇩🇪 | 🇳🇱 | 🇫🇮 | 🇷🇺 | 🇫🇷 | 🇵🇱 | 🇸🇪\n\n"
            "🚀 <b>Быстро и просто</b>\n"
            "Подключение в один клик. Никаких сложных настроек — просто защита.\n\n"
            "❤️ <b>Миссия</b>\n"
            "Дарить каждому свободу и спокойствие в сети, без компромиссов по безопасности.\n\n"
            "📘 Нажимая кнопку <b>✅ Соглашаюсь</b>, вы принимаете "
            "<a href='https://telegra.ph/Pravila-ispolzovaniya-10-18'>условия использования</a> "
            "и <a href='https://telegra.ph/Politika-konfidencialnosti-10-18-58'>политику конфиденциальности</a>."
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        ),
        reply_markup=kb.agree_btn
    )

# Вывод главного меню после согласия с политикой конфиденциальности и условиями пользования
@router.callback_query(F.data == 'agree')
async def help(callback: CallbackQuery):
    await callback.answer('')

    photo_path = "./assets/agree_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "✅ <b>Отлично, добро пожаловать в главное меню!</b>\n\n"
                "<i>Выбери интересующий тебя вариант</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.main
    )

# Вывод главное меню для старого пользователя
@router.callback_query(F.data == "continue_existing")
async def existing_user_menu(callback: CallbackQuery):
    await callback.answer()

    photo_path = "./assets/agree_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "🔓 <b>Добро пожаловать обратно!</b>\n\n"
                "<i>Выбери интересующий тебя вариант</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.main
    )

# Информация
@router.callback_query(F.data == 'info')
async def help(callback: CallbackQuery):
    await callback.answer('Информация')

    photo_path = "./assets/info_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "<b>Мы — твой цифровой щит</b>🛡️\n\n"
                "<blockquote><b>The Guardian VPN</b>🔐 — это безопасный доступ в интернет без ограничений.\n\n"
                "Мы шифруем твой трафик, скрываем IP и защищаем личные данные.\n"
                "Быстро. Надёжно. Без логов.</blockquote>\n\n"
                "<i>Подключайся и будь невидимым</i> 🥷"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.infokey
    )

# Реферальная система
@router.callback_query(F.data == 'referral')
async def connectvpn(callback: CallbackQuery):
    await callback.answer('Реферальная программа')

    tg_id = callback.from_user.id

    # 🔹 Получаем реферальный код и бонусные дни асинхронно
    ref_code = await hp.get_ref_code(tg_id)
    bonus_days_balance = await hp.get_rp_balance(tg_id)

    # Баланс конвертированных ДНЕЙ и ГИГАБАЙТОВ (ты сам создал эти поля)
    days_balance = await hp.get_rp_days_balance(tg_id)
    gb_balance = await hp.get_rp_gb_balance(tg_id)

    # 🔹 Считаем количество приглашённых
    invited_count = await hp.get_invited_count(tg_id)

    # Формируем реферальную ссылку
    ref_link = f"https://t.me/{BOT_USERNAME}?start={ref_code}"

    photo_path = "./assets/referral_knight.jpg"
    photo = FSInputFile(photo_path)

    caption = (
        "<blockquote>🎁 <b>Бонусная программа</b></blockquote>\n\n"
        "Приглашая друзей, вы получаете <b>2 RP</b> за каждого приглашённого!\n\n"
        "<b>❗️ Чтобы получить бонус, приглашённый должен зарегистрироваться.</b>\n\n"
        "<blockquote>💠<b> RP</b> - <i>это токены, являющиеся почти полноценной внутренней валютой этого сервиса.\n<b>Покупайте</b> или <b>продлевайте</b> свою подписку просто приглашая знакомых!\n\n"
        "Здесь вы также можете конвертировать ваши <b>RP</b>\nв 📅дни / 📦гигабайты, которые можно будет добавить к действующей платной подписке!</i></blockquote>\n\n"
        "<b>Курс: 1 RP = 1 день = 1.5 ГБ = 8₽</b>\n\n"
        f"<blockquote>📊 <b>Ваша статистика:</b>\n"
        f"✍🏿 <b>Всего приглашено:    {invited_count}</b>\n"
        f"💠 <b>Баланс RP:    {bonus_days_balance}</b>\n\n"
        f"📅 <b>Баланс дней:    {days_balance}</b>\n"
        f"📦 <b>Баланс гигабайтов:    {gb_balance}</b>\n\n"
        f"🔗 <b>Ваша реферальная ссылка:</b>\n"
        f"<code>{ref_link}</code></blockquote>\n\n"
        "<i>Отправляйте ссылку друзьям и получайте RP!</i> 🫂"
    )

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=kb.ref 
    )

# Добавление бонусных дней к платной подписке
@router.callback_query(F.data == 'updatesub')
async def update_sub(callback: CallbackQuery):
    await callback.answer('Модернизация подписки')

    photo_path = "./assets/modern_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
        caption=(
            f"⚙️ <b>Модернизация подписки</b>\n\n"
            f"<blockquote>В былые времена рыцари укрепляли свои <b>доспехи</b> 🦾, чтобы уверенно идти в новые походы.\n\n"
            f"Сегодня же ты можешь модернизировать свой <b>цифровой щит</b> 🛡\n\n Увеличивай кол-во <b>дней</b> ⏳ или доступных <b>ГБ</b> 🌐 и пользуйся VPN-подпиской дольше!</blockquote>\n\n"
            f"<i> Выберите тип своей подписки ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
    reply_markup=kb.updatesub
    )

# Кнопка подключения к VPN
@router.callback_query(F.data == 'connectvpn')
async def connectvpn(callback: CallbackQuery):
    await callback.answer('Подключение к VPN')

    photo_path = "./assets/vpn_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
        caption=(
            f"🏰 <b> Добро пожаловать в Чертоги Стабильного Соединения</b>\n\n"
            f"✠ Здесь рыцари шёпотом обмениваются тайными путями, недоступные чужим глазам...\n\n"
            f"<i>Выберите нужное действие ниже</i> 👇"
        ),
        parse_mode="HTML"
        ),
    reply_markup=kb.vpn
    )

# Кнопка помощь
@router.callback_query(F.data == 'help')
async def help(callback: CallbackQuery):
    await callback.answer('Помощь💬')

    photo_path = "./assets/help_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "🤝 <b>Привет! Необходима помощь?</b>\n\n"
                "🛠️ Здесь можно найти инструкцию по настройке VPN, смотри ниже.\n\n"
                "🛟 <i>Если возникла проблема или вопрос, то напиши в поддержку, поможем разобраться!</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.help
    )

# Кнопка профиля
@router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    await callback.answer('Ваш профиль👤')

    tg_id = callback.from_user.id
    full_name = callback.from_user.full_name
    username = callback.from_user.username or "—"

    user_data = await rm.get_user_by_telegram_id(tg_id)

    caption = (
        f"<blockquote>🛡️ <b>Профиль пользователя</b></blockquote>\n\n"
        f"👤 <b>Имя:</b> {full_name}\n"
        f"🆔 <b>Username:</b> @{username}\n\n"
    )

    # --- Извлекаем подписки из панели ---
    raw_users = user_data.get("users") if user_data else None
    user_list = [u for u in raw_users if u.get("telegramId") == tg_id] if raw_users else []

    # Если нет НИ ОДНОЙ подписки
    if not user_list:
        caption += (
            "<blockquote>🚫 <b>Активных подписок не найдено.</b>\n"
            "<b>Получите пробный ключ или оформите подписку</b>💎</blockquote>"
        )
    else:
        # Утилиты
        from datetime import datetime
        fmt = lambda d: datetime.fromisoformat(d.replace("Z", "+00:00")).strftime("%d.%m.%Y") if d else "—"
        to_gb = lambda b: round(b / 1024**3, 2)

        # --- Разделяем по типам подписок ---
        paid_trial = []
        special = []

        for u in user_list:
            desc = u.get("description", "")
            prefix = desc.split()[0] if desc else ""

            if prefix in ("Paid", "Trial"):
                paid_trial.append(u)
            elif prefix == "Special":
                special.append(u)

        # --- Функция выбора самой новой подписки ---
        def pick_latest(subs):
            if not subs:
                return None
            return max(subs, key=lambda s: s.get("expireAt") or "")

        paid_trial_sub = pick_latest(paid_trial)
        special_sub = pick_latest(special)

        # --- Получаем названия тарифов ---
        paid_trial_plan_name = await hp.get_latest_plan_name(tg_id)
        special_plan_name = await hp.get_latest_special_plan_name(tg_id)

        # =====================================================================
        #                         БЛОК PAID / TRIAL
        # =====================================================================
        caption += "<blockquote>✍️ <b>Платная / Пробная подписка:</b>\n\n"

        if not paid_trial_sub:
            caption += "🚫 <b>Активных подписок не найдено.</b>\n</blockquote>\n"
        else:
            u = paid_trial_sub

            start_str = fmt(u.get("createdAt"))
            end_str = fmt(u.get("expireAt"))
            used_bytes = u.get("userTraffic", {}).get("usedTrafficBytes", 0)
            used_gb = to_gb(used_bytes)
            limit_bytes = u.get("trafficLimitBytes", 0)
            traffic_str = f"{used_gb} / {to_gb(limit_bytes)} ГБ" if limit_bytes else f"{used_gb} / ∞"

            status_raw = u.get("status", "—").upper()
            if status_raw == "ACTIVE":
                status = "🟢 Active"
            elif status_raw == "EXPIRED":
                status = "🔴 Expired"
            else:
                status = "⚪️ —"

            sub_link = u.get("subscriptionUrl") or "—"
            plan_name = paid_trial_plan_name or u.get("description", "—")

            caption += (
                f"💎 <b>Тариф:</b> {plan_name}\n\n"
                f"📌 <b>Статус:</b> {status}\n"
                f"🕒 <b>Начало:</b> {start_str}\n"
                f"⏳ <b>Окончание:</b> {end_str}\n"
                f"📦 <b>Трафик:</b> {traffic_str}\n\n"
                f"🔗 <b>Подписка:</b> {sub_link}\n"
                "</blockquote>\n"
            )

        # =====================================================================
        #                         БЛОК SPECIAL
        # =====================================================================
        caption += "<blockquote>✍️ <b>Обход Whitelists подписка:</b>\n\n"

        if not special_sub:
            caption += "🚫 <b>Активных подписок не найдено.</b>\n</blockquote>"
        else:
            u = special_sub

            start_str = fmt(u.get("createdAt"))
            end_str = fmt(u.get("expireAt"))
            used_bytes = u.get("userTraffic", {}).get("usedTrafficBytes", 0)
            used_gb = to_gb(used_bytes)
            limit_bytes = u.get("trafficLimitBytes", 0)
            traffic_str = f"{used_gb} / {to_gb(limit_bytes)} ГБ" if limit_bytes else f"{used_gb} / ∞"

            status_raw = u.get("status", "—").upper()
            if status_raw == "ACTIVE":
                status = "🟢 Active"
            elif status_raw == "EXPIRED":
                status = "🔴 Expired"
            else:
                status = "⚪️ —"

            sub_link = u.get("subscriptionUrl") or "—"
            plan_name = special_plan_name or "Special"

            caption += (
                f"💎 <b>Тариф:</b> {plan_name}\n\n"
                f"📌 <b>Статус:</b> {status}\n"
                f"🕒 <b>Начало:</b> {start_str}\n"
                f"⏳ <b>Окончание:</b> {end_str}\n"
                f"📦 <b>Трафик:</b> {traffic_str}\n\n"
                f"🔗 <b>Подписка:</b> {sub_link}\n"
                "</blockquote>"
            )

    photo = FSInputFile("./assets/profile_knight.jpg")
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
        reply_markup=kb.profile_logic
    )



# Получение пробной подписки
@router.callback_query(F.data == 'key')
async def try_key(callback: CallbackQuery):
    tg_id = callback.from_user.id

    # Проверяем, активировал ли пользователь пробный период ранее
    if await hp.has_trial(tg_id):
        await callback.answer("⚠️ Вы уже активировали пробную подписку.")

        # Отправляем в главное меню
        photo_path = "./assets/continue_knight.jpg"
        photo = FSInputFile(photo_path)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=photo,
                caption=(
                    "🏠 <b>Вы уже использовали пробный тариф.</b>\n"
                    "⚠️ <b>Для продления доступа оформите платную подписку.</b>\n\n"
                    "👀 <i>Если ваша пробная подписка ещё работает, то информация о ней находится в Профиле</i>👤"
                ),
                parse_mode="HTML"
            ),
            reply_markup=kb.main
        )
        return
    
    sub_type = await hp.get_active_subscription_type(tg_id)
    if sub_type == "paid":
        await callback.answer("⚠️boobs⚠️")

        # Отправляем в главное меню
        photo_path = "./assets/continue_knight.jpg"
        photo = FSInputFile(photo_path)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=photo,
                caption=(
                    f"⚠️ <b>У вас уже есть активная платная подписка.</b>\n"
                    f"🏡 <b>Вы вернулись в главное меню</b>\n\n"
                    f"<i>Выбери интересующий тебя вариант</i> 👇"
                ),
                parse_mode="HTML"
            ),
            reply_markup=kb.main
        )
        return
    
    await callback.answer("Пробный период активирован ✅")

    photo_path = "./assets/success_knight.jpg"
    photo = FSInputFile(photo_path)

    try:
        # Создаём пользователя через Remnawave API
        user_data = await rm.create_trial_user(callback.from_user.id)

        # Активируем пробный период в базе (запоминаем, что пользователь его уже использовал)
        await hp.activate_trial(tg_id)

        # Получаем текущую дату и время
        start_date = datetime.now()
        end_date = start_date + timedelta(days=2)  # 2 дня пробного периода

        start_str = start_date.strftime("%d.%m.%Y %H:%M")
        end_str = end_date.strftime("%d.%m.%Y %H:%M")

        # Ссылка на подписку
        sub_link = f"https://sub.grdguard.xyz/{user_data.get('shortUuid')}"

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=photo,
                caption=(
                    f"🏷️ <b>Пробный период активирован!</b>\n\n"
                    f"<blockquote>🕒 <b>Начало:</b> {start_str}\n"
                    f"⏳ <b>Окончание:</b> {end_str}\n"
                    f"📦 <b>Трафик:</b> 30 ГБ\n\n"
                    f"🔗 <b>Подписка:</b> {sub_link}</blockquote>\n\n"
                    f"📖 <i>Инструкции по подключению — в разделе “Помощь💬”</i>"
                ),
                parse_mode="HTML"
            ),
            reply_markup=kb.back_to_start
        )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при активации пробного периода: {e}")

    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при создании подписки:\n<code>{e}</code>",
            parse_mode="HTML"
        )


# Возвращение в главное меню
@router.callback_query(F.data == 'back_main2')
async def back_main(callback: CallbackQuery):
    await callback.answer('')

    tg_id = callback.from_user.id
    ACTIVE_INVOICES.pop(tg_id, None)

    firstname = callback.from_user.first_name or ""
    lastname = callback.from_user.last_name or ""

    photo_path = "./assets/continue_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"🛡 <b>Вы вернулись в начало!</b>\n\n"
                f"Надеюсь вам тут нравится <b>{firstname} {lastname}</b>, я старался 👀\n\n"
                f"<i>Продолжим? Выбери интересующий тебя вариант 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.main
    )

@router.callback_query(F.data == 'back_main5')
async def connectvpn(callback: CallbackQuery):
    await callback.answer('Назад')

    tg_id = callback.from_user.id

    # 🔹 Получаем реферальный код и бонусные дни асинхронно
    ref_code = await hp.get_ref_code(tg_id)
    bonus_days_balance = await hp.get_rp_balance(tg_id)

    # Баланс конвертированных ДНЕЙ и ГИГАБАЙТОВ (ты сам создал эти поля)
    days_balance = await hp.get_rp_days_balance(tg_id)
    gb_balance = await hp.get_rp_gb_balance(tg_id)

    # 🔹 Считаем количество приглашённых
    invited_count = await hp.get_invited_count(tg_id)

    # Формируем реферальную ссылку
    ref_link = f"https://t.me/{BOT_USERNAME}?start={ref_code}"

    photo_path = "./assets/referral_knight.jpg"
    photo = FSInputFile(photo_path)

    caption = (
        "<blockquote>🎁 <b>Бонусная программа</b></blockquote>\n\n"
        "Приглашая друзей, вы получаете <b>2 RP</b> за каждого приглашённого!\n\n"
        "<b>❗️ Чтобы получить бонус, приглашённый должен зарегистрироваться.</b>\n\n"
        "<blockquote>💠<b> RP</b> - <i>это токены, являющиеся почти полноценной внутренней валютой этого сервиса.\n<b>Покупайте</b> или <b>продлевайте</b> свою подписку просто приглашая знакомых!\n\n"
        "Здесь вы также можете конвертировать ваши <b>RP</b>\nв 📅дни / 📦гигабайты, которые можно будет добавить к действующей платной подписке!</i></blockquote>\n\n"
        "<b>Курс: 1 RP = 1 день = 1.5 ГБ = 8₽</b>\n\n"
        f"<blockquote>📊 <b>Ваша статистика:</b>\n"
        f"✍🏿 <b>Всего приглашено:    {invited_count}</b>\n"
        f"💠 <b>Баланс RP:    {bonus_days_balance}</b>\n\n"
        f"📅 <b>Баланс дней:    {days_balance}</b>\n"
        f"📦 <b>Баланс гигабайтов:    {gb_balance}</b>\n\n"
        f"🔗 <b>Ваша реферальная ссылка:</b>\n"
        f"<code>{ref_link}</code></blockquote>\n\n"
        "<i>Отправляйте ссылку друзьям и получайте RP!</i> 🫂"
    )

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=kb.ref 
    )

# Возвращение в главное меню
@router.callback_query(F.data == 'back_main')
async def back_main(callback: CallbackQuery):
    await callback.answer('')

    photo_path = "./assets/continue_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "🛡️ <b>С возвращение, герой! Вот ты и снова в начале.</b>\n\n"
                "⚔️ Получай доступ и захватывай новые вершины!\n\n"
                "<i>Выбери интересующий тебя вариант 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.main
    )

# Возвращение к впн меню
@router.callback_query(F.data == 'back_main1')
async def back_main(callback: CallbackQuery):
    await callback.answer('Назад')

    photo_path = "./assets/vpn_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"🏰 <b> Добро пожаловать в Чертоги Стабильного Соединения</b>\n\n"
                f"✠ Здесь рыцари шёпотом обмениваются тайными путями, недоступные чужим глазам...\n\n"
                f"<i>Выберите нужное действие ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.vpn
    )

# Переход к тарифам
@router.callback_query(F.data == 'back_main3')
async def back_main(callback: CallbackQuery):
    await callback.answer('Назад')

    tg_id = callback.from_user.id
    ACTIVE_INVOICES.pop(tg_id, None)

    photo_path = "./assets/option_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"<b>Выбор тарифа решает твою VPN-эпопею</b> 🌐\n\n" 
                f"<i>Остаётся лишь выбрать подходящий</i> 🤔" 
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )

@router.callback_query(F.data == 'back_main4')
async def back_main(callback: CallbackQuery):
    await callback.answer('Назад')
    await callback.message.delete()

@router.callback_query(F.data == 'tarif')
async def back_main(callback: CallbackQuery):
    await callback.answer('💳 Купить тариф')

    photo_path = "./assets/option_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"<b>Выбор тарифа решает твою VPN-эпопею</b> 🌐\n\n" 
                f"<i>Остаётся лишь выбрать подходящий</i> 🤔" 
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )

@router.callback_query(F.data == 'prodlenie')
async def back_main(callback: CallbackQuery):
    await callback.answer('💳 Продление')

    photo_path = "./assets/option_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"<b>Продление подписки помогает решить твою VPN-эпопею</b> 🌐\n\n" 
                f"<i>Осталось немного путник, продолжай свой путь</i> 🫡" 
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )

@router.callback_query(F.data == 'tariffs_basic')
async def tarif(callback: CallbackQuery):
    await callback.answer('Базовый 🪴')

    user_id = callback.from_user.id

    ACTIVE_INVOICES[user_id] = {
        "tariff_group": "basic"
    }

    photo_path = "./assets/basic_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "🛡 <b>Раздел расширенных возможностей и усиленной безопасности</b>\n\n"
                "<blockquote><i>В данные тарифы не входят серверы, предназначенные для обхода белых списков 🚫\n\n"
                "Они рассчитаны на более простые задачи и также подойдут пользователям из регионов, где ещё отсутствуют полноценные блокировки</i>\n\n"
                "🌍 <b>Сервера</b>: 🇺🇸 | 🇩🇪 | 🇳🇱 | 🇫🇮 | 🇷🇺 | 🇫🇷 | 🇵🇱 | 🇸🇪</blockquote>\n\n"
                "🛣 <i>Ваш путь начинается здесь, просто двигайтесь вперёд...</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tariffs_b
    )

@router.callback_query(F.data == 'tariffs_special')
async def tarif(callback: CallbackQuery):
    await callback.answer('Обход 🥷')

    user_id = callback.from_user.id

    ACTIVE_INVOICES[user_id] = {
        "tariff_group": "special"
    }

    photo_path = "./assets/obhod_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "🥷 <b>Раздел специальных тарифов</b>\n\n"
                "<blockquote><i>Режимы с расширенными возможностями обхода блокировок и улучшенной стабильностью подключения</i> 📶\n\n"
                "🌍 <b>Сервера</b>:  🇷🇺 | 🇳🇱 | 🇫🇮 | 🇩🇪 | 🇫🇷 | 🇵🇱 | 🇸🇪</blockquote>\n\n"
                "<i>Выбери тариф — и получи более свободный доступ к нужным ресурсам 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tariffs_s
    )

@router.callback_query(F.data == 'tariffs_multi')
async def tarif(callback: CallbackQuery):
    await callback.answer('Мульти VPN 💥')

    user_id = callback.from_user.id

    ACTIVE_INVOICES[user_id] = {
        "tariff_group": "multi"
    }

    photo_path = "./assets/obhod_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "💥 <b>Раздел мульти-доступа</b>\n\n"
                "<blockquote><i>Это место, где вы можете получить доступ ко всем серверам сервиса в одной подписке</i> 🛜\n\n"
                "🌍 <b>Сервера</b>: 🇺🇸 | 🇷🇺 | 🇳🇱 | 🇫🇮 | 🇩🇪 | 🇫🇷 | 🇵🇱 | 🇸🇪</blockquote>\n\n"
                "<i>Выбери тариф — и начни свой путь 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tariffs_m
    )

# Активация пробной подписки
@router.callback_query(F.data == 'trysub')
async def connectvpn(callback: CallbackQuery):
    await callback.answer('Пробный период')

    photo_path = "./assets/try_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "🏆 <b>Тариф: Пробный</b>\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Попробуй и реши, на чьей стороне ты!\n"
              "│ 🗓  <b>Кол-во Дней:</b> 2\n"
              "│ 🌐 <b>Трафик:</b> 30 GB\n"
              "│ 💶 <b>Стоимость:</b> 0₽\n"
              "─────────────────────────────────</blockquote>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.sub
    )
    
# Выбор тарифа → сразу открываем выбор устройств
@router.callback_query(F.data.in_(TARIFFS.keys()))
async def handle_tariff_choice(callback: CallbackQuery):
    tariff_code = callback.data
    user_id = callback.from_user.id

    tariff_group = ACTIVE_INVOICES.get(user_id, {}).get("tariff_group")

    # Сохраняем выбор тарифа во временное хранилище
    ACTIVE_INVOICES[user_id] = {
        "tariff_code": tariff_code,
        "devices": DEFAULT_DEVICES,
        "tariff_group": tariff_group,
        "user_id": user_id,
        "min_value": DEVICES_MIN,
        "max_value": DEVICES_MAX,
        "step": DEVICES_STEP
    }

    photo_path = "./assets/obhod_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"⚙️ <b>Настройка тарифа: {tariff_code}</b>\n\n"
                f"<blockquote>📱 Выберите количество устройств.\n"
                f"➕ Цена за доп. устройство: <b>50₽ / мес</b></blockquote>\n\n"
                f"<i>Выберите количество устройств 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.devices_selector_keyboard(
            user_id=user_id,
            current=DEFAULT_DEVICES,  # стартовое значение
            min_value=DEVICES_MIN,
            max_value=DEVICES_MAX,
            step=DEVICES_STEP
        )
    )

    await callback.answer('Настройка тарифа')

@router.callback_query(F.data.startswith("devices:") & F.data.contains(":set:"))
async def devices_set(callback: CallbackQuery):
    tg_id = callback.from_user.id

    _, _, _, new_value = callback.data.split(":")
    new_value = int(new_value)

    invoice = ACTIVE_INVOICES.get(tg_id)
    if not invoice:
        return await callback.answer("❌ Ошибка: параметры не найдены")

    min_value = invoice["min_value"]
    max_value = invoice["max_value"]

    new_value = max(min_value, min(max_value, new_value))
    invoice["devices"] = new_value

    await callback.message.edit_reply_markup(
        reply_markup=kb.devices_selector_keyboard(
            user_id=tg_id,
            current=new_value,
            min_value=min_value,
            max_value=max_value,
            step=invoice["step"]
        )
    )

    await callback.answer()

@router.callback_query(F.data.endswith(":next") & F.data.startswith("devices:"))
async def devices_next(callback: CallbackQuery):
    tg_id = callback.from_user.id

    invoice = ACTIVE_INVOICES.get(tg_id)
    if not invoice:
        return await callback.answer("❌ Ошибка: данные покупки не найдены")

    tariff_code = invoice["tariff_code"]
    tariff = TARIFFS.get(tariff_code)

    devices_total = invoice["devices"]
    devices_extra = max(0, devices_total - 1)

    base_price = tariff["price"]
    days = tariff["days"]

    extra_price = devices_extra * 50 * (days / 30)
    final_price = int(base_price + extra_price)

    invoice["devices_total"] = devices_total
    invoice["devices_extra"] = devices_extra
    invoice["base_price"] = base_price
    invoice["extra_price"] = int(extra_price)
    invoice["final_price"] = final_price
    invoice["amount"] = final_price

    photo_path = "./assets/obhod_knight.jpg"
    photo = FSInputFile(photo_path)

    text = (
        f"<b>⚙️ Подтверждение заказа</b>\n\n"
        f"<blockquote>💎 Тариф: <b>{tariff_code} | В него входит:</b>\n"
        f"─────────────────────────────\n"
        f"🗓 Дней: <b>{days}</b>\n"
        f"🌐 Трафик: <b>{tariff['traffic']}</b>\n"
        f"📱 Устройства: <b>{devices_total}</b>\n"
        f"➕ Доп: <b>{devices_extra} × 50₽ / мес</b>\n"
        f"─────────────────────────────</blockquote>\n\n"
        f"💰 <b>Итоговая цена: {base_price} + {extra_price} = {final_price}₽</b>\n\n"
        "<i>Подтвердите, чтобы перейти к оплате</i> 👇"
    )

    await callback.message.edit_media(
        InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
        reply_markup=kb.confirm_zakaz_keyboard(tg_id)
    )
    await callback.answer('Подтверждение')

# Кнопка назад
@router.callback_query(F.data == "back:tariffs")
async def back_to_tariffs(callback: CallbackQuery):
    tg_id = callback.from_user.id
    invoice = ACTIVE_INVOICES.get(tg_id)

    if not invoice:
        return await callback.answer("Ошибка: данные не найдены")

    group = invoice.get("tariff_group")

    if group == "basic":
        markup = kb.tariffs_b
        photo = "./assets/basic_knight.jpg"
        caption = (
                "↩️ <b>Вы вернулись на развилку.</b>\n\n"
                "<blockquote><i>В данные тарифы не входят серверы, предназначенные для обхода белых списков 🚫\n\n"
                "Они рассчитаны на более простые задачи и также подойдут пользователям из регионов, где ещё отсутствуют полноценные блокировки</i>\n\n"
                "🌍 <b>Сервера</b>: 🇺🇸 | 🇩🇪 | 🇳🇱 | 🇫🇮 | 🇷🇺 | 🇫🇷 | 🇵🇱 | 🇸🇪</blockquote>\n\n"
                "🛣 <i>Путь продолжается — выберите дорогу, что поведёт вас дальше…</i>\n"
            )
    elif group == "special":
        markup = kb.tariffs_s
        photo = "./assets/obhod_knight.jpg"
        caption = (
                "🥷 <b>Раздел специальных тарифов</b>\n\n"
                "<blockquote><i>Режимы с расширенными возможностями обхода блокировок и улучшенной стабильностью подключения</i> 📶\n\n"
                "🌍 <b>Сервера</b>:  🇷🇺 | 🇳🇱 | 🇫🇮 | 🇩🇪 | 🇫🇷 | 🇵🇱 | 🇸🇪</blockquote>\n\n"
                "<i>Выбери тариф — и получи более свободный доступ к нужным ресурсам 👇</i>"
            )
    elif group == "multi":
        markup = kb.tariffs_m
        photo = "./assets/obhod_knight.jpg"
        caption = (
                "💥 <b>Раздел мульти-доступа</b>\n\n"
                "<blockquote><i>Это место, где вы можете получить доступ ко всем серверам сервиса в одной подписке</i> 🛜\n\n"
                "🌍 <b>Сервера</b>: 🇺🇸 | 🇷🇺 | 🇳🇱 | 🇫🇮 | 🇩🇪 | 🇫🇷 | 🇵🇱 | 🇸🇪</blockquote>\n\n"
                "<i>Выбери тариф — и начни свой путь 👇</i>"
            )
    else:
        return await callback.answer("Ошибка: неизвестная группа тарифа")

    await callback.message.edit_media(
        InputMediaPhoto(
            media=FSInputFile(photo),
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=markup
    )

    await callback.answer("Назад")

@router.callback_query(F.data == "back:devices")
async def back_to_devices(callback: CallbackQuery):
    tg_id = callback.from_user.id
    invoice = ACTIVE_INVOICES.get(tg_id)

    if not invoice:
        return await callback.answer("Ошибка: заказ не найден")

    tariff_code = invoice["tariff_code"]
    current = invoice["devices"]

    photo_path = "./assets/obhod_knight.jpg"
    photo = FSInputFile(photo_path)

    caption = (
        f"⚙️ <b>Настройка тарифа: {tariff_code}</b>\n\n"
        f"<blockquote>📱 Выберите количество устройств.\n"
        f"➕ Цена за доп. устройство: <b>50₽ / мес</b></blockquote>\n\n"
        f"<i>Выберите количество устройств 👇</i>"
    )

    await callback.message.edit_media(
        InputMediaPhoto(
            media=photo,
            caption=caption,
            parse_mode="HTML"
        ),
        reply_markup=kb.devices_selector_keyboard(
            user_id=tg_id,
            current=current,
            min_value=invoice["min_value"],
            max_value=invoice["max_value"],
            step=invoice["step"]
        )
    )

    await callback.answer("Назад")

@router.callback_query(F.data.startswith("confirm:"))
async def confirm_order(callback: CallbackQuery):
    tg_id = callback.from_user.id

    # Извлекаем user_id из callback_data
    _, user_id = callback.data.split(":")
    user_id = int(user_id)

    # Берём заказ
    invoice = ACTIVE_INVOICES.get(tg_id)
    if not invoice:
        return await callback.answer("❌ Ошибка: заказ не найден")

    # Переход к выбору способа оплаты
    text = (
        "<b>🜃 Вы вошли в «Зал Монет и Теней»</b>\n\n"
        "Перед вами стоит <b>Платёжный Сундучок</b> 📦, он ждёт вашего решения.\n\n"
        "<i>Выберите способ оплаты 👇</i>"
    )

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb.payment_methods(tg_id),  # ← клавиатура со способами оплаты
        parse_mode="HTML"
    )

    await callback.answer('✅ Подтверждено')

@router.callback_query(F.data.startswith("cancel:"))
async def cancel_order(callback: CallbackQuery):
    tg_id = callback.from_user.id

    _, user_id = callback.data.split(":")
    user_id = int(user_id)

    await callback.answer('❌ Отмена')

    tg_id = callback.from_user.id
    ACTIVE_INVOICES.pop(tg_id, None)

    photo_path = "./assets/option_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"<b>Заказ отменён! Вы вернулись к выбору типа тарифа</b> 🌐\n\n" 
                f"<i>Всё ещё остаётся лишь выбрать подходящий...</i> 🤔" 
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )

# Создание инвойса для оплаты определённого тарифа через CryptoBot
@router.callback_query(F.data.startswith("pay:crypto:"))
async def handle_crypto_payment(callback: CallbackQuery):
    _, _, tariff_code = callback.data.split(":")
    tg_id = callback.from_user.id

    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("❌ Ошибка: тариф не найден")

    amount_rub = tariff["price"]
    
    # Проверяем скидку
    discount = await hp.get_active_discount(tg_id)
    if discount:
        amount_rub = round(amount_rub * (100 - discount) / 100)
    
    usd_rate = await cb.get_usd_rate()
    amount_usd = round(amount_rub / usd_rate, 2)

    invoice = cb.create_invoice(amount_usd, tg_id, tariff_code)

    photo_path = "./assets/cryptobot_knight.jpg"
    photo = FSInputFile(photo_path)

    ACTIVE_INVOICES[tg_id] = {
        "invoice_id": invoice["invoice_id"],
        "tariff_code": tariff_code,
        "amount": amount_rub,  
        "discount": discount 
    }

    if not invoice:
        return await callback.answer("Ошибка при создании счёта")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"💸 <b>Оплата тарифа: {tariff_code}</b>\n\n"
                f"💰 Сумма: <b>{amount_rub}₽ (~{amount_usd}$)</b>\n\n"
                + (f"🎁 Скидка применена: <b>-{discount}%</b>\n\n" if discount else "")
                + "<i>Нажмите кнопку ниже, чтобы оплатить 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.invoice_keyboard(invoice["pay_url"], invoice["invoice_id"])
    )


# ✅ Проверка платежа + выдача подписки (Crypto)
@router.callback_query(F.data.startswith("check:crypto:"))
async def check_payment(callback: CallbackQuery):
    tg_id = callback.from_user.id
    invoice_data = ACTIVE_INVOICES.get(tg_id)
    if not invoice_data:
        return await callback.answer("❌ Активный платёж не найден.")

    paid = cb.check_crypto_invoice(invoice_data["invoice_id"])
    if not paid:
        return await callback.answer("⏳ Платёж ещё не подтверждён. Попробуйте позже.")

    invoice_data = ACTIVE_INVOICES.pop(tg_id, None)
    tariff_code = invoice_data["tariff_code"] if invoice_data else None
    tariff = TARIFFS.get(tariff_code) if tariff_code else None
    if not tariff:
        return await callback.message.edit_caption("⚠️ Ошибка: тариф не найден", reply_markup=None)

    await callback.answer("✅ Оплата подтверждена!")

    start_date = datetime.now()
    end_date = start_date + timedelta(days=tariff["days"])
    start_str = start_date.strftime("%Y-%m-%d %H:%M")
    end_str = end_date.strftime("%Y-%m-%d %H:%M")

    # Создание или продление пользователя
    if tariff_code in SPECIAL_TARIFFS:
        user_data = await rm.create_special_paid_user(tg_id, tariff_code, tariff["days"])
    else:
        user_data = await rm.create_paid_user(tg_id, tariff_code, tariff["days"])

    sub_link = f"https://sub.grdguard.xyz/{user_data.get('shortUuid')}" if user_data.get('shortUuid') else "—"

    # ✅ Сбрасываем скидку
    await hp.reset_user_discount(tg_id)

    if tariff_code in SPECIAL_TARIFFS:
        photo_path = "./assets/success2_knight.jpg"
    else:
        photo_path = "./assets/success1_knight.jpg"
    photo = FSInputFile(photo_path)

    if user_data["status"] == "created":
        caption_text = (
            f"🎉 <b>Подписка успешно активирована!</b>\n\n"
            f"<blockquote>💎 <b>Тариф:</b> {tariff_code}\n\n"
            f"🕒 <b>Начало:</b> {start_str}\n"
            f"⏳ <b>Окончание:</b> {end_str}\n"
            f"🌐 <b>Трафик:</b> {tariff['traffic']}\n\n"
            f"📦 <b>Подписка:</b> {sub_link}</blockquote>\n\n"
            f"<i>Инструкции по подключению — в разделе “Помощь💬”</i>"
        )
    else:  # extended
        new_end = datetime.fromisoformat(user_data["expire_at"])
        caption_text = (
            f"♻️ <b>Подписка продлена!</b>\n\n"
            f"<blockquote>💎 <b>Тариф:</b> {tariff_code}\n\n"
            f"⏳ <b>Новая дата окончания:</b> {new_end.strftime('%Y-%m-%d %H:%M')}\n"
            f"🌐 <b>Трафик:</b> {tariff['traffic']}</blockquote>\n\n"
            f"<blockquote><i>“May the Force be with you.” — Star Wars 🌌</i></blockquote>"
        )

    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo, caption=caption_text, parse_mode="HTML"),
        reply_markup=kb.back_to_start
    )

    # ===============================
    # 📢 УВЕДОМЛЕНИЕ ОБ ОПЛАТЕ
    # ===============================

    # tg_id пользователя
    tg_id = callback.from_user.id

    # username (на случай если нет)
    username = callback.from_user.username or f"user{tg_id}"

    # информация для уведомления из user_data
    expire_at_str = user_data["expire_at"]
    expire_at = datetime.fromisoformat(expire_at_str)
    is_extension = user_data["status"] == "extended"

    # Достаём amount + discount из invoice_data (где ты их сохраняешь!)
    amount_rub = invoice_data.get("amount")     # сумма в рублях
    discount = invoice_data.get("discount")     # None или число

    # отправка уведомления
    await pn.notify_purchase(
        bot=callback.bot,
        tg_id=tg_id,
        username=username,
        tariff_code=tariff_code,
        amount=amount_rub,
        discount=discount,
        is_extension=is_extension,
        expire_at=expire_at
    )


# ❌ Отмена оплаты
@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery):
    tg_id = callback.from_user.id
    invoice_data = ACTIVE_INVOICES.pop(tg_id, None)

    photo_path = "./assets/option_knight.jpg"
    photo = FSInputFile(photo_path)

    if invoice_data:
        # Опционально — отменяем инвойс на стороне CryptoBot
        # (CryptoBot сам его закроет по таймауту, если не оплачено)
        pass

    await callback.answer("❌ Платёж отменён.")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"<b>Вы вернулись к выбору тарифа.</b> 🌐\n\n" 
                f"<i>Всё ещё остаётся лишь выбрать подходящий</i> 🤔" 
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )

# Создание платежа в зависимости от тарифа Юkassa
@router.callback_query(F.data.startswith("pay:yoo:"))
async def handle_yookassa_payment(callback: CallbackQuery):
    _, _, tariff_code = callback.data.split(":")
    tg_id = callback.from_user.id

    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("❌ Ошибка: тариф не найден")

    amount_rub = tariff["price"]

    # Получение активной скидки
    discount = await hp.get_active_discount(tg_id)
    if discount:
        amount_rub = round(amount_rub * (100 - discount) / 100)

    photo_path = "./assets/yookassa_knight.jpg"
    photo = FSInputFile(photo_path)

    pay_url, payment_id = yoo.create_invoice(amount_rub, tg_id, tariff_code, return_url)
    if not pay_url:
        return await callback.answer("❌ Ошибка при создании платежа")

    ACTIVE_INVOICES[tg_id] = {
        "payment_id": payment_id,
        "tariff_code": tariff_code,
        "amount": amount_rub,  
        "discount": discount 
    }

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"💸 <b>Оплата тарифа: {tariff_code}</b>\n\n"
                f"💰 Сумма: <b>{amount_rub}₽</b>\n\n"
                + (f"🎁 Скидка применена: <b>-{discount}%</b>\n\n" if discount else "")
                + "<i>Нажмите кнопку ниже, чтобы оплатить 👇</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.yookassa_invoice_keyboard(pay_url, payment_id)
    )

# ✅ Проверка платежа + выдача подписки (YooKassa)
@router.callback_query(F.data.startswith("check:yookassa:"))
async def check_yookassa_payment(callback: CallbackQuery):
    _, _, payment_id = callback.data.split(":")
    tg_id = callback.from_user.id

    # Проверка оплаты через YooKassa
    paid = yoo.check_payment(payment_id)
    if not paid:
        return await callback.answer("⏳ Платёж ещё не подтверждён.")

    # Достаём данные инвойса
    invoice_data = ACTIVE_INVOICES.pop(tg_id, None)
    tariff_code = invoice_data["tariff_code"] if invoice_data else None
    tariff = TARIFFS.get(tariff_code) if tariff_code else None
    if not tariff:
        return await callback.message.edit_caption("⚠️ Ошибка: тариф не найден", reply_markup=None)

    await callback.answer("✅ Оплата подтверждена!")

    start_date = datetime.now()
    end_date = start_date + timedelta(days=tariff["days"])
    start_str = start_date.strftime("%Y-%m-%d %H:%M")
    end_str = end_date.strftime("%Y-%m-%d %H:%M")

    # ----------------------------
    # Создание или продление подписки
    # ----------------------------
    if tariff_code in SPECIAL_TARIFFS:
        # Специальный тариф (Bypass/Whitelist)
        user_data = await rm.create_special_paid_user(tg_id, tariff_code, tariff["days"])
        # После успешного ответа с панели фиксируем в БД
        await hp.add_or_extend_special_subscription(
            tg_id=tg_id,
            plan_name=tariff_code,
            amount=tariff["price"],
            days=tariff["days"],
            uuid=user_data["uuid"]
        )
        photo_path = "./assets/success2_knight.jpg"
    else:
        # Базовый тариф (Base VPN)
        user_data = await rm.create_paid_user(tg_id, tariff_code, tariff["days"])
        await hp.add_or_extend_base_subscription(
            tg_id=tg_id,
            plan_name=tariff_code,
            amount=tariff["price"],
            days=tariff["days"],
            uuid=user_data["uuid"]
        )
        photo_path = "./assets/success1_knight.jpg"

    sub_link = f"https://sub.grdguard.xyz/{user_data.get('shortUuid')}" if user_data.get('shortUuid') else "—"
    photo = FSInputFile(photo_path)

    # ✅ Сбрасываем скидку
    await hp.reset_user_discount(tg_id)

    # ----------------------------
    # Формирование текста сообщения
    # ----------------------------
    if user_data["status"] == "created":
        caption_text = (
            f"🎉 <b>Подписка успешно активирована!</b>\n\n"
            f"<blockquote>💎 <b>Тариф:</b> {tariff_code}\n\n"
            f"🕒 <b>Начало:</b> {start_str}\n"
            f"⏳ <b>Окончание:</b> {end_str}\n"
            f"🌐 <b>Трафик:</b> {tariff['traffic']}\n\n"
            f"📦 <b>Подписка:</b> {sub_link}</blockquote>\n\n"
            f"<i>Инструкции по подключению — в разделе “Помощь💬”</i>"
        )
    else:  # продление
        new_end = datetime.fromisoformat(user_data["expire_at"])
        caption_text = (
            f"♻️ <b>Подписка продлена!</b>\n\n"
            f"<blockquote>💎 <b>Тариф:</b> {tariff_code}\n\n"
            f"⏳ <b>Новая дата окончания:</b> {new_end.strftime('%Y-%m-%d %H:%M')}\n"
            f"🌐 <b>Трафик:</b> {tariff['traffic']}</blockquote>\n\n"
            f"<blockquote><i>“I feel the need… the need for speed!” — Top Gun ✈️</i></blockquote>"
        )

    # Отправка медиа с текстом
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo, caption=caption_text, parse_mode="HTML"),
        reply_markup=kb.back_to_start
    )

    # ----------------------------
    # Уведомление о платеже
    # ----------------------------
    username = callback.from_user.username or f"user{tg_id}"
    expire_at = datetime.fromisoformat(user_data["expire_at"])
    is_extension = user_data["status"] == "extended"

    amount_rub = invoice_data.get("amount")
    discount = invoice_data.get("discount")

    await pn.notify_purchase(
        bot=callback.bot,
        tg_id=tg_id,
        username=username,
        tariff_code=tariff_code,
        amount=amount_rub,
        discount=discount,
        is_extension=is_extension,
        expire_at=expire_at
    )

# Отмена платежа yookassa
@router.callback_query(F.data == "cancel_yookassa")
async def cancel_yookassa_payment(callback: CallbackQuery):
    tg_id = callback.from_user.id
    ACTIVE_INVOICES.pop(tg_id, None)

    photo_path = "./assets/option_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.answer("❌ Платёж отменён.")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"<b>Вы вернулись к выбору тарифа.</b> 🌐\n\n" 
                f"<i>Всё ещё остаётся лишь выбрать подходящий</i> 🤔" 
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )

@router.callback_query(F.data.startswith("pay:rp:"))
async def handle_rp_payment(callback: CallbackQuery):
    _, _, tariff_code = callback.data.split(":")
    tg_id = callback.from_user.id

    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("❌ Ошибка: тариф не найден")

    amount_rub = tariff["price"]

    # Конвертация RUB → RP (1 RP = 8 RUB)
    amount_rp = math.ceil(amount_rub / 8)

    # Проверяем баланс RP пользователя
    user_rp = await hp.get_rp_balance(tg_id)

    photo = FSInputFile("./assets/rp_knight.jpg")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                f"💸 <b>Оплата тарифа: {tariff_code}</b>\n\n"
                f"💰 Цена: <b>{amount_rub}₽</b>\n"
                f"🟪 В RP: <b>{amount_rp} RP</b>\n"
                f"📦 Ваш баланс: <b>{user_rp} RP</b>\n\n"
                + "<i>Подтвердить оплату RP?</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.rp_confirm_keyboard(tariff_code, amount_rp)
    )

@router.callback_query(F.data.startswith("check:rp:"))
async def check_rp_payment(callback: CallbackQuery):
    _, _, tariff_code, amount_rp = callback.data.split(":")
    tg_id = callback.from_user.id
    amount_rp = int(amount_rp)

    tariff = TARIFFS.get(tariff_code)
    if not tariff:
        return await callback.answer("❌ Тариф не найден")

    user_rp = await hp.get_rp_balance(tg_id)

    if user_rp < amount_rp:
        return await callback.answer("❌ Недостаточно RP для оплаты.")

    # Списываем RP
    await hp.remove_rp(tg_id, amount_rp, reason=f"Оплата тарифа {tariff_code}")

    start_date = datetime.now()
    end_date = start_date + timedelta(days=tariff["days"])
    start_str = start_date.strftime("%Y-%m-%d %H:%M")
    end_str = end_date.strftime("%Y-%m-%d %H:%M")

    await callback.answer("✅ Оплата подтверждена!")

    # Создание/продление подписки
    if tariff_code in SPECIAL_TARIFFS:
        user_data = await rm.create_special_paid_user(tg_id, tariff_code, tariff["days"])
    else:
        user_data = await rm.create_paid_user(tg_id, tariff_code, tariff["days"])

    sub_link = f"https://sub.grdguard.xyz/{user_data.get('shortUuid')}" if user_data.get('shortUuid') else "—"

    # Оформление результата
    if tariff_code in SPECIAL_TARIFFS:
        photo_path = "./assets/success2_knight.jpg"
    else:
        photo_path = "./assets/success1_knight.jpg"
    photo = FSInputFile(photo_path)

    start_date = datetime.now()
    end_date = start_date + timedelta(days=tariff["days"])

    if user_data["status"] == "created":
        caption = (
            f"🎉 <b>Подписка успешно активирована!</b>\n\n"
            f"<blockquote>💎 <b>Тариф:</b> {tariff_code}\n\n"
            f"🕒 <b>Начало:</b> {start_str}\n"
            f"⏳ <b>Окончание:</b> {end_str}\n"
            f"🌐 <b>Трафик:</b> {tariff['traffic']}\n\n"
            f"📦 <b>Подписка:</b> {sub_link}</blockquote>\n\n"
            f"<i>Инструкции по подключению — в разделе “Помощь💬”</i>"
        )
    else:
        new_end = datetime.fromisoformat(user_data["expire_at"])
        caption = (
            f"♻️ <b>Подписка продлена!</b>\n\n"
            f"<blockquote>💎 <b>Тариф:</b> {tariff_code}\n\n"
            f"⏳ <b>Новая дата окончания:</b> {new_end.strftime('%Y-%m-%d %H:%M')}\n"
            f"🌐 <b>Трафик:</b> {tariff['traffic']}</blockquote>\n\n"
            f"<blockquote><i>“It doesn’t matter how fast you go — what matters is that you’re moving in the right direction 🤝”</i></blockquote>"
        )

    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
        reply_markup=kb.back_to_start
    )

@router.callback_query(F.data == "cancel_rp")
async def cancel_rp_payment(callback: CallbackQuery):
    photo = FSInputFile("./assets/option_knight.jpg")

    await callback.answer("❌ Оплата RP отменена.")

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
                "<b>Вы вернулись к выбору тарифа.</b> 🌐\n\n"
                "<i>Выберите подходящий способ оплаты</i>"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.tarifs
    )


# Начало создания промокода
@router.message(Command("setpromo"))
async def setpromo_start(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return
    
    await state.set_state(CreatePromo.waiting_for_code)

    await message.answer(
        "✳️ <b>Вы перешли в меню создание промокода</b>\n"
        "<i>Введите промокод (только буквы и цифры, без пробелов):</i> \n",
        parse_mode="HTML",
        reply_markup=kb.cancel
    )

# Выбор типа промокода
@router.message(CreatePromo.waiting_for_code)
async def setpromo_code(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    promo_code = message.text.upper().strip()

    # Проверка существования
    if await hp.promo_exists(promo_code):
        return await message.answer(
            "⚠️ <b>Такой промокод уже существует.</b>\n\n"
            "<i>Введите другое название промокода:</i>",
            reply_markup=kb.cancel,
            parse_mode="HTML"
        )

    await state.update_data(promo_code=promo_code)
    await state.set_state(CreatePromo.waiting_for_type)

    await message.answer(
        f"🎞 Промокод: <b>{promo_code}</b>\n\n"
        f"<i>Выберите тип:</i>",
        reply_markup=kb.promo_type,
        parse_mode="HTML"
    )

# Тип - скидка
@router.callback_query(F.data == "promo_type_discount")
async def  promo_type_discount(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    await state.update_data(promo_type="discount")
    await state.set_state(CreatePromo.waiting_for_value)

    await callback.message.edit_text(
        "<b>Введите процент скидки (1-80):</b>",
        parse_mode="HTML"
        )

# Тип - пополнение бонусных дней
@router.callback_query(F.data == "promo_type_bonus")
async def promo_type_bonus(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    await state.update_data(promo_type="bonus")
    await state.set_state(CreatePromo.waiting_for_value)

    await callback.message.edit_text(
        "<b>Введите количество RP: </b>",
        parse_mode="HTML"
        )

# Максимальное кол-во использований
@router.message(StateFilter(CreatePromo.waiting_for_value))
async def setpromo_value(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        value = float(message.text)
    except ValueError:
        return await message.answer("Введите число!")

    await state.update_data(value=int(message.text))
    await state.set_state(CreatePromo.waiting_for_max_uses)

    await message.answer(
        "<b>Введите максимальное количество использований:</b>",
        parse_mode="HTML"
        )

# Промокод создан
@router.message(StateFilter(CreatePromo.waiting_for_max_uses))
async def setpromo_finish(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    if not message.text.isdigit():
        return await message.answer("Введите число!")

    max_uses = int(message.text)
    data = await state.get_data()

    promo_code = data["promo_code"]
    promo_type = data["promo_type"]
    value = data["value"]

    if promo_type == "discount":
        await hp.create_discount_promo(promo_code, value, max_uses)
        text = (
            f"✅ Промокод создан!\n\n"
            f"Тип: <b>Скидка</b>\n"
            f"Код: <code>{promo_code}</code>\n"
            f"Скидка: <b>{value}%</b>\n"
            f"Максимум использований: <b>{max_uses}</b>"
        )

    else:  # bonus
        await hp.create_bonus_promo(promo_code, value, max_uses)
        text = (
            f"✅ Промокод создан!\n\n"
            f"Тип: <b>🎁 RP</b>\n"
            f"Код: <code>{promo_code}</code>\n"
            f"Дает: <b>{value}</b> RP\n"
            f"Максимум использований: <b>{max_uses}</b>"
        )

    await state.clear()
    await message.answer(text, parse_mode="HTML", reply_markup=kb.back)

# Кнопка активация промокода
@router.callback_query(F.data == "activate_promo")
async def ask_promo(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Активируем промокод")
    await state.set_state(PromoActivate.waiting_for_promo)
    await callback.message.answer("🎟 Введите промокод:", reply_markup=kb.cancel)

# Активация промокода
@router.message(StateFilter(PromoActivate.waiting_for_promo))
async def apply_promo(message: Message, state: FSMContext):
    await state.clear()
    code = message.text.upper().strip()
    user_id = message.from_user.id

    # промокодик на скидку
    promo = await hp.get_discount_promo(code)
    if promo:

        # 🔥 Проверяем использовал ли уже пользователь этот промокод
        if await hp.user_used_promo(user_id, promo.id):
            return await message.answer("⚠️ Вы уже использовали этот промокод ранее.", reply_markup=kb.back)

        await hp.use_discount_promo(promo, user_id)
        await hp.save_promo_use(user_id, promo.id)

        return await message.answer(
            f"✅ Промокод <b>{code}</b> активирован!\n"
            f"💸 При покупке тарифа ваша скидка составит <b>{promo.discount_percent}%</b>",
            reply_markup=kb.back,
            parse_mode="HTML"
        )

    # промокодик на бонусные дни
    promo = await hp.get_bonus_promo(code)
    if promo:

        if await hp.user_used_promo(user_id, promo.id):
            return await message.answer("⚠️ Вы уже использовали этот промокод ранее.", reply_markup=kb.back)

        await hp.use_bonus_promo(promo, user_id)
        await hp.save_promo_use(user_id, promo.id)

        return await message.answer(
            f"✅ Промокод <b>{code}</b> активирован!\n"
            f"🎁 На баланс добавлено <b>{promo.bonus_days} RP</b>.",
            reply_markup=kb.back,
            parse_mode="HTML"
        )

    await message.answer(
        "❌ Промокод не найден или больше не активен.",
        reply_markup=kb.back,
        parse_mode="HTML"
    )

# Отмена создания ИЛИ отмена активации промокода
@router.callback_query(F.data == "cancel")
async def cancel_promo(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отмена")

# патчим подписку если есть возможность ДНИ
@router.callback_query(F.data == "basevpn")
async def update_paid_subscription(callback: CallbackQuery):
    tg_id = callback.from_user.id

    # Проверяем наличие подписки и кол-во дней
    data = await hp.check_paid_subscription_and_days(tg_id)
    if not data:
        return await callback.answer(
            "❗ Активная платная подписка не найдена или баланс дней пуст.", 
            show_alert=True
        )

    # Патчим подписку
    result = await rm.apply_rp_days(tg_id)

    if result["status"] == "success":
        return await callback.answer(
            f"✅ Дни успешно добавлены!\n"
            f"Новая дата окончания:\n"
            f"{result['new_expire'].strftime('%Y-%m-%d %H:%M')}",
            show_alert=True
        )

    if result["status"] == "api_error":
        return await callback.answer(
            "❌ Ошибка API при обновлении подписки.",
            show_alert=True
        )

    return await callback.answer(
        "❌ Не удалось обновить подписку.",
        show_alert=True
    )

@router.callback_query(F.data == "obhodwl")
async def update_special_subscription(callback: CallbackQuery):
    tg_id = callback.from_user.id

    # Проверяем наличие спец-подписки и ГБ
    data = await hp.check_special_subscription_and_gb(tg_id)
    if not data:
        return await callback.answer(
            "❗ Активная подписка Обход Whitelists не найдена или баланс ГБ пуст.",
            show_alert=True
        )

    # Патчим лимит ГБ через API + обнуляем баланс
    result = await rm.apply_rp_gb(tg_id)

    if result["status"] == "success":
        return await callback.answer(
            "✅ Гигабайты успешно добавлены!\n"
            "Новый доступный лимит обновлён.",
            show_alert=True
        )

    if result["status"] == "api_error":
        return await callback.answer(
            "❌ Ошибка API при обновлении лимита.",
            show_alert=True
        )

    return await callback.answer(
        "❌ Не удалось обновить подписку.",
        show_alert=True
    )

# Начало конвертации поинтов
@router.callback_query(F.data == "start_conversion")
async def start_conversion(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Конвертация RP')  
    await state.set_state(ConvertRPStates.choose_resource)
    await callback.message.answer(
        "🔄 Выберите, что хотите получить:",
        reply_markup=kb.convert_resource_kb
    )

# Отмена конвертации из любого состояния FSM
@router.callback_query(F.data == 'cancel_conversion')
async def cancel_promo(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("❌ Отмена")
    await callback.message.delete()

@router.callback_query(F.data == "back_to_amount_choice")
async def back_to_amount_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target = data["target_resource"]
    balance = await hp.get_rp_balance(callback.from_user.id)

    await callback.message.edit_text(
        f"🖊 <b>Выберите количество для конвертации:</b>\n"
        f"<blockquote>Ваш баланс: {balance} RP</blockquote>",
        reply_markup=kb.convert_amount_kb(balance),
        parse_mode='HTML'
    )

    await state.set_state(ConvertRPStates.choose_amount_type)

# Выбор ресурса
@router.callback_query(F.data.startswith("convert_"), ConvertRPStates.choose_resource)
async def choose_resource(callback: CallbackQuery, state: FSMContext):
    resource = callback.data.split("_")[1]  # days или gb
    await state.update_data(target_resource=resource)

    balance = await hp.get_rp_balance(callback.from_user.id)
    await callback.message.edit_text(
        f"🖊 <b>Выберите количество для конвертации:</b>\n"
        f"<blockquote>Ваш баланс: {balance} RP</blockquote>",
        reply_markup=kb.convert_amount_kb(balance),
        parse_mode='HTML'
    )
    await state.set_state(ConvertRPStates.choose_amount_type)

# Выбор количества (мин/макс/частично)
from aiogram.exceptions import TelegramBadRequest

# Выбор количества (MIN/MAX/PARTIAL)
@router.callback_query(F.data.startswith("amount_"), ConvertRPStates.choose_amount_type)
async def choose_amount(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target = data.get("target_resource")
    user_id = callback.from_user.id
    balance = await hp.get_rp_balance(user_id)

    # --- MIN ---
    if callback.data == "amount_min":
        rp_amount = 2

    # --- MAX ---
    elif callback.data == "amount_max":
        rp_amount = balance

    # --- PARTIAL ---
    elif callback.data == "amount_partial":
        # изменить текущее сообщение — сохранить ID этого сообщения для удаления позже
        try:
            msg = await callback.message.edit_text(
                f"✏️ <b>Введите количество RP для конвертации: </b>\n\n"
                f"<blockquote><b>Ваш баланс: {balance} RP</b>\n"
                f"<b>Минимум: 2 RP</b></blockquote>",
                reply_markup=kb.back_conversion_step_kb,
                parse_mode='HTML'
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                msg = callback.message
            else:
                raise

        # сохраняем ID сообщения (именно этого бота-сообщения)
        await state.update_data(prompt_msg_id=msg.message_id)

        await state.set_state(ConvertRPStates.enter_custom_amount)
        return

    else:
        await state.clear()
        return await callback.message.answer(
            "❌ Конвертация отменена.",
            reply_markup=kb.back1
        )

    # MIN / MAX — выполняем конвертацию
    success = await hp.convert_rp(user_id, rp_amount, target)
    await state.clear()

    if not success:
        return await callback.message.edit_text(
            "❌ Конвертация невозможна.\nПричина: недостаточно RP или превышен лимит копилки.",
            reply_markup=kb.back1,
            parse_mode='HTML'
        )

    # Рассчитываем результат
    if target == "days":
        converted = rp_amount
        resource = "дней"
    else:
        converted = rp_amount * 1.5
        resource = "ГБ"

    # Редактируем текущее сообщение с результатом; если нет изменений — игнорируем ошибку
    try:
        await callback.message.edit_text(
            "✨ <b>Конвертация завершена</b>\n\n"
            f"<blockquote>🔸 Потрачено: <b>{rp_amount} RP</b>\n"
            f"🔹 Получено: <b>{converted} {resource}</b></blockquote>",
            reply_markup=kb.back1,
            parse_mode='HTML'
        )
    except TelegramBadRequest as e:
        # игнорируем "message is not modified"
        if "message is not modified" not in str(e):
            raise


# Ввод RP вручную
@router.message(ConvertRPStates.enter_custom_amount)
async def enter_custom_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")
    target = data.get("target_resource")
    user_id = message.from_user.id
    balance = await hp.get_rp_balance(user_id)

    # --- Парсинг числа ---
    try:
        rp_amount = int(message.text.strip())
    except ValueError:
        return await message.answer(
            "❌ Введите корректное число.",
            reply_markup=kb.back_conversion_step_kb
        )

    if rp_amount < 2:
        return await message.answer(
            "⚠️ Минимальная конвертация — 2 RP.",
            reply_markup=kb.back_conversion_step_kb
        )

    if rp_amount > balance:
        return await message.answer(
            f"❌ Недостаточно RP. Баланс: {balance} RP",
            reply_markup=kb.back_conversion_step_kb
        )

    # --- Конвертация ---
    success = await hp.convert_rp(user_id, rp_amount, target)
    await state.clear()

    if not success:
        # Заменяем сообщение-подсказку на ошибку
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=prompt_msg_id,
                text="❌ Конвертация невозможна.\nПричина: недостаточно RP или превышен лимит.",
                reply_markup=kb.back1,
                parse_mode='HTML'
            )
        except TelegramBadRequest:
            pass
        await message.delete()
        return

    # --- Вычисляем результат ---
    if target == "days":
        converted = rp_amount
        resource = "дней"
    else:
        converted = rp_amount * 1.5
        resource = "ГБ"

    # --- Удаляем сообщение пользователя (число) ---
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    # --- ЗАМЕНЯЕМ подсказку итогом (а не создаём новое сообщение!) ---
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=prompt_msg_id,
            text=(
                "✨ <b>Конвертация завершена</b>\n\n"
                f"<blockquote>🔸 Потрачено: <b>{rp_amount} RP</b>\n"
                f"🔹 Получено: <b>{converted} {resource}</b></blockquote>"
            ),
            reply_markup=kb.back1,
            parse_mode='HTML'
        )
    except TelegramBadRequest:
        pass


# 1) Команда запуска рассылки
@router.message(Command("mailing"))
async def mailing_start(message: Message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS:
        return

    # записываем начала рассылки в массив временного сохранения
    TEMP_MAILING[admin_id] = {"state": "waiting_for_message"}

    await message.answer(
        "✉️ Отправь сообщение для рассылки.\n\n"
        "Можно отправить:\n"
        "• текст\n"
        "• фото + подпись\n"
        "• видео + подпись\n\n"
        "Чтобы отменить — нажми кнопку внизу.",
        reply_markup=kb.mailing1  # кнопка, отправляющая callback "mailing_cancel"
    )

# --- Принятие сообщения для рассылки ---
@router.message()
async def mailing_prepare(message: types.Message):
    tg_id = message.from_user.id

    if tg_id not in ADMIN_IDS or tg_id not in TEMP_MAILING:
        return

    # Определяем формат сообщения
    if message.photo:
        TEMP_MAILING[tg_id] = {
            "type": "photo",
            "file_id": message.photo[-1].file_id,
            "caption": message.caption
        }

    elif message.video:
        TEMP_MAILING[tg_id] = {
            "type": "video",
            "file_id": message.video.file_id,
            "caption": message.caption
        }

    elif message.animation:  # GIF
        TEMP_MAILING[tg_id] = {
            "type": "animation",
            "file_id": message.animation.file_id,
            "caption": message.caption
        }

    else:
        TEMP_MAILING[tg_id] = {
            "type": "text",
            "text": message.text
        }

    await message.answer(
        "📩 Готово. Отправить это всем пользователям?",
        reply_markup=kb.mailing
    )


# Отмена рассылки 
@router.callback_query(F.data == "mailing_cancel")
async def mailing_cancel(callback: CallbackQuery):
    TEMP_MAILING.pop(callback.from_user.id, None)
    await callback.message.edit_text("❌ Рассылка отменена.")


# Отправка рассылки
@router.callback_query(F.data == "mailing_send")
async def mailing_send(callback: CallbackQuery):
    tg_id = callback.from_user.id
    data = TEMP_MAILING.get(tg_id)

    if not data:
        return await callback.answer("❌ Нет сохранённого сообщения.")

    users = await hp.get_all_users()
    total = len(users)
    sent = 0

    await callback.message.edit_text(f"📨 Начинаю рассылку... 👥 {total} пользователей")

    for user_id in users:
        try:
            if data["type"] == "text":
                await callback.bot.send_message(user_id, data["text"])
            elif data["type"] == "photo":
                await callback.bot.send_photo(user_id, data["file_id"], caption=data.get("caption") or "")
            elif data["type"] == "video":
                await callback.bot.send_video(user_id, data["file_id"], caption=data.get("caption") or "")
            elif data["type"] == "animation":  # <- отправка GIF
                await callback.bot.send_animation(user_id, data["file_id"], caption=data.get("caption") or "")
            
            sent += 1
        except:
            pass  # пользователь мог заблокировать бота

        await asyncio.sleep(0.05)

    TEMP_MAILING.pop(tg_id, None)

    await callback.message.edit_text(f"✅ Доставлено: {sent} из {total}")


# Простой скипающий не нужные файлы обработчик
@router.message(F.content_type.in_({'photo', 'video', 'document'}))
async def reject_media(message: Message):
    pass
