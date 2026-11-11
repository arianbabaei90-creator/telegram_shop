import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from db import get_product
from keyboards import main_menu, product_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message):
    try:
        parts = (message.text or "").split(maxsplit=1)
        payload = parts[1] if len(parts) > 1 else ""

        if payload.startswith("item_"):
            try:
                product_id = int(payload.removeprefix("item_"))
                if product_id <= 0:
                    raise ValueError
            except ValueError:
                await message.answer("لینک محصول معتبر نیست.")
                return

            product = await get_product(product_id)
            if product is None:
                await message.answer("این محصول در دسترس نیست.")
                return

            text = (
                f"🛍 {product['name']}\n\n"
                f"💰 قیمت: {product['price']:,} تومان\n\n"
                f"{product['description'] or ''}"
            )
            await message.answer(
                text=text,
                reply_markup=product_keyboard(
                    product_id=product["id"],
                    index=0,
                    total=1,
                ),
            )
            return

        await message.answer(
            "سلام! 👋\n\nبه فروشگاه ما خوش اومدی.\n"
            "برای مشاهده محصولات روی دکمه زیر بزن.",
            reply_markup=main_menu(),
        )
    except Exception:
        logger.exception("Start handler failed.")
        await message.answer("خطایی رخ داد. لطفاً دوباره تلاش کن.")
