from aiogram import Dispatcher
import asyncio

import logging

from core.bot import bot
from components.handlers import router
from database.init_db import init_database


logging.basicConfig(level=logging.INFO)

async def main():
    await init_database()
    
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
