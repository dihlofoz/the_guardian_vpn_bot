from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='VPN 🚀', callback_data='connectvpn'), 
    InlineKeyboardButton(text='Профиль 👤', callback_data='profile'),
    InlineKeyboardButton(text='Помощь 💬', callback_data='help')],
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
    [InlineKeyboardButton(text='📖 F.A.Q.', url='https://telegra.ph/Instrukciya--FAQ-10-27')],
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
    [
        InlineKeyboardButton(
            text='Базовый VPN 🪴',
            callback_data='rp:upgrade:base'
        ),
        InlineKeyboardButton(
            text='Обход Whitelists 🥷',
            callback_data='rp:upgrade:bypass'
        )
    ],
    [
        InlineKeyboardButton(
            text='Мульти VPN 💥',
            callback_data='rp:upgrade:multi'
        )
    ],
    [
        InlineKeyboardButton(
            text='← Назад',
            callback_data='back_main5'
        )
    ]
])


def rp_resource_choice_kb(sub_type: str):
    buttons = []

    if sub_type in ("bypass", "multi"):
        buttons.append(
            InlineKeyboardButton(
                text="➕ Добавить дни",
                callback_data="rp:add:days"
            )
        )
        buttons.append(
            InlineKeyboardButton(
                text="➕ Добавить ГБ",
                callback_data="rp:add:gb"
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons,
            [InlineKeyboardButton(text="← Назад", callback_data="modernback")]
        ]
    )

rp_amount_back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад", callback_data="rp:amount:back")]
    ])

back_to_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏠 Вернуться на старт', callback_data='back_main2')]
])

def subscription_result_keyboard(sub_link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔗 Подключить VPN",
                url=sub_link
            )
        ],
        [
            InlineKeyboardButton(
                text='🏠 Вернуться на старт',
                callback_data='back_main2'
            )
        ]
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
    [InlineKeyboardButton(text='Мульти VPN 💥', callback_data='tariffs_multi')],
    [InlineKeyboardButton(text="← Назад", callback_data="back_main1"),
    InlineKeyboardButton(text='🏠 На старт', callback_data='back_main2')]
])

tariffs_b = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍼 1 месяц - 109₽', callback_data='1 месяц')],
    [InlineKeyboardButton(text='⚡️ 3 месяца - 319₽', callback_data='3 месяца')],
    [InlineKeyboardButton(text='🦾 6 месяцев - 689₽', callback_data='6 месяцев')],
    [InlineKeyboardButton(text='🪖 9 месяцев - 1049₽', callback_data='9 месяцев')], 
    [InlineKeyboardButton(text='💎 12 месяцев - 1369₽', callback_data='12 месяцев')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3'),
    InlineKeyboardButton(text='🏠 На старт', callback_data='back_main2')]
])

tariffs_s = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍼 7 дней - 59₽', callback_data='7 дней (50 GB)')],
    [InlineKeyboardButton(text='⚡️ 14 дней - 99₽', callback_data='14 дней (100 GB)')],
    [InlineKeyboardButton(text='💎 30 дней - 169₽', callback_data='30 дней (200 GB)')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3'),
    InlineKeyboardButton(text='🏠 На старт', callback_data='back_main2')]
])

tariffs_m = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍼 1 месяц - 209₽', callback_data='1 месяц (300 GB)')],
    [InlineKeyboardButton(text='⚡️ 3 месяца - 589₽', callback_data='3 месяца (900 GB)')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3'),
    InlineKeyboardButton(text='🏠 На старт', callback_data='back_main2')]
])

continue_btn_new = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить →", callback_data="continue_new")]
])

continue_btn_existing = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить →", callback_data="continue_existing")]
])

agree_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Соглашаюсь", callback_data="agree")]
])

infokey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝Условия использования', url='https://telegra.ph/Pravila-ispolzovaniya-10-18')],
    [InlineKeyboardButton(text='📝Политика конфиденциальности', url='https://telegra.ph/Politika-konfidencialnosti-10-18-58')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

def payment_methods(invoice: dict):
    tariff_code = invoice['tariff_code']
    user_id = invoice['user_id']

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 ЮKassa", callback_data=f'pay:yoo:{tariff_code}'),
        InlineKeyboardButton(text="🪙 CryptoBot", callback_data=f'pay:crypto:{tariff_code}')],
        [InlineKeyboardButton(text='🛡 RP (Referral Points)', callback_data=f'pay:rp:{tariff_code}')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data=f'cancel:{user_id}')],
    ])

def invoice_keyboard(url: str, invoice_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Оплатить", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check:crypto:{invoice_id}")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:payment_methods"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
    ])

def yookassa_invoice_keyboard(url: str, payment_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить через Юkassa", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check:yookassa:{payment_id}")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:payment_methods"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_yookassa")]
    ])

def rp_confirm_keyboard(tariff_code: str, rp_amount: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Подтвердить оплату ({rp_amount} RP)", callback_data=f"check:rp:{tariff_code}:{rp_amount}")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:payment_methods"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_rp")]
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
    [InlineKeyboardButton(text='⚙️ Панель управления подписками', callback_data='paneluprsubs')],
    [InlineKeyboardButton(text='🎁 Активировать промокод', callback_data='activate_promo')],
    [InlineKeyboardButton(text='💳 Продлить подписку', callback_data='prodlenie')],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

def manage_choose_tariff():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Базовый VPN 🪴", callback_data="manage:tariff:paid"),
        InlineKeyboardButton(text="Обход Whitelists 🥷", callback_data="manage:tariff:special")],
        [InlineKeyboardButton(text="Мульти VPN 💥", callback_data="manage:tariff:multi")],
        [InlineKeyboardButton(text="← Назад", callback_data="profile")]
    ])


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def manage_devices_keyboard(devices: list):
    kb = []

    if devices:
        for i, dev in enumerate(devices):
            model = dev.get("deviceModel") or "Unknown"
            platform = dev.get("platform") or "?"

            kb.append([
                InlineKeyboardButton(
                    text=f"{i+1}) ❌ {model} ({platform})",
                    callback_data=f"manage:dev:{i}"
                )
            ])
    else:
        kb.append([
            InlineKeyboardButton(
                text="Нет устройств ❌",
                callback_data="noop"
            )
        ])

    # ───── ДОБАВЛЕННЫЕ КНОПКИ ─────
    kb.append([InlineKeyboardButton(text="📱 Добавить устройство", callback_data="manage:add_device")])
    kb.append([InlineKeyboardButton(text="← Назад", callback_data="paneluprsubs")])

    return InlineKeyboardMarkup(inline_keyboard=kb)

def add_device_selector_keyboard(user_id: int, current: int, min_value: int, max_value: int, step: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➖",
                callback_data=f"adddev:{user_id}:set:{current - step}"
            ),
            InlineKeyboardButton(
                text=f"{current} 📱",
                callback_data="noop"
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=f"adddev:{user_id}:set:{current + step}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Продолжить →",
                callback_data=f"adddev:{user_id}:next"
            )
        ],
        [
            InlineKeyboardButton(
                text="← Назад",
                callback_data="adddev:back"
            )
        ]
    ])

def add_device_confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 ЮKassa",
                    callback_data="adddev:pay:yoo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪙 CryptoBot",
                    callback_data="adddev:pay:crypto"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛡 RP (Referral Points)",
                    callback_data="adddev:pay:rp"
                )
            ],
            [
                InlineKeyboardButton(
                    text="← Назад",
                    callback_data="adddev:back:selector"
                )
            ]
        ]
    )

def add_device_confirm_keyboard1(payment_url: str | None = None) -> InlineKeyboardMarkup:
    keyboard = []

    # Кнопка оплаты (URL из YooKassa)
    if payment_url:
        keyboard.append([
            InlineKeyboardButton(
                text="💳 Оплатить через Юkassa",
                url=payment_url
            )
        ])

    # Назад к селектору устройств
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="adddev:back"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def crypto_pay_keyboard(pay_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🪙 Оплатить через CryptoBot",
                url=pay_url
            )],
            [InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="adddev:back"
            )]
        ]
    )

def addev_rp_confirm_keyboard(amount_rp: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Подтвердить оплату ({amount_rp} RP)", callback_data=f"addev:rp:{amount_rp}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="adddev:back")]
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
def convert_amount_kb(max_amount: int, min_amount: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⬇️ Мин ({min_amount} RP)", callback_data=f"amount_min"),
         InlineKeyboardButton(text=f"⬆️ Макс", callback_data=f"amount_max")],
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


def devices_selector_keyboard(user_id: int, current: int, min_value: int, max_value: int, step: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➖",
                callback_data=f"devices:{user_id}:set:{current-step}"
            ),
            InlineKeyboardButton(
                text=f"{current} 📱",
                callback_data="devices:none"  # просто заглушка, не кликается
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=f"devices:{user_id}:set:{current+step}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Продолжить →",
                callback_data=f"devices:{user_id}:next"
            )
        ],
        [
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"back:tariffs"
            )
        ]
    ])

def confirm_zakaz_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm:{user_id}")],
        [InlineKeyboardButton(text="← Назад", callback_data="back:devices"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel:{user_id}")]
    ])

