# AI Financial Risk Engine

FastAPI-based backend that ingests financial transactions, computes risk scores, generates forecasts and simulations, detects anomalies, and explains findings with an LLM-friendly narrative.

## Features

- Transaction ingestion with CSV/JSON support, cleansing, and deduplication.
- Financial risk engine with survival probability, heatmaps, and deterministic rule checks.
- Forecasting module leveraging exponential smoothing (ARIMA-ready) for 30/60/90 day horizons.
- Scenario simulations for insolvency probability and stress summaries.
- IsolationForest/DBSCAN-powered anomaly detector.
- JWT authentication for register/login/refresh flows.
- Modular services for LLM explainers and rule engines.
- Docker Compose stack with FastAPI, Postgres, and PGAdmin.

## Project Structure

```
ai-financial-risk-engine/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── routers/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   └── security/
├── sample_data/
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Getting Started

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.11 for local dev

### Environment Variables
Copy `.env.example` (create from below) if you need overrides:
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/risk_engine
JWT_SECRET_KEY=your-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Run with Docker
```bash
docker-compose up --build
```
Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Local Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Ensure Postgres is running and `DATABASE_URL` is set accordingly.

## Database & Authentication
- On startup the app auto-creates tables (Companies, Transactions, RiskReports, Forecasts, Simulations, Users).
- Register a user: `POST /auth/register` with form data `email` & `password`.
- Login: `POST /auth/login` (OAuth2 form). Use the bearer token for protected endpoints.
- Refresh tokens via `POST /auth/refresh` with existing bearer token.

## Core Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/ingest/transactions` | Upload CSV/JSON records for a company. |
| POST | `/risk/report/{company_id}` | Generate risk scores, heatmap, survival probability, rules, LLM explanation. |
| POST | `/forecast/{company_id}` | Produce 30/60/90-day revenue & expense projections with runway. |
| POST | `/simulate/{company_id}` | Run stress scenarios (sales drop, expense spike, debtor delays, etc.). |
| POST | `/anomalies/{company_id}` | Detect unusual spending spikes, duplicates, cashflow breaks, category drift. |

### Sample Requests
- Transaction ingest body: see [`sample_data/example_transactions.json`](sample_data/example_transactions.json)
- Risk report response: [`sample_data/sample_risk_report.json`](sample_data/sample_risk_report.json)
- Forecast response: [`sample_data/sample_forecast.json`](sample_data/sample_forecast.json)
- Simulation response: [`sample_data/sample_simulation.json`](sample_data/sample_simulation.json)
- Anomaly detection: [`sample_data/sample_anomalies.json`](sample_data/sample_anomalies.json)

## LLM Explainer
`app/services/llm_explainer.py` contains `explain_risk(report_json)` which can be extended to call Fireworks, Groq, or OpenAI. Inject API keys via environment variables and replace the deterministic stub with the chosen provider.

## Deployment
- **Railway**: Create a new service, add the repo, set environment variables (`DATABASE_URL`, JWT secrets), and provision a Postgres add-on.
- **Fly.io**: Use `fly launch`, configure secrets with `fly secrets set`, and ensure Postgres attachment or external database credentials are configured.

## Testing the Engine Quickly
1. Run migrations via startup auto-create.
2. Insert a company record (manual SQL or ORM).
3. POST the sample transactions to `/ingest/transactions`.
4. Call `/risk/report/1`, `/forecast/1`, `/simulate/1`, and `/anomalies/1` to observe outputs matching the sample JSON files.

## License
MIT
