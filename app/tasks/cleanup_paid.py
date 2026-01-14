import asyncio
from datetime import datetime, timedelta, timezone
from app.services import remnawave_api as rm
from app import helpers as hp

async def cleanup_expired_paid():
    """Удаляет просроченных платных подписчиков: сначала из БД, затем из панели."""
    while True:
        try:
            users = await rm.get_all_users()
            now = datetime.now(timezone.utc)

            for user in users:
                desc = (user.get("description") or "").lower()
                status = (user.get("status") or "").lower()
                expire_at = user.get("expireAt")
                uuid = user.get("uuid")

                # Удаляем ТОЛЬКО платных
                if "paid" not in desc:
                    continue

                # Должен быть EXPIRED
                if status != "expired":
                    continue

                if not expire_at or not uuid:
                    continue

                expire_time = datetime.fromisoformat(
                    expire_at.replace("Z", "+00:00")
                )

                if now > expire_time + timedelta(hours=10):
                    removed_from_db = await hp.remove_paid_subscription_by_uuid(uuid)
                    if removed_from_db:
                        await rm.delete_user(uuid)

        except Exception:
            pass

        await asyncio.sleep(3600)