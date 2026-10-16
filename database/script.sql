CREATE SCHEMA IF NOT EXISTS analytics;


CREATE TABLE IF NOT EXISTS analytics.customers(
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics.products(
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(12, 2) NOT NULL
        CHECK (price >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics.orders(
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL
        REFERENCES analytics.customers(id),
    order_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(30) NOT NULL
        CHECK(
            status IN(
                'pending',
                'processing',
                'shipped',
                'delivered',
                'cancelled'
            )
        ),
    total_amount NUMERIC(12, 2) NOT NULL
        CHECK (total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS analytics.order_items(
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL
        REFERENCES analytics.orders(id),
    product_id BIGINT NOT NULL
        REFERENCES analytics.products(id),
    quantity INTEGER NOT NULL
        CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL
        CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS analytics.payments(
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES analytics.orders(id),
    payment_method VARCHAR(30) NOT NULL
        CHECK(
            payment_method IN(
                'credit_card',
                'debit_card',
                'paypal',
                'upi',
                'bank_transfer'
            )
        ),
    amount NUMERIC(12, 2) NOT NULL
        CHECK (amount >= 0),
    payment_status VARCHAR(30) NOT NULL
        CHECK(
            payment_status IN(
                'pending',
                'completed',
                'failed',
                'refunded'
            )
        ),
    paid_at TIMESTAMPTZ
);



CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON analytics.orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_order_date ON analytics.orders(order_date);

CREATE INDEX IF NOT EXISTS idx_orders_status ON analytics.orders(status);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON analytics.order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON analytics.order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_products_category ON analytics.products(category);

CREATE INDEX IF NOT EXISTS idx_customers_country ON analytics.customers(country);

CREATE INDEX IF NOT EXISTS idx_payments_order_id ON analytics.payments(order_id);



INSERT INTO analytics.customers(name, email, country, created_at) SELECT
    'Customer ' || gs,
    'customer' || gs || '@example.com',
    (
        ARRAY[
            'India',
            'United States',
            'United Kingdom',
            'Canada',
            'Australia',
            'Germany',
            'France',
            'Singapore',
            'Japan',
            'Brazil'
        ]
    )[1 + ((gs - 1) % 10)],
    TIMESTAMPTZ '2024-01-01 00:00:00+00' + ((gs * 13) % 700) * INTERVAL '1 day' FROM generate_series(1, 500) AS gs;



INSERT INTO analytics.products(name, category, price, created_at) VALUES
    ('MacBook Air M3', 'Laptops', 1099.00, '2024-01-10T10:00:00Z'),
    ('Dell XPS 15', 'Laptops', 1499.00, '2024-01-12T10:00:00Z'),
    ('Lenovo ThinkPad X1', 'Laptops', 1399.00, '2024-01-15T10:00:00Z'),
    ('HP Spectre x360', 'Laptops', 1299.00, '2024-01-18T10:00:00Z'),

    ('iPhone 15', 'Smartphones', 799.00, '2024-01-20T10:00:00Z'),
    ('Samsung Galaxy S24', 'Smartphones', 899.00, '2024-01-22T10:00:00Z'),
    ('Google Pixel 8', 'Smartphones', 699.00, '2024-01-25T10:00:00Z'),
    ('OnePlus 12', 'Smartphones', 749.00, '2024-01-28T10:00:00Z'),

    ('iPad Air', 'Tablets', 599.00, '2024-02-01T10:00:00Z'),
    ('Samsung Galaxy Tab S9', 'Tablets', 799.00, '2024-02-03T10:00:00Z'),
    ('Microsoft Surface Pro', 'Tablets', 999.00, '2024-02-05T10:00:00Z'),

    ('AirPods Pro', 'Audio', 249.00, '2024-02-10T10:00:00Z'),
    ('Sony WH-1000XM5', 'Audio', 399.00, '2024-02-12T10:00:00Z'),
    ('Bose QuietComfort', 'Audio', 349.00, '2024-02-15T10:00:00Z'),
    ('JBL Live 660NC', 'Audio', 199.00, '2024-02-18T10:00:00Z'),

    ('Logitech MX Master 3S', 'Accessories', 99.00, '2024-03-01T10:00:00Z'),
    ('Keychron K2', 'Accessories', 89.00, '2024-03-03T10:00:00Z'),
    ('Anker USB-C Hub', 'Accessories', 49.00, '2024-03-05T10:00:00Z'),
    ('Logitech MX Keys', 'Accessories', 119.00, '2024-03-07T10:00:00Z'),

    ('LG UltraGear Monitor', 'Monitors', 449.00, '2024-03-10T10:00:00Z'),
    ('Dell UltraSharp Monitor', 'Monitors', 599.00, '2024-03-12T10:00:00Z'),
    ('Samsung Odyssey G7', 'Monitors', 699.00, '2024-03-15T10:00:00Z'),

    ('Kindle Paperwhite', 'E-Readers', 149.00, '2024-04-01T10:00:00Z'),
    ('Nintendo Switch OLED', 'Gaming', 349.00, '2024-04-05T10:00:00Z'),
    ('PlayStation 5', 'Gaming', 499.00, '2024-04-10T10:00:00Z'),
    ('Xbox Series X', 'Gaming', 499.00, '2024-04-15T10:00:00Z');



-- initial will be 0, then populate it using order_items
INSERT INTO analytics.orders(customer_id, order_date, status, total_amount) SELECT 1 + ((gs - 1) % 500),
    TIMESTAMPTZ '2024-01-01 00:00:00+00' + ((gs * 17) % 1000) * INTERVAL '1 day' + ((gs * 37) % 24) * INTERVAL '1 hour' + ((gs * 11) % 60) * INTERVAL '1 minute',
    CASE
        WHEN gs % 20 = 0 THEN 'cancelled'
        WHEN gs % 15 = 0 THEN 'pending'
        WHEN gs % 10 = 0 THEN 'processing'
        WHEN gs % 7 = 0 THEN 'shipped'
        ELSE 'delivered'
    END,
    0
FROM generate_series(1, 1000) AS gs;



-- every order receives between 1 and 4 items
-- unit_price is copied from the product price
-- order totals can be calculated directly from order_items
INSERT INTO analytics.order_items(order_id, product_id, quantity, unit_price) SELECT o.id, p.id, 1 + ((o.id + item_number) % 3), p.price FROM analytics.orders AS o
CROSS JOIN LATERAL generate_series(1, 1 + (o.id % 4)) AS items(item_number)
JOIN analytics.products AS p ON p.id = 1 + ((o.id * 7 + items.item_number * 3) % 25);


-- calculate order totals
UPDATE analytics.orders AS o SET total_amount = totals.total FROM(
    SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS total
    FROM analytics.order_items
    GROUP BY order_id
) AS totals
WHERE o.id = totals.order_id;


-- payments
INSERT INTO analytics.payments(order_id, payment_method, amount, payment_status, paid_at) SELECT o.id,
    CASE
        WHEN o.id % 5 = 0 THEN 'credit_card'
        WHEN o.id % 5 = 1 THEN 'debit_card'
        WHEN o.id % 5 = 2 THEN 'paypal'
        WHEN o.id % 5 = 3 THEN 'upi'
        ELSE 'bank_transfer'
    END,

    o.total_amount,
    CASE
        WHEN o.status = 'cancelled' THEN 'refunded'
        WHEN o.status = 'pending' THEN 'pending'
        WHEN o.id % 23 = 0 THEN 'failed'
        ELSE 'completed'
    END,

    CASE
        WHEN o.status = 'pending' THEN NULL
        ELSE o.order_date + INTERVAL '1 hour'
    END
FROM analytics.orders AS o;


ANALYZE analytics.customers;
ANALYZE analytics.products;
ANALYZE analytics.orders;
ANALYZE analytics.order_items;
ANALYZE analytics.payments;