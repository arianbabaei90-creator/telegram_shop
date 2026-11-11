import logging
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from db import create_order, get_product
from keyboards import cancel_keyboard, contact_keyboard, remove_keyboard
from states import OrderState

router = Router()
logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r"^09\d{9}$")


@router.callback_query(F.data.startswith("order:"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    try:
        product_id = int(callback.data.split(":")[1])
        product = await get_product(product_id)

        

        await state.clear()
        await state.update_data(product_id=product_id)
        await state.set_state(OrderState.waiting_for_name)

        await callback.message.answer(
            "👤 لطفاً نام و نام خانوادگی خودت رو وارد کن.",
            reply_markup=cancel_keyboard(),
        )
        await callback.answer()
    except Exception:
        logger.exception("Failed to start order.")
        await callback.answer("خطایی رخ داد.", show_alert=True)


@router.message(OrderState.waiting_for_name, F.text)
async def get_customer_name(message: Message, state: FSMContext):
    if message.text == "❌ لغو سفارش":
        await state.clear()
        await message.answer("سفارش لغو شد.", reply_markup=remove_keyboard())
        return

    name = message.text.strip()
    if len(name) < 3 or len(name) > 200:
        await message.answer("لطفاً نام و نام خانوادگی معتبر وارد کن.")
        return

    await state.update_data(customer_name=name)
    await state.set_state(OrderState.waiting_for_address)
    await message.answer("📍 لطفاً آدرس دقیق خودت رو وارد کن.")


@router.message(OrderState.waiting_for_address, F.text)
async def get_address(message: Message, state: FSMContext):
    if message.text == "❌ لغو سفارش":
        await state.clear()
        await message.answer("سفارش لغو شد.", reply_markup=remove_keyboard())
        return

    address = message.text.strip()
    if len(address) < 10 or len(address) > 2000:
        await message.answer("لطفاً آدرس دقیق‌تری وارد کن.")
        return

    await state.update_data(address=address)
    await state.set_state(OrderState.waiting_for_phone)
    await message.answer(
        "📱 لطفاً شماره تماس خودت رو ارسال کن.\n"
        "شماره باید با 09 شروع بشه و 11 رقم باشه.\n"
        "یا از دکمه ارسال شماره تماس استفاده کن.",
        reply_markup=contact_keyboard(),
    )


@router.message(OrderState.waiting_for_phone, F.contact)
async def get_phone_from_contact(message: Message, state: FSMContext):
    contact = message.contact

    if contact.user_id != message.from_user.id:
        await message.answer("لطفاً شماره تماس خودت رو ارسال کن.")
        return

    phone = contact.phone_number
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    elif phone.startswith("98") and len(phone) == 12:
        phone = "0" + phone[2:]

    if not PHONE_REGEX.fullmatch(phone):
        await message.answer(
            "شماره تماس معتبر نیست. شماره‌ای با فرمت 09xxxxxxxxx ارسال کن."
        )
        return

    await finish_order(message, state, phone)


@router.message(OrderState.waiting_for_phone, F.text)
async def get_phone_manually(message: Message, state: FSMContext):
    if message.text == "❌ لغو سفارش":
        await state.clear()
        await message.answer("سفارش لغو شد.", reply_markup=remove_keyboard())
        return

    phone = message.text.strip()
    if not PHONE_REGEX.fullmatch(phone):
        await message.answer(
            "شماره تماس معتبر نیست.\n"
            "شماره باید 11 رقم و با 09 شروع شود.\n"
            "مثال: 09123456789"
        )
        return

    await finish_order(message, state, phone)


async def finish_order(message: Message, state: FSMContext, phone: str):
    try:
        data = await state.get_data()
        order = await create_order(
            user_id=message.from_user.id,
            product_id=data["product_id"],
            customer_name=data["customer_name"],
            address=data["address"],
            phone=phone,
        )

        if order is None:
            await state.clear()
            await message.answer(
                "متأسفانه این محصول دیگر موجود نیست.",
                reply_markup=remove_keyboard(),
            )
            return

        invoice = (
            f"🛒 سفارش جدید\n\n"
            f"🆔 شماره سفارش: {order['id']}\n"
            f"📦 محصول: {order['product_name']}\n"
            f"💰 قیمت: {order['product_price']:,} تومان\n\n"
            f"👤 مشتری: {order['customer_name']}\n"
            f"📍 آدرس: {order['address']}\n"
            f"📱 تلفن: {order['phone']}\n\n"
            f"🆔 Telegram ID: {order['user_id']}"
        )

        # The order is already persisted if sending this notification fails.
        await message.bot.send_message(chat_id=ADMIN_ID, text=invoice)

        await state.clear()
        await message.answer(
            "✅ سفارش شما با موفقیت ثبت شد.\n"
            f"شماره سفارش: {order['id']}\n"
            "به‌زودی با شما تماس گرفته خواهد شد.",
            reply_markup=remove_keyboard(),
        )
    except Exception:
        logger.exception("Failed to finish order.")
        await message.answer(
            "در ثبت یا اطلاع‌رسانی سفارش خطایی رخ داد. "
            "اگر سفارش ثبت شده باشد، مدیر فروشگاه آن را بررسی می‌کند.",
            reply_markup=remove_keyboard(),
        )
