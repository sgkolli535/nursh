-- ============================================================
-- Food Database Tables (publicly readable, no auth required)
-- ============================================================

-- 13 food group categories as defined in Nursh Product Spec
CREATE TABLE food_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,  -- e.g. 'dark_leafy_greens'
    key_nutrients TEXT[] NOT NULL DEFAULT '{}',
    color_hex TEXT NOT NULL,
    icon_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Core food items from USDA, INDB, and other authoritative sources
CREATE TABLE foods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    aliases TEXT[] NOT NULL DEFAULT '{}',
    tags TEXT[] NOT NULL DEFAULT '{}',  -- Multi-attribute: ['vegetarian','indian','iron_rich']
    cuisine_region TEXT,
    -- Transparency / data provenance
    source TEXT NOT NULL,           -- 'USDA FoodData Central', 'Indian Nutrient Databank (INDB)', etc.
    source_id TEXT,                 -- e.g. 'FDC:172421'
    source_url TEXT,                -- Link to original source for user tap-through
    verified_date DATE,             -- Last verified date shown to users
    -- pgvector nutrient profile (20 dimensions)
    nutrient_vector vector(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Per-nutrient data for each food (authoritative, never AI-generated)
CREATE TABLE food_nutrients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    food_id UUID NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
    nutrient_name TEXT NOT NULL,    -- e.g. 'iron', 'vitamin_c', 'calcium'
    amount_per_100g NUMERIC NOT NULL,
    unit TEXT NOT NULL,             -- 'mg', 'mcg', 'g', 'IU'
    UNIQUE(food_id, nutrient_name)
);

-- Many-to-many: foods belong to multiple food groups
CREATE TABLE food_food_groups (
    food_id UUID NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
    food_group_id UUID NOT NULL REFERENCES food_groups(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (food_id, food_group_id)
);

-- Recipe decomposition DAG (composite dishes → ingredients)
CREATE TABLE recipe_components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_food_id UUID NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
    child_food_id UUID NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
    amount_grams NUMERIC NOT NULL,
    yield_factor NUMERIC NOT NULL DEFAULT 1.0,
    retention_factor NUMERIC NOT NULL DEFAULT 1.0,
    UNIQUE(parent_food_id, child_food_id)
);

-- Evidence citations for health rules and nutrient pairings
CREATE TABLE evidence_citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim TEXT NOT NULL,             -- 'Iron absorption is enhanced by vitamin C'
    citation_text TEXT NOT NULL,     -- 'Hallberg et al., 1989; Cook & Reddy, 2001'
    doi TEXT,                        -- DOI link if available
    rule_key TEXT NOT NULL UNIQUE,    -- Links to health_rules engine identifier
    display_text TEXT NOT NULL,      -- Clean, non-academic user-facing version
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS: Food tables are publicly readable
ALTER TABLE food_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE foods ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_nutrients ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_food_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_citations ENABLE ROW LEVEL SECURITY;

-- SELECT: anyone can read food data
CREATE POLICY "Food groups are publicly readable"
    ON food_groups FOR SELECT USING (true);
CREATE POLICY "Foods are publicly readable"
    ON foods FOR SELECT USING (true);
CREATE POLICY "Food nutrients are publicly readable"
    ON food_nutrients FOR SELECT USING (true);
CREATE POLICY "Food-group mappings are publicly readable"
    ON food_food_groups FOR SELECT USING (true);
CREATE POLICY "Recipe components are publicly readable"
    ON recipe_components FOR SELECT USING (true);
CREATE POLICY "Evidence citations are publicly readable"
    ON evidence_citations FOR SELECT USING (true);

-- INSERT/UPDATE/DELETE: allow all operations (service_role key bypasses RLS,
-- but these policies also allow writes for authenticated admin users)
CREATE POLICY "Allow insert food_groups" ON food_groups FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update food_groups" ON food_groups FOR UPDATE USING (true);
CREATE POLICY "Allow delete food_groups" ON food_groups FOR DELETE USING (true);

CREATE POLICY "Allow insert foods" ON foods FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update foods" ON foods FOR UPDATE USING (true);
CREATE POLICY "Allow delete foods" ON foods FOR DELETE USING (true);

CREATE POLICY "Allow insert food_nutrients" ON food_nutrients FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update food_nutrients" ON food_nutrients FOR UPDATE USING (true);
CREATE POLICY "Allow delete food_nutrients" ON food_nutrients FOR DELETE USING (true);

CREATE POLICY "Allow insert food_food_groups" ON food_food_groups FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update food_food_groups" ON food_food_groups FOR UPDATE USING (true);
CREATE POLICY "Allow delete food_food_groups" ON food_food_groups FOR DELETE USING (true);

CREATE POLICY "Allow insert recipe_components" ON recipe_components FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update recipe_components" ON recipe_components FOR UPDATE USING (true);
CREATE POLICY "Allow delete recipe_components" ON recipe_components FOR DELETE USING (true);

CREATE POLICY "Allow insert evidence_citations" ON evidence_citations FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update evidence_citations" ON evidence_citations FOR UPDATE USING (true);
CREATE POLICY "Allow delete evidence_citations" ON evidence_citations FOR DELETE USING (true);
