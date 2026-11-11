import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from db import close_db, connect_db
from handlers import orders, products, start
from middleware import mymidleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(products.router)
    dp.include_router(orders.router)
    dp.message.middleware(mymidleware())
    dp.callback_query.middleware(mymidleware())
    try:
        await connect_db()
        await bot.delete_webhook(drop_pending_updates=False)
        logging.info("Bot started.")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    except Exception:
        logging.exception("Bot stopped unexpectedly.")
    finally:
        await close_db()
        await bot.session.close()
        logging.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
