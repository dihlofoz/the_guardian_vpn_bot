from aiogram import Bot
from config import ADMIN_CHANNEL_ID

async def notify_purchase(
    bot: Bot,
    tg_id: int,
    username: str,
    tariff_code: str,
    amount: int,
    discount: int | None,
    is_extension: bool,
    expire_at: str,
    paid_with_tokens: bool = False,
    paid_with_crypto: bool = False
):
    """Отправка уведомления о новой покупке/продлении в канал админов"""

    discount_text = f" (со скидкой -{discount}%)" if discount else ""
    type_text = "Продление" if is_extension else "Новая подписка"

    # ➜ Формируем сумму по типу оплаты
    if paid_with_tokens == True:
        amount_text = f"{amount} RP"
    elif paid_with_crypto == True:
        amount_text = f"{amount}${discount_text}"
    else:
        amount_text = f"{amount}₽{discount_text}"

    text = (
        f"-=+=- 🛒 <b>Новая покупка</b> -=+=-\n\n"
        f"<blockquote>👤 <b>@{username}</b> (ID: <code>{tg_id}</code>)\n"
        f"💎 Тариф: <b>{tariff_code}</b>\n"
        f"💰 Сумма: <b>{amount_text}</b>\n"
        f"🔁 Тип: <b>{type_text}</b>\n\n"
        f"📅 До: <b>{expire_at}</b></blockquote>"
    )

    try:
        await bot.send_message(ADMIN_CHANNEL_ID, text, parse_mode="HTML")
    except Exception as e:
        print("[NOTIFY ERROR]", e)