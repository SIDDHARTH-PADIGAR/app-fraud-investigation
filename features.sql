
-- Point-in-time transaction features.
-- All history windows exclude the current transaction and all future events.
-- Same-second events are excluded to avoid ambiguous event ordering.

CREATE OR REPLACE TABLE transaction_features AS

WITH inbound AS (
    SELECT
        transaction_id,
        receiver_id AS account_id,
        timestamp_s,
        amount_inr,

        COUNT(*) OVER (
            PARTITION BY receiver_id
            ORDER BY timestamp_s
            RANGE BETWEEN 86400 PRECEDING AND 1 PRECEDING
        ) AS incoming_count_24h,

        SUM(amount_inr) OVER (
            PARTITION BY receiver_id
            ORDER BY timestamp_s
            RANGE BETWEEN 86400 PRECEDING AND 1 PRECEDING
        ) AS incoming_amount_24h,

        COUNT(*) OVER (
            PARTITION BY receiver_id
            ORDER BY timestamp_s
            RANGE BETWEEN 604800 PRECEDING AND 1 PRECEDING
        ) AS incoming_count_7d,

        SUM(amount_inr) OVER (
            PARTITION BY receiver_id
            ORDER BY timestamp_s
            RANGE BETWEEN 604800 PRECEDING AND 1 PRECEDING
        ) AS incoming_amount_7d,

        COUNT(*) OVER (
            PARTITION BY receiver_id
            ORDER BY timestamp_s
            RANGE BETWEEN 2592000 PRECEDING AND 1 PRECEDING
        ) AS incoming_count_30d,

        SUM(amount_inr) OVER (
            PARTITION BY receiver_id
            ORDER BY timestamp_s
            RANGE BETWEEN 2592000 PRECEDING AND 1 PRECEDING
        ) AS incoming_amount_30d

    FROM transactions
),

outbound AS (
    SELECT
        transaction_id,
        sender_id AS account_id,
        timestamp_s,
        amount_inr,

        COUNT(*) OVER (
            PARTITION BY sender_id
            ORDER BY timestamp_s
            RANGE BETWEEN 86400 PRECEDING AND 1 PRECEDING
        ) AS outgoing_count_24h,

        SUM(amount_inr) OVER (
            PARTITION BY sender_id
            ORDER BY timestamp_s
            RANGE BETWEEN 86400 PRECEDING AND 1 PRECEDING
        ) AS outgoing_amount_24h,

        COUNT(*) OVER (
            PARTITION BY sender_id
            ORDER BY timestamp_s
            RANGE BETWEEN 604800 PRECEDING AND 1 PRECEDING
        ) AS outgoing_count_7d,

        SUM(amount_inr) OVER (
            PARTITION BY sender_id
            ORDER BY timestamp_s
            RANGE BETWEEN 604800 PRECEDING AND 1 PRECEDING
        ) AS outgoing_amount_7d,

        COUNT(*) OVER (
            PARTITION BY sender_id
            ORDER BY timestamp_s
            RANGE BETWEEN 2592000 PRECEDING AND 1 PRECEDING
        ) AS outgoing_count_30d,

        SUM(amount_inr) OVER (
            PARTITION BY sender_id
            ORDER BY timestamp_s
            RANGE BETWEEN 2592000 PRECEDING AND 1 PRECEDING
        ) AS outgoing_amount_30d

    FROM transactions
)

SELECT
    t.transaction_id,
    t.timestamp_s,
    t.day,
    t.sender_id,
    t.receiver_id,
    t.amount_inr,
    t.payment_type,
    t.channel,

    -- Receiver's historical incoming behaviour.
    COALESCE(i.incoming_count_24h, 0) AS receiver_incoming_count_24h,
    COALESCE(i.incoming_amount_24h, 0) AS receiver_incoming_amount_24h,
    COALESCE(i.incoming_count_7d, 0) AS receiver_incoming_count_7d,
    COALESCE(i.incoming_amount_7d, 0) AS receiver_incoming_amount_7d,
    COALESCE(i.incoming_count_30d, 0) AS receiver_incoming_count_30d,
    COALESCE(i.incoming_amount_30d, 0) AS receiver_incoming_amount_30d,

    -- Sender's historical outgoing behaviour.
    COALESCE(o.outgoing_count_24h, 0) AS sender_outgoing_count_24h,
    COALESCE(o.outgoing_amount_24h, 0) AS sender_outgoing_amount_24h,
    COALESCE(o.outgoing_count_7d, 0) AS sender_outgoing_count_7d,
    COALESCE(o.outgoing_amount_7d, 0) AS sender_outgoing_amount_7d,
    COALESCE(o.outgoing_count_30d, 0) AS sender_outgoing_count_30d,
    COALESCE(o.outgoing_amount_30d, 0) AS sender_outgoing_amount_30d,

    -- Account age and segment are known account metadata.
    t.day - receiver.account_created_day AS receiver_account_age_days,
    receiver.segment AS receiver_segment,
    t.day - sender.account_created_day AS sender_account_age_days,
    sender.segment AS sender_segment,

    -- Ratios use only historical activity.
    CASE
        WHEN COALESCE(i.incoming_amount_30d, 0) > 0
        THEN t.amount_inr / i.incoming_amount_30d
        ELSE NULL
    END AS amount_vs_receiver_incoming_30d,

    CASE
        WHEN COALESCE(o.outgoing_amount_30d, 0) > 0
        THEN t.amount_inr / o.outgoing_amount_30d
        ELSE NULL
    END AS amount_vs_sender_outgoing_30d

FROM transactions t

LEFT JOIN inbound i
    ON t.transaction_id = i.transaction_id

LEFT JOIN outbound o
    ON t.transaction_id = o.transaction_id

LEFT JOIN accounts receiver
    ON t.receiver_id = receiver.account_id

LEFT JOIN accounts sender
    ON t.sender_id = sender.account_id;
