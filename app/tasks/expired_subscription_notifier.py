import asyncio
from datetime import datetime, timedelta, timezone
from aiogram.types import FSInputFile
from app import helpers as hp
from app.services import remnawave_api as rm
from app import keyboards as kb
from aiogram import Bot
from config import TOKEN

bot1 = Bot(token=TOKEN)

async def expired_subscriptions_notifier1():
    while True:
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

                # --- текст + кнопки ---
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

                await bot1.send_photo(
                        chat_id=tg_id,
                        photo=FSInputFile("./assets/failure_knight.jpg"),
                        caption = text,
                        parse_mode="HTML",
                        reply_markup = key
                    )

                await hp.mark_notified(tg_id, sub_type)

            # --- еженедельный reset ---
            if await hp.should_reset_notifications():
                await hp.reset_expired_notifications()

        except Exception as e:
            print("[EXPIRED NOTIFIER ERROR]", e)

        await asyncio.sleep(1800)
