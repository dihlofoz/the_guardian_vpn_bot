import requests
import os
from config import CRYPTOBOT_TOKEN
from config import BASE_URL
import aiohttp
import json

HEADERS = {
    "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
    "Content-Type": "application/json"
}

def create_invoice(amount_usd: float, tg_id: int, tariff_code: str):
    url = BASE_URL + "createInvoice"
    HEADERS = {
    "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
    "Content-Type": "application/json"
}
    data = {
        "asset": "USDT",
        "amount": amount_usd,
        "description": f"Оплата тарифа {tariff_code}",
    }

    try:
        r = requests.post(url, headers=HEADERS, json=data)
        resp = r.json()
    except Exception as e:
        return None

    if not resp.get("ok"):
        return None

    return resp["result"]  # содержит поля id, status, pay_url и т.д.

# 🔍 Проверка инвойса
def check_crypto_invoice(invoice_id: str):
    url = f"{BASE_URL}getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    params = {"invoice_ids": invoice_id}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data.get("ok") and data["result"]["items"]:
        invoice = data["result"]["items"][0]
        return invoice["status"] == "paid"
    return False

# Функция получения курса USD к RUB
async def get_usd_rate():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()  # читаем как текст
                data = json.loads(text)       # парсим вручную
                return float(data["Valute"]["USD"]["Value"])
    except Exception as e:
        print(f"⚠️ Не удалось получить курс USD: {e}")
        return 90.0  # fallback, если не удалось получить курс