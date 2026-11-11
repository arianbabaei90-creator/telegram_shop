import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from db import get_products
from keyboards import main_menu, product_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("products:"))
async def show_products(callback: CallbackQuery):
    try:
        index = int(callback.data.split(":")[1])
        products = await get_products()

        if not products:
            await callback.message.answer("در حال حاضر محصولی موجود نیست.")
            await callback.answer()
            return

        if not 0 <= index < len(products):
            await callback.answer("صفحه موردنظر وجود ندارد.", show_alert=True)
            return

        product = products[index]
        text = (
            f"🛍 {product['name']}\n\n"
            f"💰 قیمت: {product['price']:,} تومان\n\n"
            f"{product['description'] or ''}\n\n"
            f"📦 محصول {index + 1} از {len(products)}"
        )
        keyboard = product_keyboard(
            product_id=product["id"],
            index=index,
            total=len(products),
        )

        if product["image_url"]:
            await callback.message.answer_photo(
                photo=product["image_url"],
                caption=text,
                reply_markup=keyboard,
            )
        else:
            await callback.message.answer(
                text=text,
                reply_markup=keyboard,
            )

        await callback.answer()
    except Exception:
        logger.exception("Product pagination failed.")
        await callback.answer(
            "خطایی در نمایش محصول رخ داد.",
            show_alert=True,
        )


@router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    try:
        await callback.message.answer(
            "منوی اصلی:",
            reply_markup=main_menu(),
        )
        await callback.answer()
    except Exception:
        logger.exception("Failed to return to menu.")
        await callback.answer("خطایی رخ داد.", show_alert=True)
