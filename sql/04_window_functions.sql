
-- QUERY 1: Repeat customer analysis
-- Using ROW_NUMBER and COUNT OVER

WITH customer_orders AS (

    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,

        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id
            ORDER BY
                o.order_purchase_timestamp DESC,
                o.order_id DESC
        ) AS order_rank,

        COUNT(*) OVER (
            PARTITION BY c.customer_unique_id
        ) AS total_delivered_orders

    FROM orders AS o

    INNER JOIN customers AS c
        ON o.customer_id = c.customer_id

    WHERE o.order_status = 'delivered'

)

SELECT
    customer_unique_id,
    total_delivered_orders,
    order_purchase_timestamp AS latest_purchase_date

FROM customer_orders

WHERE order_rank = 1
AND total_delivered_orders >= 2

ORDER BY
    total_delivered_orders DESC,
    latest_purchase_date DESC

LIMIT 10;



-- QUERY 2: Rank states by merchandise value
-- Using the RANK window function

WITH state_sales AS (

    SELECT
        c.customer_state,

        COUNT(DISTINCT o.order_id) AS delivered_orders,

        SUM(oi.price) AS merchandise_value

    FROM order_items AS oi

    INNER JOIN orders AS o
        ON oi.order_id = o.order_id

    INNER JOIN customers AS c
        ON o.customer_id = c.customer_id

    WHERE o.order_status = 'delivered'

    GROUP BY c.customer_state

),

ranked_states AS (

    SELECT
        customer_state,
        delivered_orders,
        merchandise_value,

        RANK() OVER (
            ORDER BY merchandise_value DESC
        ) AS sales_rank

    FROM state_sales

)

SELECT
    sales_rank,
    customer_state,
    delivered_orders,

    ROUND(
        merchandise_value, 2
    ) AS merchandise_value_brl

FROM ranked_states

ORDER BY sales_rank, customer_state

LIMIT 10;



-- QUERY 3: Monthly merchandise value growth
-- Using the LAG window function

WITH monthly_sales AS (

    SELECT
        strftime(
            '%Y-%m',
            o.order_purchase_timestamp
        ) AS purchase_month,

        SUM(oi.price) AS merchandise_value

    FROM order_items AS oi

    INNER JOIN orders AS o
        ON oi.order_id = o.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY
        strftime(
            '%Y-%m',
            o.order_purchase_timestamp
        )

),

monthly_comparison AS (

    SELECT
        purchase_month,
        merchandise_value,

        LAG(purchase_month) OVER (
            ORDER BY purchase_month
        ) AS previous_month,

        LAG(merchandise_value) OVER (
            ORDER BY purchase_month
        ) AS previous_month_value

    FROM monthly_sales

)

SELECT
    purchase_month,

    ROUND(
        merchandise_value, 2
    ) AS current_month_brl,

    ROUND(
        previous_month_value, 2
    ) AS previous_month_brl,

    CASE
        WHEN previous_month_value > 0
        AND previous_month = strftime(
            '%Y-%m',
            date(purchase_month || '-01', '-1 month')
        )

        THEN ROUND(
            (
                merchandise_value -
                previous_month_value
            ) * 100.0 / previous_month_value,
            2
        )

        ELSE NULL
    END AS mom_growth_percent

FROM monthly_comparison

WHERE purchase_month BETWEEN '2017-02' AND '2018-07'

ORDER BY purchase_month;
