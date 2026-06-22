# GH-Yield: Feature Engineering Summary

## Project Overview

**Project:** GH-Yield — Intelligent Treasury Bill Rate Forecasting System for Ghana
**Author:** David Quayefio
**Target Variable:** Next month's 91-day Treasury Bill rate (interest equivalent)
**Dataset Period:** December 2019 — December 2025
**Frequency:** Monthly

---

## Data Sources

| Source | Data | Frequency | Collection Method |
|---|---|---|---|
| Bank of Ghana (PDF bulletins) | 91-day, 182-day, 364-day T-bill rates, BoG Policy Rate | Monthly | PDF extraction with pdfplumber |
| FRED API | US 3-month T-bill rate | Daily → resampled to monthly | fredapi library |
| FRED API | Federal Funds Rate | Monthly | fredapi library |
| Yahoo Finance | USD/GHS exchange rate | Daily → resampled to monthly | yfinance library |
| World Bank API | Ghana inflation (CPI, year-on-year) | Annual → forward-filled to monthly | wbgapi library |
| World Bank API | Ghana GDP (current USD) | Annual → forward-filled to monthly | wbgapi library |

---

## Data Alignment Process

1. **Daily to monthly resampling:** US T-bill rate and USD/GHS exchange rate were resampled from daily to monthly using the mean of each month.
2. **Annual to monthly conversion:** Inflation and GDP data (annual) were forward-filled across months within each year.
3. **Missing month interpolation:** Ghana T-bill data had gaps where BoG PDFs skipped certain months. These were filled using linear interpolation.
4. **Outlier correction:** A USD/GHS data anomaly in March 2020 (31.31 instead of ~5.7) was identified and corrected via interpolation.
5. **Final merge:** All sources were merged on the date column into a single master DataFrame with 73 monthly observations.

---

## Feature Groups

### Group 1: Technical / Statistical Features (15 features)

These features capture the historical behaviour and statistical properties of the 91-day T-bill rate itself.

| Feature | Formula | Rationale |
|---|---|---|
| `rate_lag_1` | rate(t-1) | Previous month's rate, strongest predictor |
| `rate_lag_2` | rate(t-2) | Two months ago |
| `rate_lag_3` | rate(t-3) | Three months ago |
| `rate_lag_4` | rate(t-4) | Four months ago |
| `momentum_1m` | rate(t) - rate(t-1) | Short-term rate direction |
| `momentum_3m` | rate(t) - rate(t-3) | Medium-term rate trend |
| `momentum_6m` | rate(t) - rate(t-6) | Long-term rate trend |
| `roc_1m` | pct_change(1) * 100 | 1-month percentage rate of change |
| `roc_3m` | pct_change(3) * 100 | 3-month percentage rate of change |
| `acceleration` | momentum_1m(t) - momentum_1m(t-1) | Is the trend strengthening or weakening? |
| `rolling_mean_6m` | rolling(6).mean() | 6-month moving average |
| `rolling_mean_12m` | rolling(12).mean() | 12-month moving average |
| `rolling_std_6m` | rolling(6).std() | 6-month volatility |
| `rolling_std_12m` | rolling(12).std() | 12-month volatility |
| `z_score_12m` | (rate - mean_12m) / std_12m | Mean reversion signal: how far from normal |

### Group 2: Yield Curve Features (4 features)

These features capture the shape of Ghana's yield curve, which signals market expectations about future rates.

| Feature | Formula | Rationale |
|---|---|---|
| `yield_slope` | tbill_364 - tbill_91 | Term premium: positive = normal curve, negative = inverted |
| `yield_curvature` | 2 * tbill_182 - tbill_91 - tbill_364 | Non-linear term structure, butterfly spread |
| `spread_182_91` | tbill_182 - tbill_91 | Short-end spread |
| `spread_364_182` | tbill_364 - tbill_182 | Long-end spread |

### Group 3: Macro / Policy Features (6 features)

These features capture the macroeconomic environment driving T-bill rates.

| Feature | Formula | Rationale |
|---|---|---|
| `policy_spread` | tbill_91 - policy_rate | Monetary policy transmission. Positive = market rates above policy, tight liquidity |
| `real_rate` | tbill_91 - inflation | Inflation-adjusted return. Negative real rates discourage investment |
| `rate_differential` | tbill_91 - us_tbill_3m | Ghana vs US rate gap. Drives capital flows and FX pressure |
| `fx_change_1m` | pct_change(usd_ghs, 1) * 100 | 1-month cedi depreciation. Currency weakness often precedes rate hikes |
| `fx_change_3m` | pct_change(usd_ghs, 3) * 100 | 3-month cedi depreciation trend |
| `inflation_change` | inflation(t) - inflation(t-1) | Inflation momentum. Rising inflation signals future rate increases |
| `fed_change` | fed_funds(t) - fed_funds(t-1) | US monetary policy shift. Fed hikes tighten global liquidity |

### Group 4: Regime Features (3 features)

These features classify the current market environment into distinct regimes.

| Feature | Method | Rationale |
|---|---|---|
| `high_vol_regime` | 1 if rolling_std_6m > median, else 0 | Binary flag for high-volatility periods. Models may behave differently across regimes |
| `rate_regime` | "falling" if momentum_3m < -1, "stable" if between -1 and 1, "rising" if > 1 | Categorical regime label for the rate trend |
| `policy_tight` | 1 if policy_rate > tbill_91, else 0 | Is the central bank ahead of or behind the market? |

---

## Target Variables

| Target | Formula | Use Case |
|---|---|---|
| `target` | tbill_91(t+1) | Regression: predict next month's exact rate |
| `target_direction` | 1 if target > tbill_91, else 0 | Classification: predict whether the rate goes up or down |

---

## Key Observations from the Data

### Rate Cycle (2019-2025)
- **2019-2021:** Stable rates around 12-14%, low volatility environment
- **2022:** Rates climbed sharply from 12.5% to 35.5% as Ghana's debt crisis escalated and inflation surged past 50%
- **Early 2023 peak:** 91-day rate hit 35.67% in February 2023, the highest in the dataset
- **March 2023 correction:** Rates crashed from 35.67% to 20.38% in a single month following the domestic debt exchange programme (DDEP)
- **2024:** Rates stabilised between 24-28%, elevated but controlled
- **2025:** Rapid decline from 28.37% to 11.08% as inflation fell from 23.5% to 5.4% and the BoG cut the policy rate from 27% to 18%

### Yield Curve Dynamics
- The yield curve slope (364-day minus 91-day) was consistently positive throughout the period, ranging from approximately 1.8% to 7.4%
- The curve flattened significantly during the 2023 crisis when short-term rates spiked
- Curvature turned negative during rapid rate changes, signalling market stress

### Macro Drivers
- Inflation and the 91-day rate show strong co-movement with a 1-3 month lag
- USD/GHS depreciation episodes (mid-2022, late-2023) preceded T-bill rate increases
- The BoG policy rate frequently lagged the T-bill rate, meaning the market moved before the central bank

---

## Feature Count Summary

| Category | Count |
|---|---|
| Technical / Statistical | 15 |
| Yield Curve | 4 |
| Macro / Policy | 7 |
| Regime | 3 |
| **Total Features** | **29** |
| Target Variables | 2 |

---

## Data Quality Notes

1. **Missing months:** Some months were missing from BoG PDF data (PDFs report 10-12 of 13 possible months per file). These were filled using linear interpolation.
2. **Inflation granularity:** Annual inflation was forward-filled to monthly. For improved model performance, monthly CPI data from the Ghana Statistical Service should be sourced in a future iteration.
3. **GDP granularity:** Same limitation as inflation. Quarterly GDP estimates would improve the signal.
4. **FX data quality:** One outlier in March 2020 was corrected. The USD/GHS exchange rate from Yahoo Finance occasionally shows data gaps or spikes that require cleaning.
5. **Sample size:** 73 monthly observations is small for ML. This constrains model complexity and makes walk-forward cross-validation essential to avoid overfitting.

---

## Files Generated

| File | Location | Description |
|---|---|---|
| `master_dataset.csv` | `data/` | Aligned raw data, all sources merged, 73 rows x 10 columns |
| `features_dataset.csv` | `data/` | Final feature matrix with all 29 features + targets, NaN rows dropped |
| `overview_chart.png` | `data/` | Time series plot of T-bill rate, exchange rate, and inflation |
| `correlation_heatmap.png` | `data/` | Feature correlation heatmap (top 15 features vs target) |

---

## Next Steps (Week 2: Modeling)

1. Train classical time series models (ARIMA, SARIMA, Prophet) on the 91-day rate
2. Train ML models (XGBoost, LightGBM) using the engineered features
3. Train LSTM/GRU on rate sequences
4. Implement walk-forward cross-validation (expanding window)
5. Track all experiments in MLflow
6. Build a weighted ensemble of the best-performing models
7. Evaluate using RMSE, MAE, directional accuracy, and Diebold-Mariano test
