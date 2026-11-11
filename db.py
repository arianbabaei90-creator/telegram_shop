import logging

import asyncpg

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)
pool: asyncpg.Pool | None = None


async def connect_db():
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=1,
            max_size=10,
            command_timeout=30,
        )
        logger.info("Database connection pool created.")
    except Exception:
        logger.exception("Failed to connect to database.")
        raise


async def close_db():
    global pool
    if pool is not None:
        await pool.close()
        pool = None
        logger.info("Database connection pool closed.")


def get_pool() -> asyncpg.Pool:
    if pool is None:
        raise RuntimeError("Database pool is not initialized.")
    return pool


async def get_products():
    try:
        return await get_pool().fetch(
            """
            SELECT id, name, description, price, image_url
            FROM products
            WHERE is_active = TRUE
            ORDER BY id
            """
        )
    except Exception:
        logger.exception("Failed to fetch products.")
        raise


async def get_product(product_id: int):
    try:
        return await get_pool().fetchrow(
            """
            SELECT id, name, description, price, image_url
            FROM products
            WHERE id = $1 AND is_active = TRUE
            """,
            product_id,
        )
    except Exception:
        logger.exception("Failed to fetch product %s", product_id)
        raise


async def create_order(
    user_id: int,
    product_id: int,
    customer_name: str,
    address: str,
    phone: str,
):
    try:
        async with get_pool().acquire() as connection:
            async with connection.transaction():
                product = await connection.fetchrow(
                    """
                    SELECT id, name, price
                    FROM products
                    WHERE id = $1 AND is_active = TRUE
                    FOR SHARE
                    """,
                    product_id,
                )
                if product is None:
                    return None

                order = await connection.fetchrow(
                    """
                    INSERT INTO orders (
                        user_id, product_id, product_name, product_price,
                        customer_name, address, phone
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id, created_at
                    """,
                    user_id,
                    product["id"],
                    product["name"],
                    product["price"],
                    customer_name,
                    address,
                    phone,
                )

                return {
                    "id": order["id"],
                    "created_at": order["created_at"],
                    "product_name": product["name"],
                    "product_price": product["price"],
                    "customer_name": customer_name,
                    "address": address,
                    "phone": phone,
                    "user_id": user_id,
                }
    except Exception:
        logger.exception("Failed to create order.")
        raise
