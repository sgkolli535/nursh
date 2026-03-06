-- ============================================================
-- Favorite Meals — save meals for quick re-logging
-- ============================================================

CREATE TABLE favorite_meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    label TEXT NOT NULL,              -- User-facing name, e.g. "Idli sambar breakfast"
    items JSONB NOT NULL DEFAULT '[]', -- Array of {food_name, food_id, portion, food_group_ids}
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, label)
);

ALTER TABLE favorite_meals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own favorites"
    ON favorite_meals FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own favorites"
    ON favorite_meals FOR ALL USING (auth.uid() = user_id);

CREATE INDEX idx_favorite_meals_user ON favorite_meals (user_id);
