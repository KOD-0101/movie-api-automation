# movie-api-automation

A fully automated movie data pipeline with a Streamlit dashboard, built to demonstrate a complete dev workflow, from code quality checks to data validation and deployment.

---

## What it does

The project pulls movie data from the [TMDB API](https://www.themoviedb.org/documentation/api), stores it in a local SQLite database, and serves it through an interactive dashboard. The whole thing runs on a daily schedule via GitHub Actions, with CI checks running on every push and pull request.

---

## Project structure

```
movie-api-automation/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI pipeline (lint, tests, validation)
│       └── movie_workflow.yml      # Daily data fetch and commit
├── tests/
│   ├── test_analyze_movies.py
│   ├── test_api.py
│   ├── test_dashboard.py
│   ├── test_database.py
│   ├── test_get_top_movies.py
│   ├── test_ui_helpers.py
│   └── test_validation.py
├── app.py                          # Streamlit entry point
├── dashboard.py                    # Dashboard and home page rendering
├── api.py                          # TMDB API calls with caching
├── database.py                     # Local SQLite data access
├── get_top_movies.py               # Data ingestion script
├── analyze_movies.py               # SQL analysis queries
├── validation.py                   # Movie record validation
├── ui_helpers.py                   # Session state and URL helpers
├── logger_setup.py                 # Shared logging config
├── movies.db                       # SQLite database (auto-updated daily)
├── top_movies.csv                  # CSV export of top 50 movies
└── requirements.txt
```

---

## CI pipeline (`ci.yml`)

Runs on every push and pull request across `main`, `dev`, `feature/**`, and `hotfix/**` branches.

```
Lint & Format Check
    ↓
Basic Checks & Unit Tests
    ↓
Dev Validation (dev branch)  /  Production Check (main branch)
    ↓
Pipeline Summary
```

**Lint & Format Check** — runs `ruff` for style errors and `black --check` for formatting. Fails fast if either finds issues, blocking everything downstream.

**Basic Checks & Unit Tests** — verifies all imports resolve, all scripts compile, and runs the full test suite with coverage reporting. Requires a minimum of 50% coverage to pass (currently sitting at ~92%).

**Dev Validation** — runs on the `dev` branch only. Checks the database schema has all expected columns, validates data integrity (rating ranges, null checks, category count), and confirms all dashboard modules load correctly.

**Production Check** — runs on `main` only. Stricter version of the above — requires at least 10 records in the DB, validates all module exports with smoke tests, and checks that dependencies are pinned.

**Pipeline Summary** — always runs regardless of other results, writes a markdown summary table to the GitHub Actions job summary.

---

## Data workflow (`movie_workflow.yml`)

Runs daily at 12:00 UTC, or manually via `workflow_dispatch`.

```
Fetch Movie Data
    ↓
Validate Ingested Data
    ↓
Commit Updated Data
    ↓
Workflow Summary
```

**Fetch Movie Data** — runs `get_top_movies.py`, which pulls from four TMDB endpoints (`top_rated`, `popular`, `now_playing`, `upcoming`) across 5 pages each. Each record goes through `validation.py` before being inserted. Fails immediately if the DB ends up empty.

**Validate Ingested Data** — checks the schema, runs integrity checks (nulls, rating ranges, category coverage), and exports a fresh `top_movies.csv` with the top 50 rated movies.

**Commit Updated Data** — commits `movies.db` and `top_movies.csv` back to the repo with a timestamped commit message.

**Workflow Summary** — reports the result of each stage and the total row count to the GitHub Actions summary tab.

---

## Running locally

**1. Clone the repo and set up a virtual environment:**
```bash
git clone https://github.com/KOD-0101/movie-api-automation.git
cd movie-api-automation
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Add your TMDB API key:**

Create a `.env` file in the root directory:
```
TMDB_API_KEY=your_key_here
```
You can get a free API key at [themoviedb.org](https://www.themoviedb.org/settings/api).

**3. Fetch movie data:**
```bash
python get_top_movies.py
```

**4. Run the dashboard:**
```bash
streamlit run app.py
```

**5. Run the tests:**
```bash
pytest --cov=. --cov-report=term-missing
```

---

## Tech stack

- **Python 3.11**
- **Streamlit** — dashboard and UI
- **SQLite** — local data storage
- **TMDB API** — movie data source
- **GitHub Actions** — CI/CD and scheduled automation
- **pytest + pytest-cov** — testing and coverage
- **ruff + black** — linting and formatting
