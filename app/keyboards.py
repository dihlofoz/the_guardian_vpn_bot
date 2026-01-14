from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='VPN🚀', callback_data='connectvpn'), 
    InlineKeyboardButton(text='Профиль👤', callback_data='profile'),
    InlineKeyboardButton(text='Помощь💬', callback_data='help')],
    [InlineKeyboardButton(text='🧬 Реферальная программа', callback_data='referral')],
    [InlineKeyboardButton(text='ℹ️ О нас', callback_data='info'),
    InlineKeyboardButton(text='📢 Канал', url='https://t.me/grdVPNnews')]
])

vpn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎟 Пробный период', callback_data='trysub')],
    [InlineKeyboardButton(text='💳 Купить тариф', callback_data='tarif')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

help = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📖 Инструкция + F.A.Q.', url='https://telegra.ph/Instrukciya--FAQ-10-27')],
    [InlineKeyboardButton(text='✉️ Написать в поддержку', url='https://t.me/suppgrdvpn')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

back1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='← Назад', callback_data='back_main4')]
])

back_conversion_step_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_amount_choice")]
])

ref = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Конвертировать RP', callback_data='start_conversion')],
    [InlineKeyboardButton(text='⚙️ Модернизировать подписку', callback_data='updatesub')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

updatesub = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Базовый VPN 🪴', callback_data='basevpn'),
    InlineKeyboardButton(text='Обход Whitelists 🥷', callback_data='obhodwl')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main5')]
])

back_to_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏠 Вернуться на старт', callback_data='back_main2')]
])

choose_amount_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="← Назад", callback_data="back_updatesub")]
])

sub = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔑 Получить ключ', callback_data='key')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main1')]
])

tarifs = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Базовый VPN 🪴", callback_data="tariffs_basic"), 
    InlineKeyboardButton(text="Обход Whitelists 🥷", callback_data="tariffs_special")],
    [InlineKeyboardButton(text="← Назад", callback_data="back_main1")]
])

tariffs_b = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍼 1 месяц - 139₽', callback_data='1 месяц')],
    [InlineKeyboardButton(text='⚡️ 3 месяца - 389₽', callback_data='3 месяца')],
    [InlineKeyboardButton(text='🦾 6 месяцев - 749₽', callback_data='6 месяцев')],
    [InlineKeyboardButton(text='🪖 9 месяцев - 1109₽', callback_data='9 месяцев')], 
    [InlineKeyboardButton(text='💎 12 месяцев - 1449₽', callback_data='12 месяцев')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3')]
])

tariffs_s = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍼 7 дней - 75₽', callback_data='7 дней (25 GB)')],
    [InlineKeyboardButton(text='⚡️ 14 дней - 135₽', callback_data='14 дней (50 GB)')],
    [InlineKeyboardButton(text='💎 30 дней - 215₽', callback_data='30 дней (100 GB)')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3')]
])

continue_btn_new = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👉 Продолжить", callback_data="continue_new")]
])

continue_btn_existing = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👉 Продолжить", callback_data="continue_existing")]
])

agree_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Соглашаюсь", callback_data="agree")]
])

infokey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝Условия использования', url='https://telegra.ph/Pravila-ispolzovaniya-10-18')],
    [InlineKeyboardButton(text='📝Политика конфиденциальности', url='https://telegra.ph/Politika-konfidencialnosti-10-18-58')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

def payment_methods(tariff_code: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🛡 RP', callback_data=f'pay:rp:{tariff_code}')],
        [InlineKeyboardButton(text="💳 ЮKassa", callback_data=f'pay:yoo:{tariff_code}')],
        [InlineKeyboardButton(text="💰 CryptoBot", callback_data=f'pay:crypto:{tariff_code}')],
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_tariffs_b")]
    ])

def payment_methods_special(tariff_code: str): 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🛡 RP', callback_data=f'pay:rp:{tariff_code}')],
        [InlineKeyboardButton(text="💳 ЮKassa", callback_data=f'pay:yoo:{tariff_code}')],
        [InlineKeyboardButton(text="💰 CryptoBot", callback_data=f'pay:crypto:{tariff_code}')],
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_tariffs_s")]
    ])

def invoice_keyboard(url: str, invoice_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Оплатить", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check:crypto:{invoice_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
    ])

def yookassa_invoice_keyboard(url: str, payment_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить через Юkassa", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check:yookassa:{payment_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_yookassa")]
    ])

def rp_confirm_keyboard(tariff_code: str, rp_amount: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Подтвердить оплату ({rp_amount} RP)", callback_data=f"check:rp:{tariff_code}:{rp_amount}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_rp")]
    ])

mailing =  InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Отправить', callback_data='mailing_send')],
    [InlineKeyboardButton(text='❌ Отмена', callback_data='mailing_cancel')]
])

mailing1 =  InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌ Отмена', callback_data='mailing_cancel')]
])

promo_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Скидка", callback_data="promo_type_discount"),
    InlineKeyboardButton(text="🎁 RP", callback_data="promo_type_bonus")],
    [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
])

cancel =  InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
])

profile_logic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎁 Активировать промокод', callback_data='activate_promo')],
    [InlineKeyboardButton(text='💳 Продлить подписку', callback_data='prodlenie')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

subscribe_check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/grdVPNnews")],
    [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")]
])

# Кнопки выбора ресурса
convert_resource_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏳ Дни", callback_data="convert_days"),
     InlineKeyboardButton(text="🌐 Гигабайты", callback_data="convert_gb")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_conversion")]
])

# Кнопки выбора количества
def convert_amount_kb(max_amount: int, min_amount: int = 2):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⬇️ Мин ({min_amount} RP)", callback_data=f"amount_min"),
         InlineKeyboardButton(text=f"⬆️ Макс ({max_amount} RP)", callback_data=f"amount_max")],
        [InlineKeyboardButton(text="↕️ Частично", callback_data="amount_partial")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_conversion")]
    ])

# Клавиатуры уведомлений об истёкших подписках
expired_trial_kb =  InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Оформить подписку", callback_data="prodlenie")]
])

expired_paid_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻ Продлить подписку", callback_data="prodlenie")]
])

expired_special_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Продлить подписку", callback_data="prodlenie")]
])
