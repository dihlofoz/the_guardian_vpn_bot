import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.tasks import cleanup as cl
from app.tasks import cleanup_paid as cl_p
from app.tasks import cleanup_special as cl_sp
from app.tasks import expired_subscription_notifier as e_s
from app.tasks import trial_reminder as t_r_t
from logger_config import setup_logger

logger = setup_logger("bot.log")

# ⚙️ Импортируем SQLAlchemy engine и Base
from app.db.dealer import engine, Base

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔹 Создание таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized successfully!")

async def main():
    await init_db()
    dp.include_router(router)
    asyncio.create_task(cl.cleanup_expired_trials())
    asyncio.create_task(cl_p.cleanup_expired_paid())
    asyncio.create_task(cl_sp.cleanup_expired_special())
    asyncio.create_task(t_r_t.trial_reminder_task())
    asyncio.create_task(e_s.expired_subscriptions_notifier1())
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('🚪 Exit')


    
