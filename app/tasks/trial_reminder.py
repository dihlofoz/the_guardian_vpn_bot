import asyncio
from datetime import datetime, timedelta, timezone
from aiogram.types import FSInputFile
from app import helpers as hp
from app.services import remnawave_api as rm
from app import keyboards as kb
from main import bot


async def trial_reminder_task():
    """
    Периодическая задача — отправляет уведомление пользователям,
    у которых есть Trial, но они ещё не подключались.
    """
    while True:
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

                created_at = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
                if created_at > day_ago:
                    continue

                # Проверяем в БД, что уведомление ещё не отправлено
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
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"[Ошибка при отправке уведомления {u.get('telegramId')}] {e}")

        except Exception as e:
            print(f"[trial_reminder_task] Ошибка выполнения задачи: {e}")

        # Проверяем раз в 6 часов (можешь поставить 86400 для 1 раза в день)
        await asyncio.sleep(86400)