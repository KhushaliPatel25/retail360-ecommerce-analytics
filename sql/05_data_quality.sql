
-- ===========================================
-- RETAIL360 - SQL DATA QUALITY VALIDATION
-- ===========================================


-- QUERY 1: Check duplicate primary keys

SELECT
    'Orders' AS table_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT order_id) AS unique_ids,
    COUNT(*) - COUNT(DISTINCT order_id)
        AS duplicate_or_missing_ids
FROM orders

UNION ALL

SELECT
    'Customers',
    COUNT(*),
    COUNT(DISTINCT customer_id),
    COUNT(*) - COUNT(DISTINCT customer_id)
FROM customers

UNION ALL

SELECT
    'Products',
    COUNT(*),
    COUNT(DISTINCT product_id),
    COUNT(*) - COUNT(DISTINCT product_id)
FROM products

UNION ALL

SELECT
    'Sellers',
    COUNT(*),
    COUNT(DISTINCT seller_id),
    COUNT(*) - COUNT(DISTINCT seller_id)
FROM sellers;


-- QUERY 2: Find unmatched relationships

SELECT
    'Order Items to Orders' AS relationship,
    COUNT(*) AS unmatched_records
FROM order_items AS oi
LEFT JOIN orders AS o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL

UNION ALL

SELECT
    'Orders to Customers',
    COUNT(*)
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT
    'Order Items to Products',
    COUNT(*)
FROM order_items AS oi
LEFT JOIN products AS p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'Order Items to Sellers',
    COUNT(*)
FROM order_items AS oi
LEFT JOIN sellers AS s
    ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL

UNION ALL

SELECT
    'Payments to Orders',
    COUNT(*)
FROM payments AS p
LEFT JOIN orders AS o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL;


-- QUERY 3: Identify JOIN multiplication risk

WITH item_counts AS (

    SELECT
        order_id,
        COUNT(*) AS item_records

    FROM order_items
    GROUP BY order_id

),

payment_counts AS (

    SELECT
        order_id,
        COUNT(*) AS payment_records

    FROM payments
    GROUP BY order_id

)

SELECT
    COUNT(*) AS orders_with_items_and_payments,

    SUM(
        CASE
            WHEN item_records > 1
              OR payment_records > 1
            THEN 1
            ELSE 0
        END
    ) AS orders_with_multiple_join_rows,

    SUM(
        CASE
            WHEN item_records > 1
             AND payment_records > 1
            THEN 1
            ELSE 0
        END
    ) AS orders_with_both_multiple,

    MAX(
        item_records * payment_records
    ) AS maximum_join_rows_per_order

FROM item_counts AS i

INNER JOIN payment_counts AS p
    ON i.order_id = p.order_id;


-- QUERY 4: Investigate missing timestamps

SELECT
    order_status,

    COUNT(*) AS total_orders,

    SUM(
        CASE
            WHEN order_approved_at IS NULL
            THEN 1
            ELSE 0
        END
    ) AS missing_approval_dates,

    SUM(
        CASE
            WHEN order_delivered_customer_date IS NULL
            THEN 1
            ELSE 0
        END
    ) AS missing_delivery_dates

FROM orders

GROUP BY order_status

ORDER BY total_orders DESC;
