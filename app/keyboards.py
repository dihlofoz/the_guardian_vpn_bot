from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='VPN', callback_data='connectvpn', icon_custom_emoji_id=5188481279963715781), 
    InlineKeyboardButton(text='Профиль', callback_data='profile', icon_custom_emoji_id=5373012449597335010),
    InlineKeyboardButton(text='Помощь', callback_data='help', icon_custom_emoji_id=5465300082628763143)],
    [InlineKeyboardButton(text='Реферальная программа', callback_data='referral', icon_custom_emoji_id=5355270175920763448)],
    [InlineKeyboardButton(text='О нас', callback_data='info', icon_custom_emoji_id=5334544901428229844),
    InlineKeyboardButton(text='Канал', url='https://t.me/grdVPNnews', icon_custom_emoji_id=5424818078833715060)]
])

vpn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пробный период', callback_data='trysub', icon_custom_emoji_id=5377599075237502153)],
    [InlineKeyboardButton(text='Купить тариф', callback_data='tarif', icon_custom_emoji_id=5445353829304387411)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

help = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='F.A.Q.', url='https://telegra.ph/Instrukciya--FAQ-10-27', icon_custom_emoji_id=5226512880362332956)],
    [InlineKeyboardButton(text='Написать в поддержку', url='https://t.me/suppgrdvpn', icon_custom_emoji_id=5253742260054409879)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

back1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='← Назад', callback_data='back_main4')]
])

back_conversion_step_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_amount_choice")]
])

ref = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Конвертировать RP', callback_data='start_conversion', icon_custom_emoji_id=5264727218734524899)],
    [InlineKeyboardButton(text='Модернизировать подписку', callback_data='updatesub', icon_custom_emoji_id=5341715473882955310)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

updatesub = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Базовый VPN',
            callback_data='rp:upgrade:base',
            icon_custom_emoji_id=5278428495121248059
        ),
        InlineKeyboardButton(
            text='Обход Whitelists',
            callback_data='rp:upgrade:bypass',
            icon_custom_emoji_id=5420266513011579594
        )
    ],
    [
        InlineKeyboardButton(
            text='Мульти VPN',
            callback_data='rp:upgrade:multi',
            icon_custom_emoji_id=5276032951342088188
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
    [InlineKeyboardButton(text="Базовый VPN", callback_data="tariffs_basic", icon_custom_emoji_id=5278428495121248059), 
    InlineKeyboardButton(text="Обход Whitelists", callback_data="tariffs_special", icon_custom_emoji_id=5420266513011579594)],
    [InlineKeyboardButton(text='Мульти VPN', callback_data='tariffs_multi', icon_custom_emoji_id=5276032951342088188)],
    [InlineKeyboardButton(text="← Назад", callback_data="back_main1"),
    InlineKeyboardButton(text='На старт', callback_data='back_main2', icon_custom_emoji_id=5465226866321268133)]
])

tariffs_b = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 месяц - 109₽', callback_data='1 месяц', icon_custom_emoji_id=5411128690916467494)],
    [InlineKeyboardButton(text='3 месяца - 319₽', callback_data='3 месяца', icon_custom_emoji_id=5431449001532594346)],
    [InlineKeyboardButton(text='6 месяцев - 689₽', callback_data='6 месяцев', icon_custom_emoji_id=5386766919154016047)],
    [InlineKeyboardButton(text='9 месяцев - 1049₽', callback_data='9 месяцев', icon_custom_emoji_id=5433787452311484697)], 
    [InlineKeyboardButton(text='12 месяцев - 1369₽', callback_data='12 месяцев', icon_custom_emoji_id=5427168083074628963)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3'),
    InlineKeyboardButton(text='На старт', callback_data='back_main2', icon_custom_emoji_id=5465226866321268133)]
])

tariffs_s = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='7 дней - 59₽', callback_data='7 дней (50 GB)', icon_custom_emoji_id=5411128690916467494)],
    [InlineKeyboardButton(text='14 дней - 99₽', callback_data='14 дней (100 GB)', icon_custom_emoji_id=5431449001532594346)],
    [InlineKeyboardButton(text='30 дней - 169₽', callback_data='30 дней (200 GB)', icon_custom_emoji_id=5427168083074628963)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3'),
    InlineKeyboardButton(text='На старт', callback_data='back_main2', icon_custom_emoji_id=5465226866321268133)]
])

tariffs_m = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 месяц - 209₽', callback_data='1 месяц (300 GB)', icon_custom_emoji_id=5411128690916467494)],
    [InlineKeyboardButton(text='3 месяца - 589₽', callback_data='3 месяца (900 GB)', icon_custom_emoji_id=5431449001532594346)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main3'),
    InlineKeyboardButton(text='На старт', callback_data='back_main2', icon_custom_emoji_id=5465226866321268133)]
])

continue_btn_new = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить →", callback_data="continue_new")]
])

continue_btn_existing = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить →", callback_data="continue_existing")]
])

agree_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Соглашаюсь", callback_data="agree", icon_custom_emoji_id=5206607081334906820)]
])

infokey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Условия использования', url='https://telegra.ph/Pravila-ispolzovaniya-10-18', icon_custom_emoji_id=5334882760735598374)],
    [InlineKeyboardButton(text='Политика конфиденциальности', url='https://telegra.ph/Politika-konfidencialnosti-10-18-58', icon_custom_emoji_id=5334882760735598374)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

def payment_methods(invoice: dict):
    tariff_code = invoice['tariff_code']
    user_id = invoice['user_id']

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ЮKassa", callback_data=f'pay:yoo:{tariff_code}', icon_custom_emoji_id=5445353829304387411),
        InlineKeyboardButton(text="CryptoBot", callback_data=f'pay:crypto:{tariff_code}', icon_custom_emoji_id=5199552030615558774)],
        [InlineKeyboardButton(text='RP (Referral Points)', callback_data=f'pay:rp:{tariff_code}', icon_custom_emoji_id=5775979247814318159)],
        [InlineKeyboardButton(text='Отмена', callback_data=f'cancel:{user_id}', icon_custom_emoji_id=5210952531676504517)],
    ])

def invoice_keyboard(url: str, invoice_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить через CryptoBot", url=url, icon_custom_emoji_id=5199552030615558774)],
        [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check:crypto:{invoice_id}", icon_custom_emoji_id=5264727218734524899)],
        [InlineKeyboardButton(text="← Назад", callback_data="back:payment_methods"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel_payment", icon_custom_emoji_id=5210952531676504517)]
    ])

def yookassa_invoice_keyboard(url: str, payment_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить через Юkassa", url=url, icon_custom_emoji_id=5445353829304387411)],
        [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check:yookassa:{payment_id}", icon_custom_emoji_id=5264727218734524899)],
        [InlineKeyboardButton(text="← Назад", callback_data="back:payment_methods"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel_yookassa", icon_custom_emoji_id=5210952531676504517)]
    ])

def rp_confirm_keyboard(tariff_code: str, rp_amount: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Подтвердить оплату ({rp_amount} RP)", callback_data=f"check:rp:{tariff_code}:{rp_amount}", icon_custom_emoji_id=5206607081334906820)],
        [InlineKeyboardButton(text="← Назад", callback_data="back:payment_methods"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel_rp", icon_custom_emoji_id=5210952531676504517)]
    ])

mailing =  InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить', callback_data='mailing_send', icon_custom_emoji_id=5206607081334906820)],
    [InlineKeyboardButton(text='Отмена', callback_data='mailing_cancel', icon_custom_emoji_id=5210952531676504517)]
])

mailing1 =  InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='mailing_cancel', icon_custom_emoji_id=5210952531676504517)]
])

promo_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Скидка", callback_data="promo_type_discount"),
    InlineKeyboardButton(text="🎁 RP", callback_data="promo_type_bonus")],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel', icon_custom_emoji_id=5210952531676504517)]
])

cancel =  InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel', icon_custom_emoji_id=5210952531676504517)]
])

profile_logic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Панель управления подписками', callback_data='paneluprsubs', icon_custom_emoji_id=5341715473882955310)],
    [InlineKeyboardButton(text='Активировать промокод', callback_data='activate_promo', icon_custom_emoji_id=5203996991054432397)],
    [InlineKeyboardButton(text='Продлить подписку', callback_data='prodlenie', icon_custom_emoji_id=5445353829304387411)],
    [InlineKeyboardButton(text='← Назад', callback_data='back_main')]
])

def manage_choose_tariff():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Базовый VPN", callback_data="manage:tariff:paid", icon_custom_emoji_id=5278428495121248059),
        InlineKeyboardButton(text="Обход Whitelists", callback_data="manage:tariff:special", icon_custom_emoji_id=5420266513011579594)],
        [InlineKeyboardButton(text="Мульти VPN", callback_data="manage:tariff:multi", icon_custom_emoji_id=5276032951342088188)],
        [InlineKeyboardButton(text="← Назад", callback_data="profile")]
    ])

def manage_devices_keyboard(devices: list):
    kb = []

    if devices:
        for i, dev in enumerate(devices):
            model = dev.get("deviceModel") or "Unknown"
            platform = dev.get("platform") or "?"

            kb.append([
                InlineKeyboardButton(
                    text=f"{model} ({platform})",
                    callback_data=f"manage:dev:{i}",
                    icon_custom_emoji_id=5210952531676504517
                )
            ])
    else:
        kb.append([
            InlineKeyboardButton(
                text="Нет устройств",
                callback_data="noop",
                icon_custom_emoji_id=5210952531676504517
            )
        ])

    # ───── ДОБАВЛЕННЫЕ КНОПКИ ─────
    kb.append([InlineKeyboardButton(text="Добавить устройство", callback_data="manage:add_device", icon_custom_emoji_id=5407025283456835913)])
    kb.append([InlineKeyboardButton(text="← Назад", callback_data="paneluprsubs")])

    return InlineKeyboardMarkup(inline_keyboard=kb)

def add_device_selector_keyboard(user_id: int, current: int, min_value: int, max_value: int, step: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⠀",
                callback_data=f"adddev:{user_id}:set:{current - step}",
                icon_custom_emoji_id=5229113891081956317
            ),
            InlineKeyboardButton(
                text=f"{current}",
                callback_data="noop",
                icon_custom_emoji_id=5407025283456835913
            ),
            InlineKeyboardButton(
                text="⠀",
                callback_data=f"adddev:{user_id}:set:{current + step}",
                icon_custom_emoji_id=5226945370684140473
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
            [InlineKeyboardButton(text="ЮKassa", callback_data="adddev:pay:yoo", icon_custom_emoji_id=5445353829304387411),
            InlineKeyboardButton(text="CryptoBot", callback_data="adddev:pay:crypto", icon_custom_emoji_id=5199552030615558774)],
            [InlineKeyboardButton(text="RP (Referral Points)", callback_data="adddev:pay:rp", icon_custom_emoji_id=5775979247814318159)],
            [InlineKeyboardButton(text="← Назад", callback_data="adddev:back:selector")]
        ])

def add_device_confirm_keyboard1(payment_url: str | None = None) -> InlineKeyboardMarkup:
    keyboard = []

    # Кнопка оплаты (URL из YooKassa)
    if payment_url:
        keyboard.append([
            InlineKeyboardButton(
                text="Оплатить через Юkassa",
                url=payment_url,
                icon_custom_emoji_id=5445353829304387411
            )
        ])

    # Назад к селектору устройств
    keyboard.append([
        InlineKeyboardButton(
            text="Отмена",
            callback_data="adddev:back",
            icon_custom_emoji_id=5210952531676504517
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def crypto_pay_keyboard(pay_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Оплатить через CryptoBot",
                url=pay_url,
                icon_custom_emoji_id=5199552030615558774
            )],
            [InlineKeyboardButton(
                text="Отмена",
                callback_data="adddev:back",
                icon_custom_emoji_id=5210952531676504517
            )]
        ]
    )

def addev_rp_confirm_keyboard(amount_rp: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Подтвердить оплату ({amount_rp} RP)", callback_data=f"addev:rp:{amount_rp}", icon_custom_emoji_id=5206607081334906820)],
        [InlineKeyboardButton(text="Отмена", callback_data="adddev:back", icon_custom_emoji_id=5210952531676504517)]
    ])

subscribe_check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/grdVPNnews", icon_custom_emoji_id=5424818078833715060)],
    [InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription", icon_custom_emoji_id=5206607081334906820)]
])

# Кнопки выбора ресурса
convert_resource_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Дни", callback_data="convert_days", icon_custom_emoji_id=5431897022456145283),
     InlineKeyboardButton(text="Гигабайты", callback_data="convert_gb", icon_custom_emoji_id=5447410659077661506)],
    [InlineKeyboardButton(text="Отмена", callback_data="cancel_conversion", icon_custom_emoji_id=5210952531676504517)]
])

# Кнопки выбора количества
def convert_amount_kb(max_amount: int, min_amount: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Мин ({min_amount} RP)", callback_data=f"amount_min", icon_custom_emoji_id=5436016445848831807),
         InlineKeyboardButton(text=f"Макс", callback_data=f"amount_max", icon_custom_emoji_id=5435891415055878798)],
        [InlineKeyboardButton(text="Частично", callback_data="amount_partial", icon_custom_emoji_id=5334673106202010226)],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_conversion", icon_custom_emoji_id=5210952531676504517)]
    ])

# Клавиатуры уведомлений об истёкших подписках
expired_trial_kb =  InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оформить подписку", callback_data="tarif", icon_custom_emoji_id=5427168083074628963)]
])

expired_paid_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продлить подписку", callback_data="prodlenie", icon_custom_emoji_id=5974235702701853774)]
])

expired_special_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продлить подписку", callback_data="prodlenie", icon_custom_emoji_id=5974235702701853774)]
])


def devices_selector_keyboard(user_id: int, current: int, min_value: int, max_value: int, step: int = 1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⠀",
                callback_data=f"devices:{user_id}:set:{current-step}",
                icon_custom_emoji_id=5229113891081956317
            ),
            InlineKeyboardButton(
                text=f"{current}",
                callback_data="devices:none",
                icon_custom_emoji_id=5407025283456835913
            ),
            InlineKeyboardButton(
                text="⠀",
                callback_data=f"devices:{user_id}:set:{current+step}",
                icon_custom_emoji_id=5226945370684140473
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
        [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm:{user_id}", icon_custom_emoji_id=5206607081334906820)],
        [InlineKeyboardButton(text="← Назад", callback_data="back:devices"),
        InlineKeyboardButton(text="Отмена", callback_data=f"cancel:{user_id}", icon_custom_emoji_id=5210952531676504517)]
    ])

referral_notify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💫 Пригласить', callback_data='referral')]
])