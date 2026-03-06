# Nursh

**A health-focused food journal that tracks food groups — not calories.**

Nursh helps people eat well without the anxiety of calorie counting. It provides personalized, culturally-aware food recommendations rooted in your health context (PCOS, anemia, pregnancy, thyroid conditions, and more), with full transparency into *why* each recommendation is made.

[Live Demo](#demo) | [Architecture](#architecture) | [Technical Highlights](#technical-highlights) | [Setup](#getting-started)

---

## What Makes This Different

Most food tracking apps treat nutrition as a numbers game — calories in, calories out. Nursh reframes the question from "how much did you eat?" to "what does your body need?"

- **13 food groups instead of macros** — track dark leafy greens, fermented foods, omega-3 sources, etc.
- **Culturally inclusive food data** — South Asian, West African, East Asian, Latin American, and Middle Eastern cuisines from authoritative national databases (USDA, IFCT, FAO/INFOODS)
- **Health-context awareness** — recommendations adapt to conditions like PCOS, iron-deficiency anemia, hypothyroidism, pregnancy by trimester, and perimenopause
- **Radical transparency** — every recommendation shows its logic chain, data source, and evidence citation
- **AI that never invents nutrition data** — LLMs handle language; deterministic algorithms handle all numbers

---

## Demo

![Nursh Demo](nursh_demo-ezgif.com-video-to-gif-converter.gif)

---

## Architecture

Nursh uses a **three-layer architecture** that separates AI capabilities from nutrition data integrity:

```
                     User Input (text / search / browse)
                              |
                    +---------v---------+
                    |   AI Input Layer   |     LangGraph agents parse natural
                    |   (meal_parser)    |     language into structured food items
                    +---------+---------+
                              |
                    +---------v---------+
                    | Deterministic Data |     All nutrition data, food group
                    |       Layer        |     classification, gap analysis,
                    |                    |     health rules, nutrient pairings
                    +---------+---------+     (NO AI — fully auditable)
                              |
                    +---------v---------+
                    |  AI Output Layer   |     LangGraph agents generate warm,
                    |   (recommender,    |     culturally-aware recommendations
                    |   insight_writer)  |     with guardrails + evidence citations
                    +---------+---------+
                              |
                     Personalized Recommendations
                     with Transparency Traces
```

**Stack**: Python FastAPI + LangGraph | Next.js + TypeScript | Supabase (PostgreSQL + pgvector + pg_trgm) | Gemini Flash (dev) / Claude (prod)

---

## Technical Highlights

### Self-Correcting LangGraph Agents

The recommender agent uses a **retry loop with decreasing temperature** when guardrails catch violations:

```
gather_context --> generate_recommendations --> validate_guardrails
                                                    |
                                         [valid] ---+--> attach_traces --> END
                                                    |
                                         [invalid, retries < 3] --> regenerate_with_feedback
                                                    |                (includes specific violations)
                                         [invalid, retries >= 3] --> template_fallback
```

Each retry feeds back the specific violations ("message contains 'you should' — rephrase as a suggestion") and lowers the temperature (0.5 -> 0.35 -> 0.2). If the LLM can't self-correct after 3 attempts, safe pre-written templates populated with Data Layer values serve as a deterministic fallback.

The meal parser agent similarly routes through confidence-based branching — high-confidence items resolve directly, while low-confidence items trigger fuzzy search and disambiguation UI.

### Defense-in-Depth Guardrails

LLM output safety uses two independent layers that must both pass:

**1. System prompt constraints** — 7 absolute rules baked into every generation prompt:
- Never state specific nutrient quantities (prevents hallucinated "15mg of iron")
- Never use diagnostic language ("you should", "you must")
- Never use negative food language ("avoid", "don't eat")
- Always frame additively ("consider adding", "you might enjoy")

**2. Regex blocklist validation** — catches what prompts miss, organized into four categories:

| Category | Examples | Why It Matters |
|----------|----------|----------------|
| Diagnostic | "you should", "you need to", "your condition requires" | Not a medical provider |
| Negative food | "avoid", "bad for you", "you're deficient" | Additive philosophy only |
| Medical | "treat", "cure", "diagnose", "prescription" | Legal and safety boundary |
| Invented quantities | `\d+\s*(mg\|mcg\|g)`, `\d+%\s*(DV\|RDA)` | AI never invents numbers |

### Deterministic Data Layer (No AI Touches Nutrition Data)

Every nutrient value, food group classification, and gap analysis traces back to an authoritative source. The Data Layer is purely algorithmic:

- **Gap analysis** reads from a **materialized view** (`user_daily_food_groups`) for O(1) performance instead of joining 4 tables per request. Targets adjust per health condition — iron-deficiency anemia increases `dark_leafy_greens` target from 5 to 7 days/week.
- **Health rules engine** — deterministic rule mappings (condition -> priority food groups, suggested foods, beneficial pairings, inhibitor pairings). Each rule links to a published evidence citation via `rule_key`.
- **Nutrient pairing detection** — identifies beneficial combinations (iron + vitamin C) and inhibitors (iron + calcium) within single meals.
- **Recipe decomposition** — a **recursive CTE** walks a DAG of recipe components (e.g., garam masala is a sub-recipe in 50+ dishes) applying yield and retention factors at each level.

### Cross-Cultural Food Discovery via pgvector

Each food has a 20-dimensional nutrient vector. Cosine similarity search enables discovery across cuisine boundaries:

> "I eat dal every day — what's nutritionally similar from other cuisines?"
> -> Black beans (Latin American, 0.89), Hummus (Middle Eastern, 0.84), Tempeh (Indonesian, 0.78)

This is backed by an **HNSW index** (`m=16, ef_construction=64`) for approximate nearest neighbor search at scale, combined with **pg_trgm** `word_similarity` for fuzzy text matching ("dal" finds "dal makhani" where standard `similarity()` fails).

### Transparency Traces

Every recommendation carries a trace built *after* LLM generation using only Data Layer outputs:

```json
{
  "logic_chain": [
    "Health context: iron_deficiency_anemia + pcos",
    "Gap analysis: dark_leafy_greens present 1/7 days (high gap)",
    "Rule: iron_deficiency_anemia -> prioritize iron-rich greens",
    "Food match: moringa — iron: 28mg/100g, calcium: 185mg/100g",
    "Cuisine fit: South Indian (matches user preference)"
  ],
  "data_source": {
    "food": "Drumstick Leaves (Moringa)",
    "source": "IFCT 2017",
    "source_id": "IFCT-G010",
    "source_url": "https://ifct2017.com/food/G010",
    "verified_date": "2024-11-15"
  },
  "evidence": {
    "claim": "Moringa leaves contain 28mg iron per 100g...",
    "citation": "Gopalakrishnan et al., J Food Sci & Tech, 2016"
  }
}
```

Traces are never hallucinated — they're assembled from the same deterministic data the rules engine used.

### Pluggable LLM Abstraction

A provider registry pattern allows swapping LLMs without code changes:

```python
# Set LLM_PROVIDER=gemini (dev) or LLM_PROVIDER=claude (prod)
provider = get_llm_provider()  # singleton factory
response = await provider.complete_structured(prompt, schema)
# -> LLMResponse(content, model, provider, latency_ms, tokens...)
```

Gemini Flash for fast development iteration, Claude for production quality. OpenAI as a fallback. Each provider implements the same `LLMProvider` abstract base class with `complete()` and `complete_structured()` methods.

---

## Project Structure

```
nursh/
  backend/
    app/
      agents/           # LangGraph agent graphs (meal_parser, recommender, insight_writer)
      api/routes/       # FastAPI endpoints (parse, recommend, insights, journal, food, profile)
      data_layer/       # Deterministic: gap analysis, health rules, pairings, transparency,
                        #   recipe engine, food search, nutrients
      db/               # Supabase client, queries, seed data (500+ foods from USDA/IFCT/FAO)
      guardrails/       # Blocklist regex, validators, template fallbacks
      llm/              # Provider abstraction (base, gemini, claude, openai, registry)
      prompts/v1/       # Versioned prompt templates (parse_meal, generate_recommendation,
                        #   generate_insight, disambiguate)
      supabase/
        migrations/     # 001-008: extensions, food tables, user tables, journal tables,
                        #   materialized views, indexes, favorites, RPC functions
  frontend/
    src/
      app/              # Next.js App Router pages (journal, log, insights, discover, profile)
      components/       # UI (Button, Card, Input), food groups (dashboard, chips),
                        #   transparency (confidence, traces, type labels)
      demo/             # Mock data + API for self-contained demo mode
      lib/              # API client, types, Supabase client, design tokens
      styles/           # Design tokens (warm palette, 13 food group colors)
  docs/
    PROMPT_ENGINEERING.md   # Prompt design decisions and iterations
    EVAL_FRAMEWORK.md       # LLM output quality measurement methodology
    LLM_FAILURES.md         # Observed failures, root causes, and mitigations
```

---

## Database Schema

Six PostgreSQL extensions power the search and similarity features:

| Extension | Purpose |
|-----------|---------|
| `pgvector` | 20-dimensional nutrient vectors for cross-cultural food similarity |
| `pg_trgm` | Fuzzy text search — `word_similarity` for partial food name matching |
| `uuid-ossp` | UUID generation for all entity IDs |

Key tables: `foods` (with nutrient_vector, source provenance, aliases[], tags[]), `food_groups` (13 categories), `food_nutrients` (per-nutrient authoritative data), `recipe_components` (DAG for composite dishes), `evidence_citations` (links health rules to published research), `journal_entries`, `journal_items`, `user_profiles`, `user_health_contexts`, `favorites`.

Performance: materialized view for gap analysis, GIN indexes on name/aliases/tags for trigram search, HNSW index on nutrient_vector for approximate nearest neighbor.

---

## Getting Started

### Prerequisites

- Python 3.12+, Node.js 22+
- Supabase project (or local Supabase via Docker)
- Gemini API key (dev) or Anthropic API key (prod)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Configure .env with SUPABASE_URL, SUPABASE_KEY, LLM_PROVIDER, GEMINI_API_KEY
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
# Configure .env.local with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
npm run dev
```
