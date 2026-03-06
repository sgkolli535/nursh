-- ============================================================
-- Materialized Views for Pre-Aggregated Analytics
-- ============================================================

-- Pre-aggregated food group presence per user per day.
-- Gap analysis reads from this view instead of joining 4 tables on every request.
CREATE MATERIALIZED VIEW user_daily_food_groups AS
SELECT
    je.user_id,
    je.date,
    jifg.food_group_id,
    COUNT(*) AS servings
FROM journal_entries je
JOIN journal_items ji ON je.id = ji.entry_id
JOIN journal_item_food_groups jifg ON ji.id = jifg.item_id
GROUP BY je.user_id, je.date, jifg.food_group_id;

-- Index on the materialized view for fast lookups
CREATE INDEX idx_user_daily_fg_user_date
    ON user_daily_food_groups (user_id, date);

CREATE INDEX idx_user_daily_fg_user_fg
    ON user_daily_food_groups (user_id, food_group_id);

-- Function to refresh the materialized view (called after journal writes)
CREATE OR REPLACE FUNCTION refresh_user_daily_food_groups()
RETURNS trigger AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_daily_food_groups;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Note: In production, you'd want to debounce this or refresh on a schedule
-- rather than on every single insert. For MVP, this is acceptable.
-- The CONCURRENTLY keyword allows reads during refresh.
