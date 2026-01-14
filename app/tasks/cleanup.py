import asyncio
from datetime import datetime, timedelta, timezone
from app.services import remnawave_api as rm

async def cleanup_expired_trials():
    """Удаляет пользователей с истёкшим trial спустя 2 часа после окончания."""
    while True:
        try:
            users = await rm.get_all_users()
            now = datetime.now(timezone.utc)

            for user in users:
                desc = (user.get("description") or "").lower()
                status = (user.get("status") or "").lower()
                expire_at = user.get("expireAt")
                uuid = user.get("uuid")

                # фильтруем нужных пользователей
                if "trial" not in desc or status != "expired" or not expire_at:
                    continue

                expire_time = datetime.fromisoformat(expire_at.replace("Z", "+00:00"))
                if now > expire_time + timedelta(hours=2):
                    await rm.delete_user(uuid)

        except Exception as e:
            print(f"[cleanup_expired_trials] Ошибка: {e}")

        # Интервал между проверками (1 час)
        await asyncio.sleep(3600)
