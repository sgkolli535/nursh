-- ============================================================
-- RPC Functions for advanced queries
-- ============================================================

-- 1. Fuzzy food search via pg_trgm word_similarity
-- word_similarity is better than similarity() because "dal" matches
-- "dal makhani" even though full-string similarity is low.
CREATE OR REPLACE FUNCTION search_foods_fuzzy(
    query_text text,
    result_limit int DEFAULT 10
)
RETURNS TABLE(id uuid, name text, cuisine_region text, source text, source_id text, similarity float)
AS $$
    SELECT f.id, f.name, f.cuisine_region, f.source, f.source_id,
           GREATEST(
               word_similarity(query_text, f.name),
               similarity(query_text, f.name)
           )::float AS sim
    FROM foods f
    WHERE word_similarity(query_text, f.name) > 0.3
       OR query_text % ANY(f.aliases)
    ORDER BY sim DESC
    LIMIT result_limit;
$$ LANGUAGE sql STABLE;


-- 2. Nutrient similarity via pgvector cosine distance
-- Powers cross-cultural food discovery:
-- "You enjoy dal. Here are similar foods from other cuisines."
CREATE OR REPLACE FUNCTION find_similar_foods(
    target_food_id uuid,
    exclude_cuisine_region text DEFAULT NULL,
    result_limit int DEFAULT 5
)
RETURNS TABLE(id uuid, name text, cuisine_region text, source text, source_id text, similarity float)
AS $$
    SELECT f.id, f.name, f.cuisine_region, f.source, f.source_id,
           (1 - (f.nutrient_vector <=> t.nutrient_vector))::float AS similarity
    FROM foods f, foods t
    WHERE t.id = target_food_id
      AND f.id != target_food_id
      AND f.nutrient_vector IS NOT NULL
      AND t.nutrient_vector IS NOT NULL
      AND (exclude_cuisine_region IS NULL OR f.cuisine_region != exclude_cuisine_region)
    ORDER BY f.nutrient_vector <=> t.nutrient_vector
    LIMIT result_limit;
$$ LANGUAGE sql STABLE;


-- 3. User food group summary for gap analysis
-- Reads from materialized view (or falls back to direct query)
CREATE OR REPLACE FUNCTION get_user_food_group_summary(
    target_user_id uuid,
    start_date date DEFAULT (CURRENT_DATE - INTERVAL '6 days')::date,
    end_date date DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    slug text,
    food_group_name text,
    days_present bigint,
    food_group_slug text
)
AS $$
    SELECT
        fg.slug,
        fg.name AS food_group_name,
        COUNT(DISTINCT je.date) AS days_present,
        fg.slug AS food_group_slug
    FROM food_groups fg
    LEFT JOIN food_food_groups ffg ON ffg.food_group_id = fg.id
    LEFT JOIN journal_items ji ON ji.food_id = ffg.food_id
    LEFT JOIN journal_entries je ON je.id = ji.entry_id
        AND je.user_id = target_user_id
        AND je.date BETWEEN start_date AND end_date
    GROUP BY fg.id, fg.slug, fg.name
    ORDER BY fg.name;
$$ LANGUAGE sql STABLE;


-- 4. Compute recipe nutrients via recursive CTE
-- Walks the recipe_components DAG to sum nutrients for composite dishes
CREATE OR REPLACE FUNCTION compute_recipe_nutrients(
    target_food_id uuid
)
RETURNS TABLE(nutrient_name text, total_amount numeric)
AS $$
    WITH RECURSIVE ingredients AS (
        -- Base case: direct components
        SELECT
            rc.child_food_id,
            rc.amount_grams,
            rc.yield_factor,
            rc.retention_factor
        FROM recipe_components rc
        WHERE rc.parent_food_id = target_food_id

        UNION ALL

        -- Recursive case: sub-components
        SELECT
            rc.child_food_id,
            rc.amount_grams * i.yield_factor,
            rc.yield_factor,
            rc.retention_factor
        FROM recipe_components rc
        JOIN ingredients i ON rc.parent_food_id = i.child_food_id
    )
    SELECT
        fn.nutrient_name,
        SUM(fn.amount_per_100g * i.amount_grams / 100.0 * i.retention_factor) AS total_amount
    FROM ingredients i
    JOIN food_nutrients fn ON fn.food_id = i.child_food_id
    GROUP BY fn.nutrient_name;
$$ LANGUAGE sql STABLE;


-- 5. Add unique index on materialized view for CONCURRENTLY refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_daily_fg_unique
    ON user_daily_food_groups (user_id, date, food_group_id);
