import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from logger_config import setup_logger
from app.db.dealer import engine, Base
from app.scheduler import setup_scheduler, shutdown_scheduler

logger = setup_logger("bot.log")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized successfully!")

async def main():
    await init_db()
    dp.include_router(router)
    setup_scheduler(bot)

    try:
        await dp.start_polling(bot)
    finally:
        shutdown_scheduler(bot)
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚪 Exit")