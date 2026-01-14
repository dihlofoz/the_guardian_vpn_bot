import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import DATABASE_URL
from app.db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db")

# Асинхронный engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Асинхронный sessionmaker
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    try:
        logger.info("🔄 Проверка подключения к PostgreSQL...")
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Соединение с базой установлено")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("📦 Таблицы проверены/созданы")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации базы данных: {e}")
        raise e
