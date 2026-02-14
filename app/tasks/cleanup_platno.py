import asyncio
from datetime import datetime, timedelta, timezone
from app.services import remnawave_api as rm
from app import helpers as hp
from app.db.dealer import async_session_maker
from app.db.models import Subscriptions
from sqlalchemy import select

async def cleanup_expired_subscriptions():
    while True:
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

                    # 🔍 Определяем тип подписки
                    if "paid" in desc:
                        sub_type = "base"
                    elif "special" in desc:
                        sub_type = "bypass"
                    elif "multi" in desc:
                        sub_type = "multi"
                    else:
                        continue

                    # 🔎 Ищем строку по uuid
                    stmt = select(Subscriptions).where(
                        getattr(Subscriptions, f"{sub_type}_uuid") == uuid
                    )
                    result = await session.execute(stmt)
                    subscription = result.scalar_one_or_none()

                    if not subscription:
                        continue

                    # 🧠 Проверяем другие активные
                    if has_other_active(subscription, sub_type):
                        # просто обнуляем конкретный тариф
                        reset_subscription_type(subscription, sub_type)
                        await session.commit()
                    else:
                        # удаляем строку полностью
                        await session.delete(subscription)
                        await session.commit()

                    # 🗑 удаляем пользователя из панели
                    await rm.delete_user(uuid)

        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

        await asyncio.sleep(3600)


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
