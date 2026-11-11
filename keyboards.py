from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🛍 مشاهده محصولات",
                callback_data="products:0",
            )]
        ]
    )


def product_keyboard(product_id: int, index: int, total: int):
    buttons = []
    navigation = []

    if index > 0:
        navigation.append(InlineKeyboardButton(
            text="⬅️ قبلی",
            callback_data=f"products:{index - 1}",
        ))
    if index < total - 1:
        navigation.append(InlineKeyboardButton(
            text="بعدی ➡️",
            callback_data=f"products:{index + 1}",
        ))

    if navigation:
        buttons.append(navigation)

    buttons.append([InlineKeyboardButton(
        text="🛒 ثبت سفارش",
        callback_data=f"order:{product_id}",
    )])
    buttons.append([InlineKeyboardButton(
        text="🏠 منوی اصلی",
        callback_data="menu",
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text="📱 ارسال شماره تماس",
            request_contact=True,
        )]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ لغو سفارش")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard():
    return ReplyKeyboardRemove()
