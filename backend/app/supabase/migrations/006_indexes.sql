-- ============================================================
-- Performance Indexes
-- ============================================================

-- Trigram indexes for fuzzy food search
-- word_similarity() matches partial words: "dal" finds "dal makhani"
CREATE INDEX idx_foods_trgm_name
    ON foods USING GIN (name gin_trgm_ops);

CREATE INDEX idx_foods_trgm_aliases
    ON foods USING GIN (aliases);

-- GIN index on tags for multi-attribute queries
-- e.g. WHERE tags @> ARRAY['vegetarian', 'indian', 'iron_rich']
CREATE INDEX idx_foods_tags
    ON foods USING GIN (tags);

-- HNSW index on nutrient_vector for fast cosine similarity search
-- Enables cross-cultural food discovery: "find nutritionally similar foods"
CREATE INDEX idx_foods_nutrient_vector
    ON foods USING hnsw (nutrient_vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Standard B-tree indexes for common lookups
CREATE INDEX idx_foods_cuisine_region ON foods (cuisine_region);
CREATE INDEX idx_foods_source ON foods (source);
CREATE INDEX idx_food_nutrients_food_id ON food_nutrients (food_id);
CREATE INDEX idx_food_food_groups_food_id ON food_food_groups (food_id);
CREATE INDEX idx_food_food_groups_group_id ON food_food_groups (food_group_id);
CREATE INDEX idx_recipe_components_parent ON recipe_components (parent_food_id);
CREATE INDEX idx_recipe_components_child ON recipe_components (child_food_id);
CREATE INDEX idx_evidence_citations_rule_key ON evidence_citations (rule_key);

-- Journal indexes
CREATE INDEX idx_journal_entries_user_date ON journal_entries (user_id, date);
CREATE INDEX idx_journal_items_entry_id ON journal_items (entry_id);
CREATE INDEX idx_journal_items_food_id ON journal_items (food_id);

-- User preference indexes
CREATE INDEX idx_health_contexts_user ON health_contexts (user_id);
CREATE INDEX idx_dietary_prefs_user ON dietary_preferences (user_id);
CREATE INDEX idx_cuisine_prefs_user ON cuisine_preferences (user_id);
