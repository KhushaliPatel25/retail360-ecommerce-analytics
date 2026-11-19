
-- ===============================================
-- RETAIL360 - SQL REPORTING VIEWS
-- ===============================================

-- Remove previous versions of these views
-- so the script can be run again.

DROP VIEW IF EXISTS vw_monthly_delivered_sales;
DROP VIEW IF EXISTS vw_item_sales;
DROP VIEW IF EXISTS vw_order_summary;


-- ===============================================
-- VIEW 1: ORDER SUMMARY
-- One row per order
-- ===============================================

CREATE VIEW vw_order_summary AS

WITH item_totals AS (

    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS merchandise_value_brl,
        SUM(freight_value) AS freight_value_brl

    FROM order_items
    GROUP BY order_id

),

payment_totals AS (

    SELECT
        order_id,
        COUNT(*) AS payment_count,
        SUM(payment_value) AS payment_value_brl

    FROM payments
    GROUP BY order_id

)

SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    COALESCE(i.item_count, 0)
        AS item_count,

    COALESCE(i.merchandise_value_brl, 0)
        AS merchandise_value_brl,

    COALESCE(i.freight_value_brl, 0)
        AS freight_value_brl,

    COALESCE(p.payment_count, 0)
        AS payment_count,

    COALESCE(p.payment_value_brl, 0)
        AS payment_value_brl,

    CASE
        WHEN i.order_id IS NOT NULL THEN 1
        ELSE 0
    END AS has_item_records

FROM orders AS o

LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id

LEFT JOIN item_totals AS i
    ON o.order_id = i.order_id

LEFT JOIN payment_totals AS p
    ON o.order_id = p.order_id;


-- ===============================================
-- VIEW 2: ITEM SALES
-- One row per order-item record
-- ===============================================

CREATE VIEW vw_item_sales AS

SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,

    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    o.order_status,
    o.order_purchase_timestamp,

    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS product_category,

    oi.price AS item_price_brl,
    oi.freight_value AS item_freight_brl

FROM order_items AS oi

LEFT JOIN orders AS o
    ON oi.order_id = o.order_id

LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id

LEFT JOIN products AS p
    ON oi.product_id = p.product_id

LEFT JOIN category_translation AS t
    ON p.product_category_name =
       t.product_category_name;


-- ===============================================
-- VIEW 3: MONTHLY DELIVERED SALES
-- One row per purchase month
-- ===============================================

CREATE VIEW vw_monthly_delivered_sales AS

SELECT
    SUBSTR(
        order_purchase_timestamp, 1, 7
    ) AS purchase_month,

    COUNT(*) AS delivered_orders,

    SUM(item_count) AS items_sold,

    ROUND(
        SUM(merchandise_value_brl), 2
    ) AS merchandise_value_brl,

    ROUND(
        SUM(freight_value_brl), 2
    ) AS freight_value_brl,

    ROUND(
        AVG(merchandise_value_brl), 2
    ) AS avg_merchandise_per_order_brl

FROM vw_order_summary

WHERE order_status = 'delivered'
AND item_count > 0
AND order_purchase_timestamp IS NOT NULL

GROUP BY
    SUBSTR(order_purchase_timestamp, 1, 7);
