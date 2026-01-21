from datetime import datetime, timedelta
from config import REMNAWAVE_BASE_URL, REMNAWAVE_TOKEN, SQUAD_ID, TARIFFS, TRIAL_DAYS, TRIAL_TRAFFIC_BYTES, SECOND_SQUAD_ID, SPECIAL_TRAFFIC_LIMITS, SQUAD_ID_TRIAL, DEFAULT_DEVICES, MULTI_TRAFFIC_LIMITS
import asyncio
import re
import httpx
from typing import List, Dict
from app import helpers as hp
from app.db.dealer import async_session_maker
from sqlalchemy import select

# Константа с эндпоинтом пользователей
REMNA_API_URL = f"{REMNAWAVE_BASE_URL.rstrip('/')}/users"


async def create_trial_user(telegram_id: int):

    username = f"letstry_{telegram_id}"
    expire_at = (datetime.utcnow() + timedelta(days=TRIAL_DAYS)).isoformat() + "Z"

    payload = {
        "username": username,
        "status": "ACTIVE",
        "expireAt": expire_at,
        "trafficLimitBytes": TRIAL_TRAFFIC_BYTES,
        "trafficLimitStrategy": "NO_RESET",
        "telegramId": telegram_id,
        "email": f"{username}@trial.remna",
        "hwidDeviceLimit": 3,
        "activeInternalSquads": [SQUAD_ID_TRIAL],
        "description": f"Trial"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(REMNA_API_URL, headers=headers, json=payload)

    if response.status_code not in (200, 201):
        raise Exception(f"{response.status_code} - {response.text}")

    # Теперь сразу получаем shortUuid по telegramId
    short_uuid = await get_short_uuid_by_telegram(telegram_id)

    return {
        "username": username,
        "shortUuid": short_uuid
    }

# Возвращает shortUuid пользователя по его Telegram ID
async def get_short_uuid_by_telegram(telegram_id: int) -> str:
    
    url = f"{REMNAWAVE_BASE_URL.rstrip('/')}/users/by-telegram-id/{telegram_id}"
    headers = {"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()  # автоматически бросит исключение, если код != 200

    data = r.json().get("response", [])
    if not data:
        raise Exception(f"Пользователь с Telegram ID {telegram_id} не найден")

    return data[0].get("shortUuid")

# Возвращает shortUuid PAID подписки для пользователя по Telegram ID
async def get_short_uuid_by_telegram_paid(telegram_id: int) -> str:
    url = f"{REMNAWAVE_BASE_URL.rstrip('/')}/users/by-telegram-id/{telegram_id}"
    headers = {"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()

    users = r.json().get("response", [])
    if not users:
        raise Exception(f"Пользователь с Telegram ID {telegram_id} не найден")

    # Ищем пользователя, у которого description содержит "paid"
    for user in users:
        desc = (user.get("description") or "").lower()
        if "paid" in desc:
            short_uuid = user.get("shortUuid")
            if short_uuid:
                return short_uuid
            else:
                raise Exception("У найденного PAID-пользователя отсутствует shortUuid")

    # Если SPECIAL пользователи не найдены
    raise Exception(f"У пользователя с Telegram ID {telegram_id} нет PAID-подписки")

# Возвращает shortUuid специальной (Special) подписки для пользователя по Telegram ID
async def get_short_uuid_by_telegram_special(telegram_id: int) -> str:
    url = f"{REMNAWAVE_BASE_URL.rstrip('/')}/users/by-telegram-id/{telegram_id}"
    headers = {"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()

    users = r.json().get("response", [])
    if not users:
        raise Exception(f"Пользователь с Telegram ID {telegram_id} не найден")

    # Ищем пользователя, у которого description содержит "special"
    for user in users:
        desc = (user.get("description") or "").lower()
        if "special" in desc:
            short_uuid = user.get("shortUuid")
            if short_uuid:
                return short_uuid
            else:
                raise Exception("У найденного SPECIAL-пользователя отсутствует shortUuid")

    # Если SPECIAL пользователи не найдены
    raise Exception(f"У пользователя с Telegram ID {telegram_id} нет SPECIAL-подписки")

# Возвращает shortUuid специальной (Special) подписки для пользователя по Telegram ID
async def get_short_uuid_by_telegram_multi(telegram_id: int) -> str:
    url = f"{REMNAWAVE_BASE_URL.rstrip('/')}/users/by-telegram-id/{telegram_id}"
    headers = {"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()

    users = r.json().get("response", [])
    if not users:
        raise Exception(f"Пользователь с Telegram ID {telegram_id} не найден")

    # Ищем пользователя, у которого description содержит "multi"
    for user in users:
        desc = (user.get("description") or "").lower()
        if "multi" in desc:
            short_uuid = user.get("shortUuid")
            if short_uuid:
                return short_uuid
            else:
                raise Exception("У найденного MULTI-пользователя отсутствует shortUuid")

    # Если SPECIAL пользователи не найдены
    raise Exception(f"У пользователя с Telegram ID {telegram_id} нет MULTI-подписки")
 
# Создаёт платного пользователя через Remnawave API
async def create_paid_user(tg_id: int, tariff_code: str, days: int, hwid_limit: int):
    safe_tariff_code = re.sub(r'[^A-Za-z0-9_-]', '_', tariff_code)
    base_username = f"paid_{tg_id}_{safe_tariff_code}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
    }

    active = await hp.get_active_base_subscription(tg_id)

    async with httpx.AsyncClient(timeout=30) as client:
        if active and active.get("uuid"):
            # Продление подписки
            new_expire_dt = active["expire_date"] + timedelta(days=days)
            new_expire_str = new_expire_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

            payload = {
                "uuid": active["uuid"],
                "username": active.get("username", base_username),
                "status": "ACTIVE",
                "expireAt": new_expire_str,
                "telegramId": tg_id,
                "email": f"{base_username}@paid.remna",
                "description": f"Paid {tariff_code}",
                "hwidDeviceLimit": hwid_limit,
                "activeInternalSquads": [SQUAD_ID]
            }

            response = await client.patch(
                REMNA_API_URL,
                headers=headers,
                json=payload
            )

            if response.status_code not in (200, 201, 204):
                raise Exception(f"{response.status_code} - {response.text}")

            await hp.add_or_extend_base_subscription(
                tg_id=tg_id,
                plan_name=tariff_code,
                days=days,
                amount=TARIFFS[tariff_code]["price"],
                uuid=active["uuid"]
            )

            # shortUuid берём корректно
            short_uuid = await get_short_uuid_by_telegram_paid(tg_id)

            return {
                "status": "extended",
                "expire_at": new_expire_str,
                "uuid": active["uuid"],
                "shortUuid": short_uuid
            }

        else:
            # Создание новой подписки
            expire_at_dt = datetime.utcnow() + timedelta(days=days)
            expire_at_str = expire_at_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

            payload = {
                "username": base_username,
                "status": "ACTIVE",
                "expireAt": expire_at_str,
                "telegramId": tg_id,
                "email": f"{base_username}@paid.remna",
                "hwidDeviceLimit": hwid_limit,
                "activeInternalSquads": [SQUAD_ID],
                "description": f"Paid {tariff_code}"
            }

            response = await client.post(REMNA_API_URL, headers=headers, json=payload)
            if response.status_code not in (200, 201):
                raise Exception(f"{response.status_code} - {response.text}")

            res_json = response.json().get("response", {})
            uuid = res_json.get("uuid")

            await hp.add_or_extend_base_subscription(
                tg_id=tg_id,
                plan_name=tariff_code,
                days=days,
                amount=TARIFFS[tariff_code]["price"],
                uuid=uuid
            )

            # shortUuid получаем так же, как в trial
            short_uuid = await get_short_uuid_by_telegram_paid(tg_id)

            return {
                "status": "created",
                "username": base_username,
                "uuid": uuid,
                "shortUuid": short_uuid,
                "expire_at": expire_at_str
            }
        
async def create_special_paid_user(tg_id: int, tariff_code: str, days: int, hwid_limit: int):
    safe_tariff_code = re.sub(r'[^A-Za-z0-9_-]', '_', tariff_code)
    base_username = f"special_{tg_id}_{safe_tariff_code}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
    }

    # Берём лимит по тарифу
    traffic_limit_bytes = SPECIAL_TRAFFIC_LIMITS.get(tariff_code, 0)  # 0 = безлимит

    # Проверяем активную спец-подписку
    active = await hp.get_active_special_subscription(tg_id)

    async with httpx.AsyncClient(timeout=30) as client:

        #  ПРОДЛЕНИЕ
        if active and active.get("uuid"):

            # Узнаём текущий трафик пользователя из RemnaWave
            user_data_resp = await client.get(
                f"{REMNA_API_URL}/{active['uuid']}",
                headers=headers
            )

            if user_data_resp.status_code != 200:
                raise Exception(f"Ошибка получения данных пользователя: {user_data_resp.text}")

            user_data = user_data_resp.json().get("response", {})
            current_limit = user_data.get("trafficLimitBytes", 0) or 0

            # Добавляем новый объём
            add_limit = traffic_limit_bytes
            new_limit = current_limit + add_limit

            # Продлеваем срок
            new_expire_dt = active["expire_date"] + timedelta(days=days)
            new_expire_str = new_expire_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

            # Готовим payload
            payload = {
                "uuid": active["uuid"],
                "username": active.get("username", base_username),
                "status": "ACTIVE",
                "expireAt": new_expire_str,
                "telegramId": tg_id,
                "email": f"{base_username}@special.remna",
                "description": f"Special {tariff_code}",
                "hwidDeviceLimit": hwid_limit,
                "activeInternalSquads": [SECOND_SQUAD_ID],
                "trafficLimitBytes": new_limit,
                "trafficLimitStrategy": "NO_RESET"
            }

            # PATCH в панель
            response = await client.patch(
                REMNA_API_URL,
                headers=headers,
                json=payload
            )

            if response.status_code not in (200, 201, 204):
                raise Exception(f"{response.status_code} - {response.text}")

            # Обновляем запись в БД
            await hp.add_or_extend_special_subscription(
                tg_id=tg_id,
                plan_name=tariff_code,
                days=days,
                amount=TARIFFS[tariff_code]["price"],
                uuid=active["uuid"]
            )

            short_uuid = await get_short_uuid_by_telegram_special(tg_id)

            return {
                "status": "extended",
                "expire_at": new_expire_str,
                "uuid": active["uuid"],
                "shortUuid": short_uuid
            }

        
        # СОЗДАНИЕ
        else:
            expire_at_dt = datetime.utcnow() + timedelta(days=days)
            expire_at_str = expire_at_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

            payload = {
                "username": base_username,
                "status": "ACTIVE",
                "expireAt": expire_at_str,
                "telegramId": tg_id,
                "email": f"{base_username}@special.remna",
                "hwidDeviceLimit": hwid_limit,
                "activeInternalSquads": [SECOND_SQUAD_ID],
                "description": f"Special {tariff_code}",
                "trafficLimitBytes": traffic_limit_bytes,
                "trafficLimitStrategy": "NO_RESET"
            }

            response = await client.post(REMNA_API_URL, headers=headers, json=payload)
            if response.status_code not in (200, 201):
                raise Exception(f"{response.status_code} - {response.text}")

            res_json = response.json().get("response", {})
            uuid = res_json.get("uuid")

            await hp.add_or_extend_special_subscription(
                tg_id=tg_id,
                plan_name=tariff_code,
                days=days,
                amount=TARIFFS[tariff_code]["price"],
                uuid=uuid
            )

            short_uuid = await get_short_uuid_by_telegram_special(tg_id)

            return {
                "status": "created",
                "username": base_username,
                "uuid": uuid,
                "shortUuid": short_uuid,
                "expire_at": expire_at_str
            }
        
async def create_multi_paid_user(tg_id: int, tariff_code: str, days: int, hwid_limit: int):
    safe_tariff_code = re.sub(r'[^A-Za-z0-9_-]', '_', tariff_code)
    base_username = f"multi_{tg_id}_{safe_tariff_code}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
    }

    # Берём лимит по тарифу
    traffic_limit_bytes = MULTI_TRAFFIC_LIMITS.get(tariff_code, 0)  # 0 = безлимит

    # Проверяем активную спец-подписку
    active = await hp.get_active_multi_subscription(tg_id)

    async with httpx.AsyncClient(timeout=30) as client:

        #  ПРОДЛЕНИЕ
        if active and active.get("uuid"):

            # Узнаём текущий трафик пользователя из RemnaWave
            user_data_resp = await client.get(
                f"{REMNA_API_URL}/{active['uuid']}",
                headers=headers
            )

            if user_data_resp.status_code != 200:
                raise Exception(f"Ошибка получения данных пользователя: {user_data_resp.text}")

            user_data = user_data_resp.json().get("response", {})
            current_limit = user_data.get("trafficLimitBytes", 0) or 0

            # Добавляем новый объём
            add_limit = traffic_limit_bytes
            new_limit = current_limit + add_limit

            # Продлеваем срок
            new_expire_dt = active["expire_date"] + timedelta(days=days)
            new_expire_str = new_expire_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

            # Готовим payload
            payload = {
                "uuid": active["uuid"],
                "username": active.get("username", base_username),
                "status": "ACTIVE",
                "expireAt": new_expire_str,
                "telegramId": tg_id,
                "email": f"{base_username}@multi.remna",
                "description": f"Multi {tariff_code}",
                "hwidDeviceLimit": hwid_limit,
                "activeInternalSquads": [SQUAD_ID_TRIAL],
                "trafficLimitBytes": new_limit,
                "trafficLimitStrategy": "NO_RESET"
            }

            # PATCH в панель
            response = await client.patch(
                REMNA_API_URL,
                headers=headers,
                json=payload
            )

            if response.status_code not in (200, 201, 204):
                raise Exception(f"{response.status_code} - {response.text}")

            # Обновляем запись в БД
            await hp.add_or_extend_multi_subscription(
                tg_id=tg_id,
                plan_name=tariff_code,
                days=days,
                amount=TARIFFS[tariff_code]["price"],
                uuid=active["uuid"]
            )

            short_uuid = await get_short_uuid_by_telegram_multi(tg_id)

            return {
                "status": "extended",
                "expire_at": new_expire_str,
                "uuid": active["uuid"],
                "shortUuid": short_uuid
            }

        
        # СОЗДАНИЕ
        else:
            expire_at_dt = datetime.utcnow() + timedelta(days=days)
            expire_at_str = expire_at_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

            payload = {
                "username": base_username,
                "status": "ACTIVE",
                "expireAt": expire_at_str,
                "telegramId": tg_id,
                "email": f"{base_username}@special.remna",
                "hwidDeviceLimit": hwid_limit,
                "activeInternalSquads": [SQUAD_ID_TRIAL],
                "description": f"Multi {tariff_code}",
                "trafficLimitBytes": traffic_limit_bytes,
                "trafficLimitStrategy": "NO_RESET"
            }

            response = await client.post(REMNA_API_URL, headers=headers, json=payload)
            if response.status_code not in (200, 201):
                raise Exception(f"{response.status_code} - {response.text}")

            res_json = response.json().get("response", {})
            uuid = res_json.get("uuid")

            await hp.add_or_extend_multi_subscription(
                tg_id=tg_id,
                plan_name=tariff_code,
                days=days,
                amount=TARIFFS[tariff_code]["price"],
                uuid=uuid
            )

            short_uuid = await get_short_uuid_by_telegram_multi(tg_id)

            return {
                "status": "created",
                "username": base_username,
                "uuid": uuid,
                "shortUuid": short_uuid,
                "expire_at": expire_at_str
            }

# Возвращает информацию о пользователе Remnawave по Telegram ID или None
async def get_user_by_telegram_id(telegram_id: int) -> dict | None:
    users = []
    page = 1

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            r = await client.get(
                REMNA_API_URL,
                params={"page": page, "size": 100},
                headers={"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}
            )

            if r.status_code != 200:
                break

            resp = r.json().get("response", {})
            page_users = resp.get("users", [])

            if not page_users:
                break

            # фильтруем ТОЛЬКО нужного пользователя
            users.extend(
                u for u in page_users
                if u.get("telegramId") == telegram_id
            )

            if len(page_users) < 100:
                break

            page += 1

    if not users:
        return None

    # ⚠️ ВАЖНО: возвращаем структуру, которую ожидает профиль
    return {
        "users": users
    }

async def get_hwid_devices(user_uuid: str) -> dict:
    url = f"{REMNAWAVE_BASE_URL}/hwid/devices/{user_uuid}"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(
                url,
                headers={"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}
            )

            if r.status_code != 200:
                return {"total": 0, "devices": []}

            resp = r.json().get("response", {})

            return {
                "total": resp.get("total", 0),
                "devices": resp.get("devices", [])
            }

        except Exception:
            return {"total": 0, "devices": []}

# Получаем всех пользователей
async def get_all_users() -> List[Dict]:
    all_users = []
    page = 1
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            try:
                r = await client.get(
                    REMNA_API_URL,
                    params={"page": page, "size": 100},  # размер страницы
                    headers={"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}
                )
                r.raise_for_status()
                resp = r.json().get("response", {})
                users = resp.get("users", [])
                if not users:
                    break  # пользователей больше нет
                all_users.extend(
                    [u for u in users if isinstance(u, dict) and u.get("uuid")]
                )
                # если вернулось меньше 100 — значит, достигли конца
                if len(users) < 100:
                    break
                page += 1
            except httpx.HTTPError as e:
                break
            except Exception as e:
                break
    return all_users

# Удаление пользователя
async def delete_user(uuid: str):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.delete(
            f"{REMNA_API_URL}/{uuid}",
            headers={"Authorization": f"Bearer {REMNAWAVE_TOKEN}"}
        )
    return r.status_code == 204

# Универсальная функция обновления подписки через REMNA API
async def update_subscription_expire(uuid: str, new_expire):
    payload = {
        "uuid": uuid,
        "expireAt": new_expire.isoformat(),
        "status": "ACTIVE"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.patch(
            REMNA_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
            },
            json=payload
        )

    return r

# Добавление дней в подписку
async def apply_rp_days(tg_id: int):
    data = await hp.check_paid_subscription_and_days(tg_id)
    if not data:
        return {"status": "invalid"}

    days_to_add = int(data["balance"])
    new_expire = data["expire_date"] + timedelta(days=days_to_add)

    # PATCH на REMNA
    r = await update_subscription_expire(data["uuid"], new_expire)
    if r.status_code not in (200, 201, 204):
        return {"status": "api_error", "details": r.text}

    # Обновление базы
    ok = await hp.update_paid_subscription_with_rp_days(tg_id)
    if not ok:
        return {"status": "db_error"}

    return {"status": "success", "new_expire": new_expire}

# Добавление гигов в подписку
async def apply_rp_gb(tg_id: int):
    data = await hp.check_special_subscription_and_gb(tg_id)
    if not data:
        return {"status": "invalid"}

    uuid = data["uuid"]
    add_gb = float(data["balance"])
    add_bytes = int(add_gb * 1024 * 1024 * 1024)  # GB → bytes

    async with httpx.AsyncClient(timeout=30) as client:
        # Получаем текущий трафик
        user_data_resp = await client.get(f"{REMNA_API_URL}/{uuid}", headers={
            "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
        })

        if user_data_resp.status_code != 200:
            return {"status": "api_error", "details": user_data_resp.text}

        user_data = user_data_resp.json().get("response", {})
        current_limit = user_data.get("trafficLimitBytes", 0) or 0

        # Добавляем новый объём
        new_limit = current_limit + add_bytes

        # PATCH обновления лимита
        r = await client.patch(
            REMNA_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {REMNAWAVE_TOKEN}"
            },
            json={
                "uuid": uuid,
                "trafficLimitBytes": new_limit,
                "status": "ACTIVE"
            }
        )

    if r.status_code not in (200, 201, 204):
        return {"status": "api_error", "details": r.text}

    # Обновление базы — уменьшаем баланс GB
    ok = await hp.update_special_subscription_after_gb_apply(tg_id, add_gb)
    if not ok:
        return {"status": "db_error"}

    return {"status": "success", "added_gb": add_gb}
