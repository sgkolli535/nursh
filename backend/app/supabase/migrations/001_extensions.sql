-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;    -- Fuzzy text search (trigram similarity)
CREATE EXTENSION IF NOT EXISTS vector;      -- pgvector for nutrient similarity search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- UUID generation
