# GH-Yield: Ghana Treasury Bill Rate Forecasting System

**An end-to-end intelligent treasury management system that forecasts Ghana's 91-day T-bill rates, generates optimal investment signals, quantifies risk, and serves predictions through a production API with an interactive dashboard.**

---

## The Problem

Ghana's 91-day Treasury bill rate swung from **14%** (2021) to **35.7%** (February 2023) to **11%** (December 2025). For a treasury manager at a Ghanaian bank, timing this cycle on a GHS 50 million position translates to millions in quarterly earnings either captured or lost.

GH-Yield asks: **can a systematic, data-driven approach time these rate movements better than intuition?**

---

## Architecture

```
Data Sources → Feature Engineering → Model Training → Strategy Engine → API / Dashboard
     |                |                    |                |               |
 Bank of Ghana   29 features         8 ML models      BUY/HOLD/WAIT    FastAPI +
 FRED API        Technical +         Walk-forward CV   Risk metrics     Streamlit
 Yahoo Finance   Yield curve +       MLflow tracking   Backtesting      Docker
 World Bank      Macro + Regime      Ensemble          Monte Carlo
```

---

## Key Features

**Data Pipeline**
- Automated extraction from Bank of Ghana PDF statistical bulletins using pdfplumber
- FRED API integration for US T-bill rates and Federal Funds Rate
- Yahoo Finance for USD/GHS exchange rate
- World Bank API for Ghana inflation and GDP
- Alignment of daily, monthly, and annual data to a common monthly frequency

**Feature Engineering (29 features across 4 groups)**
- **Technical (15):** Lag features, momentum, rolling statistics, z-score mean reversion signal, rate acceleration
- **Yield Curve (4):** Term structure slope, curvature, short-end and long-end spreads
- **Macro / Policy (7):** Real rate, policy spread, Ghana-US rate differential, FX momentum, inflation momentum
- **Regime (3):** Volatility regime, rate direction regime, policy stance classification

**Modeling**
- 8 models: ARIMA, SARIMA, SARIMAX, Prophet, XGBoost, LightGBM, Ensemble, Naive Baseline
- Walk-forward cross-validation (expanding window, no random splits)
- MLflow experiment tracking for all model runs
- Hyperparameter tuning with proper time series methodology

**Strategy Engine**
- Trading signal generation: BUY (lock in rate before decline), WAIT (rates rising), HOLD (no significant change)
- Backtesting against buy-and-hold benchmark with GHS 1,000,000 initial portfolio
- Risk metrics: Value at Risk (VaR), Sharpe ratio, maximum drawdown
- Monte Carlo simulation: 10,000 rate path scenarios for 6-month outlook
- Automated treasury recommendation reports

**Production Deployment**
- FastAPI REST API with /predict, /signal, /health, and /history endpoints
- Streamlit interactive dashboard with KPI cards, charts, and data tables
- Docker containerization for reproducible deployment

---

## Project Structure

```
gh-yield/
├── data/
│   ├── ghana_tbill_rates.csv         # Target: 91-day, 182-day, 364-day rates
│   ├── us_tbill_3m.csv               # US 3-month T-bill rate
│   ├── fed_funds_rate.csv            # Federal Funds Rate
│   ├── usd_ghs.csv                   # USD/GHS exchange rate
│   ├── ghana_inflation.csv           # Ghana CPI inflation
│   ├── ghana_gdp.csv                 # Ghana GDP
│   ├── master_dataset.csv            # Aligned, merged dataset
│   ├── features_dataset.csv          # Final feature matrix (29 features)
│   ├── model.joblib                  # Trained XGBoost model
│   ├── model_comparison.csv          # All model results
│   ├── predictions_with_signals.csv  # Walk-forward predictions + signals
│   ├── backtest_strategy.csv         # Strategy portfolio performance
│   ├── backtest_benchmark.csv        # Benchmark portfolio performance
│   └── experiment_log.json           # Experiment tracking log
├── notebooks/
│   ├── 01_data_collection.ipynb      # Data sourcing and scraping
│   ├── 02_data_alignment.ipynb       # Frequency alignment and merging
│   ├── 03_feature_engineering.ipynb   # 29 features across 4 groups
│   ├── 04_modeling.ipynb             # 8 models, walk-forward CV, MLflow
│   ├── 05_strategy_engine.ipynb      # Signals, backtesting, Monte Carlo
│   └── 06_deployment.ipynb           # Model export, API + dashboard generation
├── src/
│   └── api.py                        # FastAPI REST API
├── dashboards/
│   └── app.py                        # Streamlit dashboard
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── FEATURE_ENGINEERING.md
└── README.md
```

---

## Results

### Model Comparison

| Model | RMSE | Directional Accuracy |
|---|---|---|
| Naive Baseline | 3.07 | 83.3% |
| XGBoost | — | 83.3% |
| LightGBM | — | 66.7% |
| Ensemble (XGB + LGB + SARIMAX) | — | 66.7% |
| Prophet (with regressors) | — | 66.7% |
| SARIMA(1,1,1)(1,0,0,12) | — | 50.0% |
| ARIMA(1,1,1) | — | 41.7% |
| SARIMAX (with macro regressors) | — | 41.7% |

The Naive Baseline winning is an honest and expected result for highly autocorrelated interest rate series in low-volatility periods. The 2025 test period had a slow, steady decline, which naive persistence handles well. The model's value emerges during regime transitions (e.g., the 2022-2023 crisis) where lag-based approaches fail.

### Key Findings

- The BoG policy rate consistently lagged the T-bill market rate throughout 2022-2023, meaning the market priced in tightening before the central bank acted
- Yield curve slope and policy rate spread are stronger directional predictors than the rate's own lags
- Ghana's 91-day rate dropped from 28.37% to 5.30% between January 2025 and June 2026, one of the sharpest declines in recent history

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | API information and available endpoints |
| `/predict` | GET | Returns next month's rate forecast |
| `/signal` | GET | Returns BUY/WAIT/HOLD signal with recommendation |
| `/health` | GET | Model health check and status |
| `/history` | GET | Historical T-bill rate data |

### Example Response (`/signal`)

```json
{
  "date": "2025-12-01",
  "current_rate": 10.98,
  "predicted_next_month": 11.12,
  "predicted_change": 0.14,
  "signal": "HOLD",
  "recommendation": "Maintain current position. No significant change expected.",
  "timestamp": "2026-06-23T21:00:00"
}
```

---

## Dashboard

The Streamlit dashboard provides:
- Real-time KPI cards (current rate, prediction, signal, yield curve slope)
- Interactive rate history chart (91-day, 182-day, 364-day, policy rate)
- Current yield curve visualization
- Trading signal overlay on historical rates
- Backtest equity curve (ML strategy vs buy-and-hold benchmark)
- Raw data explorer

---

## Setup and Installation

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/david006-DS/GH-Yield.git
cd GH-Yield

# Install dependencies
uv sync

# Train the model
uv run python src/model.py
```

### Run the API

```bash
cd src
uv run uvicorn api:app --reload --port 8000
```

Open `http://localhost:8000/predict` in your browser.

### Run the Dashboard

```bash
uv run streamlit run dashboards/app.py
```

Open `http://localhost:8501` in your browser.

### Run with Docker

```bash
docker-compose up --build
```

API available at `http://localhost:8000`, dashboard at `http://localhost:8501`.

---

## Data Sources

| Source | Data | Update Frequency |
|---|---|---|
| [Bank of Ghana](https://www.bog.gov.gh) | 91-day, 182-day, 364-day T-bill rates, Policy Rate | Monthly (PDF bulletins) |
| [FRED](https://fred.stlouisfed.org) | US 3-month T-bill (DTB3), Federal Funds Rate (FEDFUNDS) | Daily / Monthly |
| [Yahoo Finance](https://finance.yahoo.com) | USD/GHS exchange rate | Daily |
| [World Bank](https://data.worldbank.org) | Ghana inflation (CPI), GDP | Annual |

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Data Processing | Pandas, NumPy |
| ML Models | Scikit-Learn, XGBoost, LightGBM, Statsmodels, Prophet |
| Experiment Tracking | MLflow |
| API | FastAPI, Uvicorn |
| Dashboard | Streamlit, Plotly |
| Data Extraction | pdfplumber, BeautifulSoup, fredapi, yfinance, wbgapi |
| Containerization | Docker, Docker Compose |
| Package Management | uv |
| Version Control | Git, GitHub |

---

## Future Improvements

- [ ] Add weekly frequency data for higher-resolution forecasting
- [ ] Implement LSTM/GRU sequence models for regime transition detection
- [ ] Add regime-switching model to handle structural breaks (e.g., March 2023 DDEP)
- [ ] Source monthly CPI from Ghana Statistical Service (replacing annual World Bank data)
- [ ] Automated weekly data refresh pipeline with cron scheduling
- [ ] Deploy to cloud (AWS/GCP) with CI/CD via GitHub Actions
- [ ] Add prediction confidence intervals to the API response
- [ ] Implement model drift monitoring and automated retraining triggers

---

## Author

**David Quayefio**
- GitHub: [david006-DS](https://github.com/david006-DS)
- LinkedIn: [David Quayefio](https://www.linkedin.com/in/david-quayefio/)
- Location: Accra, Ghana

---

## License

This project is open source and available under the [MIT License](LICENSE).
