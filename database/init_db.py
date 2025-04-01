from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy import BigInteger, JSON

import os
from dotenv import load_dotenv


load_dotenv()

engine = create_async_engine(os.getenv('DB_PATH'))
async_session = async_sessionmaker(bind=engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    achievements: Mapped[dict] = mapped_column(JSON)

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
