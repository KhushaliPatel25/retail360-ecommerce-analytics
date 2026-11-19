
-- QUERY 1: Combine Orders and Customers
-- Display five customer orders with locations

SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_city,
    c.customer_state
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
LIMIT 5;


-- QUERY 2: Top 10 states by delivered orders

SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS delivered_orders
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY delivered_orders DESC
LIMIT 10;


-- QUERY 3: Delivered merchandise value
-- Join Orders with Order Items

SELECT
    COUNT(DISTINCT o.order_id) AS delivered_orders_with_items,
    COUNT(*) AS item_records,
    ROUND(SUM(oi.price), 2) AS merchandise_value_brl,
    ROUND(SUM(oi.freight_value), 2) AS freight_value_brl
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered';


-- QUERY 4: Top 10 product categories
-- Connect Orders, Order Items, Products,
-- and Category Translation

SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    COUNT(*) AS items_sold,
    COUNT(DISTINCT o.order_id) AS unique_orders,
    ROUND(SUM(oi.price), 2) AS merchandise_value_brl
FROM order_items AS oi
INNER JOIN orders AS o
    ON oi.order_id = o.order_id
LEFT JOIN products AS p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation AS t
    ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )
ORDER BY merchandise_value_brl DESC
LIMIT 10;


-- QUERY 5: Find orders without item records
-- Demonstrate LEFT JOIN

SELECT
    COUNT(DISTINCT o.order_id) AS orders_without_items
FROM orders AS o
LEFT JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE oi.order_id IS NULL;
