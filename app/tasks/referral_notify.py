import asyncio
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramRetryAfter
)

from sqlalchemy import select
from app.db.dealer import async_session_maker
from app.db.models import NotificationMeta
from app import helpers as hp
from app import keyboards as kb
from config import TOKEN


bot3 = Bot(token=TOKEN)


REFERRAL_TEXT = (
    "🚀 <b>Приглашай друзей — получай VPN бесплатно!</b>\n\n"
    "За каждого приглашённого друга ты получаешь бонус к подписке.\n\n"
    "Жми кнопку ниже и делись своей ссылкой 👇"
)


async def send_weekly_referral_notifications():
    while True:
        try:
            now = datetime.now(timezone.utc)

            async with async_session_maker() as session:

                # Получаем единственную строку мета-таблицы
                stmt = select(NotificationMeta)
                result = await session.execute(stmt)
                meta = result.scalar_one_or_none()

                # Если таблица пустая — создаём запись
                if not meta:
                    meta = NotificationMeta(
                        last_referral_notify=now
                    )
                    session.add(meta)
                    await session.commit()

                # Проверяем, нужно ли отправлять
                if meta.last_referral_notify:
                    if now - meta.last_referral_notify < timedelta(days=7):
                        await asyncio.sleep(3600)
                        continue

                print("[REFERRAL] Sending weekly broadcast")

                # Получаем пользователей через helpers
                users = await hp.get_all_users()

                meta.last_referral_notify = now
                await session.commit()

                for user in users:
                    tg_id = user.tg_id

                    try:
                        await bot3.send_photo(
                            chat_id=tg_id,
                            text=REFERRAL_TEXT,
                            photo=FSInputFile("./assets/referral_notify_knight.jpg"),
                            reply_markup=kb.referral_notify,
                            parse_mode="HTML"
                        )

                        # анти-флуд
                        await asyncio.sleep(0.05)

                    except TelegramForbiddenError:
                        continue

                    except TelegramBadRequest:
                        continue

                    except TelegramRetryAfter as e:
                        await asyncio.sleep(e.retry_after)
                        continue

                    except Exception as e:
                        print(f"[REFERRAL SEND ERROR] {e}")
                        continue

                # Обновляем дату глобальной рассылки
                meta.last_referral_notify = now
                await session.commit()

                print("[REFERRAL] Broadcast finished")

        except Exception as e:
            print(f"[REFERRAL LOOP ERROR] {e}")

        # Проверяем раз в час
        await asyncio.sleep(3600)

