# Telegram Shop Bot

A starter Telegram shop bot using Python 3, aiogram 3, PostgreSQL, and asyncpg.

## Features
- Main menu and product catalog
- Product pagination
- Deep links such as `https://t.me/YourBotName?start=item_1`
- FSM checkout: name, address, phone
- Contact sharing and manual phone validation
- PostgreSQL order persistence
- Admin invoice notification

## Setup
1. Create a PostgreSQL database named `telegram_shop`.
2. Run `database.sql` against that database.
3. Copy `.env.example` to `.env` and fill in your bot token, admin ID, and database credentials.
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python main.py`

## Notes
- `MemoryStorage` loses FSM state after bot restart. Use Redis for a production deployment.
- Sample product image URLs in `database.sql` are placeholders; replace them with valid image URLs.
- Orders are saved before the admin notification is sent. A notification failure does not undo the database order.
