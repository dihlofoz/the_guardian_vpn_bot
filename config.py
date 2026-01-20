TOKEN='8308366735:AAFtsNNNRI0QbNmRO-A_ZFHu1c_BX7qa_mk'
BOT_USERNAME="GrdVPNbot"
ADMIN_IDS=[5002578567, 1231937075]
CHANNEL_ID = "@grdVPNnews"
ADMIN_CHANNEL_ID = -1003512170455

# CryptoBot
CRYPTOBOT_TOKEN='476277:AAOitMZFLrFWGaVVrxlCr8NfoS7qdTyY6LO'
BASE_URL = "https://pay.crypt.bot/api/"

# Тарифы
TARIFFS = {
    "1 месяц": {
        "days": 30,
        "price": 139,
        "traffic": "∞ Безлимит"
    },
    "3 месяца": {
        "days": 91,
        "price": 389,
        "traffic": "∞ Безлимит"
    },
    "6 месяцев": {
        "days": 182,
        "price": 749,
        "traffic": "∞ Безлимит"
    },
    "9 месяцев": {
        "days": 273,
        "price": 1109,
        "traffic": "∞ Безлимит"
    },
    "12 месяцев": {
        "days": 365,
        "price": 1449,
        "traffic": "∞ Безлимит"
    },
    "7 дней (25 GB)": {
        "days": 7,
        "price": 75,
        "traffic": "25 GB"
    },
    "14 дней (50 GB)": {
        "days": 14,
        "price": 135,
        "traffic": "50 GB"
    },
    "30 дней (100 GB)": {
        "days": 30,
        "price": 215,
        "traffic": "100GB"
    },
    "1 месяц (300 GB)": {
        "days": 30,
        "price": 219,
        "traffic": "300GB"
    },
    "3 месяца (900 GB)": {
        "days": 91,
        "price": 639,
        "traffic": "900GB"
    }
}

TRIAL_DAYS = 2
TRIAL_TRAFFIC_GB = 30
TRIAL_TRAFFIC_BYTES = TRIAL_TRAFFIC_GB * 1024**3

SPECIAL_TRAFFIC_LIMITS = {
    "7 дней (25 GB)": 25 * 1024**3,
    "14 дней (50 GB)": 50 * 1024**3,
    "30 дней (100 GB)": 100 * 1024**3
}

MULTI_TRAFFIC_LIMITS = {
    "1 месяц (300 GB)": 300 * 1024**3,
    "3 месяца (900 GB)": 900 * 1024**3,
}

SPECIAL_TARIFFS = {
    "7 дней (25 GB)",
    "14 дней (50 GB)",
    "30 дней (100 GB)"
}

MULTI_TARIFFS = {
    "1 месяц (300 GB)",
    "3 месяца (900 GB)"
}

BASE_TARIFFS = {
    "1 месяц",
    "3 месяца",
    "6 месяцев",
    "9 месяцев",
    "12 месяцев"
}

# Юkassa
ACCOUNT_ID='1189888'
SECRET_KEY='test_2MphmmsqWsXlh7LmAOFNre32HNr6pov9V8ZenYkB-L0'
BASE_URL_YOO = "https://api.yookassa.ru/v3/payments"

# Remnawave
REMNAWAVE_BASE_URL='https://panel.grdguard.xyz/api'
REMNAWAVE_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiODM1YmM4OGMtMTIwOS00NjhhLThlOTYtNzM2MDljNzRlMmFhIiwidXNlcm5hbWUiOm51bGwsInJvbGUiOiJBUEkiLCJpYXQiOjE3NjEyNDQ3NTEsImV4cCI6MTA0MDExNTgzNTF9.7t02VkJaycL2_ZRIG2fzspLMeaUDzZEcAu48PvQRn6U'
SQUAD_ID = '628f6873-1aae-4ce0-818b-8b2e2d96c308'
SECOND_SQUAD_ID = '81b30140-0d94-4a1c-b6b4-6a88b4e2fa4c'
SQUAD_ID_TRIAL = 'bfe69553-510e-4441-b4e4-ba9d5405f632'

DEFAULT_DEVICES = 1
DEFAULT_DEVICES = 1
DEVICES_MIN = 1
DEVICES_MAX = 5
DEVICES_STEP = 1

# База данных PostgreSQL
DATABASE_URL = "postgresql+asyncpg://vpn_user:Local4ti!@localhost:5432/vpn_bot_db"
