
-- QUERY 1: Count orders by status

SELECT
    order_status,
    COUNT(*) AS total_orders
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;


-- QUERY 2: Count orders by purchase year

SELECT
    strftime('%Y', order_purchase_timestamp) AS purchase_year,
    COUNT(*) AS total_orders
FROM orders
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY strftime('%Y', order_purchase_timestamp)
ORDER BY purchase_year;


-- QUERY 3: Analyze recorded payment amounts

SELECT
    payment_type,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS unique_orders,
    ROUND(SUM(payment_value), 2) AS total_payment_value_brl
FROM payments
GROUP BY payment_type
ORDER BY total_payment_value_brl DESC;


-- QUERY 4: Count orders containing multiple items

SELECT
    COUNT(*) AS multi_item_orders
FROM (
    SELECT
        order_id
    FROM order_items
    GROUP BY order_id
    HAVING COUNT(*) > 1
) AS multi_item_summary;
