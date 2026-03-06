-- ============================================================
-- Food Journal Tables (RLS: users access only their own entries)
-- ============================================================

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snacks')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, date, meal_type)
);

CREATE TABLE journal_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    food_id UUID REFERENCES foods(id),  -- NULL if food not in DB
    food_name_raw TEXT NOT NULL,         -- What the user originally typed
    portion_description TEXT NOT NULL DEFAULT '1 serving',
    portion_grams_est NUMERIC,
    confidence_score NUMERIC NOT NULL DEFAULT 1.0 CHECK (confidence_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Which food groups each journal item contributes to
CREATE TABLE journal_item_food_groups (
    item_id UUID NOT NULL REFERENCES journal_items(id) ON DELETE CASCADE,
    food_group_id UUID NOT NULL REFERENCES food_groups(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, food_group_id)
);

-- RLS: Users can only access their own journal entries
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_item_food_groups ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own journal entries"
    ON journal_entries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own journal entries"
    ON journal_entries FOR ALL USING (auth.uid() = user_id);

-- Journal items accessed via their parent entry's user_id
CREATE POLICY "Users can view own journal items"
    ON journal_items FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM journal_entries
        WHERE journal_entries.id = journal_items.entry_id
        AND journal_entries.user_id = auth.uid()
    ));
CREATE POLICY "Users can manage own journal items"
    ON journal_items FOR ALL
    USING (EXISTS (
        SELECT 1 FROM journal_entries
        WHERE journal_entries.id = journal_items.entry_id
        AND journal_entries.user_id = auth.uid()
    ));

CREATE POLICY "Users can view own journal item food groups"
    ON journal_item_food_groups FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM journal_items ji
        JOIN journal_entries je ON je.id = ji.entry_id
        WHERE ji.id = journal_item_food_groups.item_id
        AND je.user_id = auth.uid()
    ));
CREATE POLICY "Users can manage own journal item food groups"
    ON journal_item_food_groups FOR ALL
    USING (EXISTS (
        SELECT 1 FROM journal_items ji
        JOIN journal_entries je ON je.id = ji.entry_id
        WHERE ji.id = journal_item_food_groups.item_id
        AND je.user_id = auth.uid()
    ));
