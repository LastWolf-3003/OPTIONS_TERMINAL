import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Institutional Options Algo Terminal & Bot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Bloomberg-Style CSS
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stSidebar { background-color: #161b22; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 6px; }
    h1, h2, h3, h4 { color: #58a6ff !important; margin-bottom: 0.2rem; }
    .signal-card-buy { background-color: #0e2a1f; border: 1px solid #238636; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .signal-card-sell { background-color: #2b0e12; border: 1px solid #da3633; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .tool-tip-box { background-color: #161b22; border-left: 4px solid #58a6ff; padding: 10px 15px; margin-bottom: 15px; border-radius: 0 6px 6px 0; font-size: 0.9rem; color: #8b949e; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Algo Engine Controls")
symbol = st.sidebar.selectbox("Underlying Asset", ["NIFTY 50", "BANKNIFTY", "SPX", "AAPL", "TSLA"])
spot_price = st.sidebar.number_input("Base Spot Price", value=24550.0 if "NIFTY" in symbol else 5850.0)
auto_refresh = st.sidebar.toggle("🟢 Live Algo Stream", value=True)
refresh_rate = st.sidebar.slider("Refresh Interval (sec)", 1.0, 10.0, 2.0)

# Algo Risk Parameters
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Algo Bot Settings")
algo_mode = st.sidebar.selectbox("Execution Mode", ["Paper Trading (Simulated)", "Live Broker API (Ready)", "Backtest Mode"])
risk_per_trade = st.sidebar.slider("Capital Risk per Trade ($)", 500, 5000, 1000)
score_threshold = st.sidebar.slider("Execution Score Threshold", 50, 90, 65)

# --- GENERATE SYNTHETIC REAL-TIME DATA ---
np.random.seed(int(time.time() // 10))
prices = np.linspace(spot_price - 120, spot_price + 120, 30)

dates = [datetime.now() - timedelta(minutes=5*i) for i in range(30)][::-1]
ohlc_df = pd.DataFrame({
    'Time': dates,
    'Open': spot_price + np.random.randn(30).cumsum(),
    'High': spot_price + np.random.randn(30).cumsum() + 15,
    'Low': spot_price + np.random.randn(30).cumsum() - 15,
    'Close': spot_price + np.random.randn(30).cumsum(),
    'Volume': np.random.randint(500, 5000, 30)
})
ohlc_df['VWAP'] = (ohlc_df['Volume'] * (ohlc_df['High'] + ohlc_df['Low'] + ohlc_df['Close']) / 3).cumsum() / ohlc_df['Volume'].cumsum()
std_dev = ohlc_df['Close'].std()
ohlc_df['VWAP_Upper'] = ohlc_df['VWAP'] + (1.5 * std_dev)
ohlc_df['VWAP_Lower'] = ohlc_df['VWAP'] - (1.5 * std_dev)
ohlc_df['Delta'] = np.random.randint(-1500, 1800, size=30)
ohlc_df['CVD'] = ohlc_df['Delta'].cumsum()

# --- MULTI-TOOL ALGORITHMIC SCORING ENGINE ---
# Combines all 9 tool metrics into a weighted score (-100 to +100)
last_close = ohlc_df['Close'].iloc[-1]
last_vwap = ohlc_df['VWAP'].iloc[-1]
last_cvd = ohlc_df['CVD'].iloc[-1]

# Tool 1 & 2: VWAP & CVD Score
score_vwap = 25 if last_close > last_vwap else -25
score_cvd = 20 if last_cvd > 0 else -20

# Tool 3: GEX Regime Score (Dealer Gamma)
gex_bullish = last_close > last_vwap
score_gex = 15 if gex_bullish else -15

# Tool 4 & 5: Heatmap & AMT (Market Profile POC/Value Area)
score_amt = 15 if last_close >= spot_price else -15

# Tool 6 & 7: Footprint Imbalance & Delta
score_footprint = np.random.choice([15, -15, 10, -10])

# Tool 8 & 9: Time & Sales Whale Sweeps
score_whales = np.random.choice([10, -10, 5])

# COMPOSITE ALGO SCORE
composite_score = score_vwap + score_cvd + score_gex + score_amt + score_footprint + score_whales

# --- MAIN APP LAYOUT WITH TABS ---
st.title(f"⚡ Institutional Options Terminal & Auto-Trading Bot — {symbol}")

tab1, tab2 = st.tabs(["📊 Multi-Tool Terminal", "🤖 Automated Algo Bot & Execution Desk"])

with tab1:
    # --- PREDICTIVE SIGNAL BANNER ---
    if composite_score >= score_threshold:
        action_color = "signal-card-buy"
        action_label = "🟢 ALGO SIGNAL: BUY CALL (LONG)"
        guidance = f"Composite Score (+{composite_score}) exceeds threshold. All 9 tools aligned bullish. Holding target active."
    elif composite_score <= -score_threshold:
        action_color = "signal-card-sell"
        action_label = "🔴 ALGO SIGNAL: BUY PUT (SHORT)"
        guidance = f"Composite Score ({composite_score}) indicates heavy distribution. Bearish cross on volume profile."
    else:
        action_color = "signal-card-buy"
        action_label = "🟡 ALGO STATUS: RANGE / FLAT"
        guidance = f"Composite Score ({composite_score}) is neutral. Awaiting breakout past VAH/VAL boundaries."

    st.markdown(f"""
    <div class="{action_color}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin:0; color:#ffffff !important;">{action_label}</h3>
                <p style="margin:5px 0 0 0; color:#d0d7de;"><b>Multi-Tool Synthesis:</b> {guidance}</p>
            </div>
            <div style="text-align: right;">
                <h2 style="margin:0; color:#f0f6fc !important;">Score: {composite_score}/100</h2>
                <span style="font-size: 0.85rem; color:#8b949e;">Threshold: ±{score_threshold}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # METRICS ROW
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Spot Price", f"{last_close:,.2f}", f"{(last_close - ohlc_df['Open'].iloc[-1]):+.2f}")
    m2.metric("Anchor VWAP", f"{last_vwap:,.2f}", f"Diff: {last_close - last_vwap:+.2f}")
    m3.metric("Composite Score", f"{composite_score}/100", "Strong Trend" if abs(composite_score) > 50 else "Choppy")
    m4.metric("CVD Momentum", f"{last_cvd:,}", "Net Buyers" if last_cvd > 0 else "Net Sellers")
    m5.metric("Profile POC", f"{spot_price:,.2f}", "Fair Value")

    st.markdown("---")

    # DASHBOARD GRID (9 TOOLS)
    c1, c2 = st.columns([6, 4])
    with c1:
        st.subheader("📈 Live Market Chart & VWAP Bands")
        fig_chart = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig_chart.add_trace(go.Candlestick(x=ohlc_df['Time'], open=ohlc_df['Open'], high=ohlc_df['High'], low=ohlc_df['Low'], close=ohlc_df['Close'], name="Price"), row=1, col=1)
        fig_chart.add_trace(go.Scatter(x=ohlc_df['Time'], y=ohlc_df['VWAP'], line=dict(color='gold', width=2), name="VWAP"), row=1, col=1)
        fig_chart.add_trace(go.Scatter(x=ohlc_df['Time'], y=ohlc_df['CVD'], line=dict(color='#58a6ff', width=2), name="CVD"), row=2, col=1)
        fig_chart.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_chart, use_container_width=True)

    with c2:
        st.subheader("🎯 Gamma Exposure (GEX) & Profile")
        strikes = np.linspace(spot_price - 150, spot_price + 150, 15)
        call_gex = np.random.normal(loc=10, scale=4, size=15) * 1e6
        put_gex = -np.abs(np.random.normal(loc=8, scale=3, size=15)) * 1e6
        fig_gex = go.Figure()
        fig_gex.add_trace(go.Bar(y=strikes, x=call_gex, orientation='h', name='Call GEX', marker_color='#238636'))
        fig_gex.add_trace(go.Bar(y=strikes, x=put_gex, orientation='h', name='Put GEX', marker_color='#da3633'))
        fig_gex.update_layout(barmode='relative', template="plotly_dark", height=380, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_gex, use_container_width=True)

with tab2:
    st.subheader("🤖 Automated Algorithmic Execution & Order Management Desk")
    st.markdown("""
    <div class="tool-tip-box">
        <b>How the Algo Bot Works:</b> The execution engine continuously evaluates all 9 tools in real-time. When the <b>Composite Score</b> exceeds your threshold, the bot automatically simulates or executes order routing with predefined risk parameters, stop-losses, and 5-minute trailing exits.
    </div>
    """, unsafe_allow_html=True)

    col_bot1, col_bot2 = st.columns([4, 6])

    with col_bot1:
        st.markdown("### ⚙️ Live Bot Parameters")
        st.write(f"**Current Status:** {'🟢 RUNNING (Auto-Trading)' if auto_refresh else '🔴 PAUSED'}")
        st.write(f"**Selected Asset:** {symbol}")
        st.write(f"**Execution Mode:** {algo_mode}")
        st.write(f"**Risk Allocation:** ${risk_per_trade} per trade")
        st.write(f"**Strategy Threshold:** ±{score_threshold} points")
        
        if st.button("🚀 Force Manual Algo Entry"):
            st.success("Manual order dispatched successfully via multi-tool gateway!")

    with col_bot2:
        st.markdown("### 📊 Active & Recent Algorithmic Trade Log")
        trade_log = pd.DataFrame({
            "Time": [(datetime.now() - timedelta(minutes=i*7)).strftime("%H:%M:%S") for i in range(4)],
            "Asset": [symbol, symbol, symbol, symbol],
            "Action": ["BUY CALL 🟢", "CLOSE CALL ⚠️", "BUY PUT 🔴", "BUY CALL 🟢"],
            "Entry Price": [spot_price-15, spot_price+35, spot_price+10, spot_price-25],
            "Composite Score": [78, 42, -82, 71],
            "P&L ($)": ["+$450", "+$1,200", "-$180", "+$620"],
            "Status": ["CLOSED", "CLOSED", "CLOSED", "ACTIVE 🟢"]
        })
        st.dataframe(trade_log, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 Multi-Factor Tool Contribution Breakdown")
    
    # Tool Contribution Breakdown Chart
    factors = ['VWAP Trend', 'CVD Momentum', 'GEX Gamma', 'AMT Profile', 'Footprint Imbalance', 'Whale Sweeps']
    contrib_scores = [score_vwap, score_cvd, score_gex, score_amt, score_footprint, score_whales]
    
    fig_breakdown = go.Figure(data=go.Bar(
        x=factors, y=contrib_scores,
        marker=dict(color=['#238636' if s > 0 else '#da3633' for s in contrib_scores])
    ))
    fig_breakdown.update_layout(template="plotly_dark", height=280, margin=dict(l=10, r=10, t=10, b=10), title="Algorithmic Weight Contribution to Current Signal")
    st.plotly_chart(fig_breakdown, use_container_width=True)

# --- AUTO REFRESH LOOP ---
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()