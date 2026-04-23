# movie-api-automation

A fully automated movie data pipeline with a Streamlit dashboard, built to demonstrate a complete dev workflow — from code quality checks to data validation and deployment.

## 🚀 Live Application

**[https://movie-api-automation-4gufjmxzzo2vdhdy4jcwaz.streamlit.app/](https://movie-api-automation-4gufjmxzzo2vdhdy4jcwaz.streamlit.app/)**

The application is deployed on Streamlit Community Cloud and updated daily by the automated data workflow.

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
Lint & Format Check (ruff + black)
    ↓
Basic Checks & Unit Tests (imports, compile, pytest + coverage)
    ↓
Dev Validation (dev branch)  /  Production Check (main branch)
    ↓
Pipeline Summary (always runs)
```

- **Lint & Format Check** — fails fast if code style or formatting issues are found
- **Basic Checks & Unit Tests** — runs 55 tests with 93.63% coverage, enforces 50% minimum threshold
- **Dev Validation** — schema check, data integrity check, module structure validation
- **Production Check** — stricter validation including minimum record count and smoke tests
- **Pipeline Summary** — writes a markdown summary table to the GitHub Actions job summary

---

## Data workflow (`movie_workflow.yml`)

Runs daily at 12:00 UTC, or manually via `workflow_dispatch`.

```
Fetch Movie Data (runs get_top_movies.py, checks DB is not empty)
    ↓
Validate Ingested Data (schema, integrity, CSV export)
    ↓
Commit Updated Data (timestamped commit back to repo)
    ↓
Workflow Summary (reports stage results and record count)
```

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
Get a free API key at [themoviedb.org](https://www.themoviedb.org/settings/api).

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

---

## Results

- ✅ 55 tests passing
- ✅ 93.63% test coverage
- ✅ Daily scheduled data refresh
- ✅ Live deployment on Streamlit Community Cloud
