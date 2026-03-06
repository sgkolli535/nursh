-- ============================================================
-- User Profile Tables (RLS: users access only their own data)
-- ============================================================

-- User profile extends Supabase auth.users
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Health conditions (PCOS, anemia, hypothyroidism, pregnancy, etc.)
CREATE TABLE health_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    condition TEXT NOT NULL,  -- 'pcos', 'iron_deficiency_anemia', 'hypothyroidism', etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, condition)
);

-- Dietary preferences (vegetarian, vegan, gluten-free, etc.)
CREATE TABLE dietary_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    preference_type TEXT NOT NULL,  -- 'vegetarian', 'vegan', 'gluten_free', 'dairy_free'
    value TEXT NOT NULL DEFAULT 'true',
    UNIQUE(user_id, preference_type)
);

-- Cuisine preferences with affinity level
CREATE TABLE cuisine_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cuisine_region TEXT NOT NULL,   -- 'south_indian', 'north_indian', 'west_african', etc.
    affinity_level INTEGER NOT NULL DEFAULT 3 CHECK (affinity_level BETWEEN 1 AND 5),
    UNIQUE(user_id, cuisine_region)
);

-- RLS Policies: users can only access their own data
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE dietary_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE cuisine_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can view own health contexts"
    ON health_contexts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own health contexts"
    ON health_contexts FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own dietary preferences"
    ON dietary_preferences FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own dietary preferences"
    ON dietary_preferences FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own cuisine preferences"
    ON cuisine_preferences FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own cuisine preferences"
    ON cuisine_preferences FOR ALL USING (auth.uid() = user_id);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name)
    VALUES (new.id, new.raw_user_meta_data->>'display_name');
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
