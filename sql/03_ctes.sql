
-- QUERY 1: Calculate delivered order KPIs
-- using Common Table Expressions

WITH delivered_order_lines AS (

    SELECT
        oi.order_id,
        oi.price,
        oi.freight_value

    FROM order_items AS oi

    INNER JOIN orders AS o
        ON oi.order_id = o.order_id

    WHERE o.order_status = 'delivered'

),

order_totals AS (

    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS merchandise_value,
        SUM(freight_value) AS freight_value

    FROM delivered_order_lines

    GROUP BY order_id

)

SELECT
    COUNT(*) AS delivered_orders_with_items,

    SUM(item_count) AS delivered_item_records,

    ROUND(
        SUM(merchandise_value), 2
    ) AS total_merchandise_value_brl,

    ROUND(
        AVG(merchandise_value), 2
    ) AS avg_order_merchandise_brl

FROM order_totals;


-- QUERY 2: Top 10 customer states
-- by delivered merchandise value

WITH order_totals AS (

    SELECT
        oi.order_id,
        o.customer_id,
        SUM(oi.price) AS merchandise_value

    FROM order_items AS oi

    INNER JOIN orders AS o
        ON oi.order_id = o.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY
        oi.order_id,
        o.customer_id

),

state_performance AS (

    SELECT
        c.customer_state,

        COUNT(*) AS total_orders,

        SUM(
            ot.merchandise_value
        ) AS merchandise_value,

        AVG(
            ot.merchandise_value
        ) AS avg_order_value

    FROM order_totals AS ot

    INNER JOIN customers AS c
        ON ot.customer_id = c.customer_id

    GROUP BY c.customer_state

)

SELECT
    customer_state,

    total_orders,

    ROUND(
        merchandise_value, 2
    ) AS merchandise_value_brl,

    ROUND(
        avg_order_value, 2
    ) AS avg_order_value_brl

FROM state_performance

ORDER BY merchandise_value DESC

LIMIT 10;


-- QUERY 3: Customer repeat purchase analysis
-- using multiple CTEs

WITH delivered_customer_orders AS (

    SELECT
        c.customer_unique_id,
        o.order_id

    FROM orders AS o

    INNER JOIN customers AS c
        ON o.customer_id = c.customer_id

    WHERE o.order_status = 'delivered'

),

customer_frequency AS (

    SELECT
        customer_unique_id,

        COUNT(
            DISTINCT order_id
        ) AS delivered_order_count

    FROM delivered_customer_orders

    GROUP BY customer_unique_id

)

SELECT
    COUNT(*) AS unique_customers,

    SUM(
        CASE
            WHEN delivered_order_count = 1
            THEN 1
            ELSE 0
        END
    ) AS one_time_customers,

    SUM(
        CASE
            WHEN delivered_order_count >= 2
            THEN 1
            ELSE 0
        END
    ) AS repeat_customers,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN delivered_order_count >= 2
                THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_customer_rate_percent

FROM customer_frequency;
