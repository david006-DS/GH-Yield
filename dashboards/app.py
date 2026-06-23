import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
from pathlib import Path

st.set_page_config(page_title="GH-Yield Dashboard", page_icon="", layout="wide")
st.title("GH-Yield: Ghana T-Bill Forecasting System")
st.markdown("Intelligent Treasury Bill Rate Forecasting for Ghana")

DATA_PATH = Path(__file__).parent.parent / "data"


@st.cache_data
def load_data():
    tbill = pd.read_csv(DATA_PATH / "ghana_tbill_rates.csv", parse_dates=["date"])
    features = pd.read_csv(DATA_PATH / "features_dataset.csv", parse_dates=["date"])
    try:
        signals = pd.read_csv(DATA_PATH / "predictions_with_signals.csv", parse_dates=["date"])
    except:
        signals = None
    try:
        strategy = pd.read_csv(DATA_PATH / "backtest_strategy.csv", parse_dates=["date"])
        benchmark = pd.read_csv(DATA_PATH / "backtest_benchmark.csv", parse_dates=["date"])
    except:
        strategy = None
        benchmark = None
    return tbill, features, signals, strategy, benchmark


def get_prediction():
    saved = joblib.load(DATA_PATH / "model.joblib")
    model = saved["model"]
    feature_cols = saved["features"]
    df = pd.read_csv(DATA_PATH / "features_dataset.csv", parse_dates=["date"])
    latest = df.iloc[-1]
    X = latest[feature_cols].values.reshape(1, -1)
    predicted = float(model.predict(X)[0])
    current = float(latest["tbill_91"])
    change = predicted - current
    if change < -0.5:
        signal = "BUY"
    elif change > 0.5:
        signal = "WAIT"
    else:
        signal = "HOLD"
    return {
        "current_rate": round(current, 2),
        "predicted_next_month": round(predicted, 2),
        "predicted_change": round(change, 2),
        "signal": signal
    }


tbill, features, signals, strategy, benchmark = load_data()
prediction = get_prediction()

# KPI Cards
st.header("Current Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="91-Day Rate", value=f"{prediction['current_rate']:.2f}%")

with col2:
    st.metric(
        label="Predicted Next Month",
        value=f"{prediction['predicted_next_month']:.2f}%",
        delta=f"{prediction['predicted_change']:+.2f}%"
    )

with col3:
    signal_icon = {"BUY": "GREEN", "WAIT": "RED", "HOLD": "YELLOW"}
    st.metric(label="Signal", value=f"{prediction['signal']}")

with col4:
    slope = tbill["tbill_364"].iloc[-1] - tbill["tbill_91"].iloc[-1]
    st.metric(label="Yield Curve Slope", value=f"{slope:.2f}%")

# Rate History
st.header("Rate History")
fig = go.Figure()
fig.add_trace(go.Scatter(x=tbill["date"], y=tbill["tbill_91"], name="91-Day", line=dict(width=2)))
fig.add_trace(go.Scatter(x=tbill["date"], y=tbill["tbill_182"], name="182-Day", line=dict(width=2, dash="dash")))
fig.add_trace(go.Scatter(x=tbill["date"], y=tbill["tbill_364"], name="364-Day", line=dict(width=2, dash="dot")))
fig.add_trace(go.Scatter(x=tbill["date"], y=tbill["policy_rate"], name="Policy Rate", line=dict(width=1, color="red")))
fig.update_layout(yaxis_title="Rate (%)", hovermode="x unified", height=450)
st.plotly_chart(fig, use_container_width=True)

# Yield Curve
st.header("Current Yield Curve")
latest_row = tbill.iloc[-1]
tenors = ["91-Day", "182-Day", "364-Day"]
rates = [latest_row["tbill_91"], latest_row["tbill_182"], latest_row["tbill_364"]]
fig_yc = go.Figure()
fig_yc.add_trace(go.Scatter(x=tenors, y=rates, mode="lines+markers", line=dict(width=3, color="blue"), marker=dict(size=10)))
fig_yc.update_layout(yaxis_title="Rate (%)", xaxis_title="Tenor", height=350)
st.plotly_chart(fig_yc, use_container_width=True)

# Trading Signals
if signals is not None:
    st.header("Trading Signals History")
    fig_sig = go.Figure()
    fig_sig.add_trace(go.Scatter(x=signals["date"], y=signals["current_rate"], name="Actual Rate", line=dict(width=2, color="blue")))
    fig_sig.add_trace(go.Scatter(x=signals["date"], y=signals["predicted_next"], name="Predicted", line=dict(width=1, dash="dash", color="red")))
    for _, row in signals.iterrows():
        color = {"BUY": "green", "WAIT": "red", "HOLD": "gray"}[row["signal"]]
        fig_sig.add_vrect(x0=row["date"], x1=row["date"] + pd.Timedelta(days=28), fillcolor=color, opacity=0.1, line_width=0)
    fig_sig.update_layout(yaxis_title="Rate (%)", height=400)
    st.plotly_chart(fig_sig, use_container_width=True)

# Backtest
if strategy is not None and benchmark is not None:
    st.header("Backtest Performance")
    col1, col2 = st.columns(2)
    with col1:
        ret = (strategy["value"].iloc[-1] / 1_000_000 - 1) * 100
        st.metric("Strategy Return", f"{ret:.2f}%")
    with col2:
        ret_bm = (benchmark["value"].iloc[-1] / 1_000_000 - 1) * 100
        st.metric("Benchmark Return", f"{ret_bm:.2f}%")
    fig_bt = go.Figure()
    fig_bt.add_trace(go.Scatter(x=strategy["date"], y=strategy["value"], name="ML Strategy", line=dict(width=2, color="blue")))
    fig_bt.add_trace(go.Scatter(x=benchmark["date"], y=benchmark["value"], name="Buy & Hold", line=dict(width=2, dash="dash", color="red")))
    fig_bt.update_layout(yaxis_title="Portfolio Value (GHS)", height=400)
    st.plotly_chart(fig_bt, use_container_width=True)

# Data Table
st.header("Raw Data")
st.dataframe(tbill.sort_values("date", ascending=False), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**GH-Yield** | Built by David Quayefio | [GitHub](https://github.com/david006-DS/GH-Yield)")
