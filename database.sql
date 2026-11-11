CREATE TABLE IF NOT EXISTS products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price BIGINT NOT NULL CHECK (price >= 0),
    image_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    product_name VARCHAR(200) NOT NULL,
    product_price BIGINT NOT NULL CHECK (product_price >= 0),
    customer_name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(11) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);

-- Sample products (replace image URLs with real image URLs):
INSERT INTO products (name, description, price, image_url)
VALUES
('هدفون بلوتوثی', 'هدفون با کیفیت صدای مناسب', 1500000, 'https://example.com/headphone.jpg'),
('ماوس گیمینگ', 'ماوس مناسب بازی و کار', 850000, 'https://example.com/mouse.jpg'),
('کیبورد مکانیکی', 'کیبورد مکانیکی با نورپردازی', 3200000, 'https://example.com/keyboard.jpg');
