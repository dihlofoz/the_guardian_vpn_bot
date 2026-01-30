import uuid
import yookassa
from yookassa import Payment
from config import SECRET_KEY, ACCOUNT_ID

# Настраиваем SDK
yookassa.Configuration.account_id = ACCOUNT_ID
yookassa.Configuration.secret_key = SECRET_KEY


def create_invoice(amount: float, tg_id: int, tariff_code: str, return_url: str):
    """
    Создаёт инвойс на оплату в YooKassa и возвращает (url, id)
    Пользователь сможет сам выбрать способ оплаты.
    """
    idempotence_key = str(uuid.uuid4())
    email= "no-email@example.com"

    description = f"Оплата тарифа {tariff_code}"
    metadata = {
        "chat_id": tg_id,
        "tariff_code": tariff_code
    }

    try:
        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            # Убираем "payment_method_data", чтобы пользователь выбирал сам
            "confirmation": {
                "type": "redirect",
                "return_url": return_url  # куда вернётся пользователь после оплаты
            },
            "capture": True,
            "metadata": metadata,
            "description": description,
            "receipt": {
                "customer": {
                    "email": email
                }, 
                "items": [
                    {
                        "description": description,
                        "quantity": "1",
                        "amount": {
                            "value": f"{amount:.2f}",
                            "currency": "RUB"
                        },
                        "vat_code": "1",
                        "payment_mode": "full_prepayment",
                        "payment_subject": "service"
                    }
                ]
            }
        }, idempotence_key)

        return payment.confirmation.confirmation_url, payment.id

    except Exception as e:
        print(f"❌ Ошибка при создании платежа в YooKassa: {e}")
        return None, None

def create_add_device_invoice(
    amount: float,
    tg_id: int,
    old_limit: int,
    new_limit: int,
    return_url: str
):
    idempotence_key = str(uuid.uuid4())
    email = "no-email@example.com"

    description = f"Добавление устройств: {old_limit} → {new_limit}"

    metadata = {
        "chat_id": tg_id,
        "action": "add_device",
        "old_limit": old_limit,
        "new_limit": new_limit
    }

    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": description,
                "metadata": metadata,
                "receipt": {
                    "customer": {"email": email},
                    "items": [
                        {
                            "description": description,
                            "quantity": "1",
                            "amount": {
                                "value": f"{amount:.2f}",
                                "currency": "RUB"
                            },
                            "vat_code": "1",
                            "payment_mode": "full_prepayment",
                            "payment_subject": "service"
                        }
                    ]
                }
            },
            idempotence_key
        )

        return payment.confirmation.confirmation_url, payment.id

    except Exception as e:
        print(f"❌ YooKassa create error: {e}")
        return None, None


def check_payment(payment_id: str) -> bool:
    """
    Проверяет, оплачен ли инвойс
    """
    try:
        payment = Payment.find_one(payment_id)
        return payment.status == "succeeded"
    except Exception as e:
        print(f"⚠️ Ошибка при проверке платежа: {e}")
        return False