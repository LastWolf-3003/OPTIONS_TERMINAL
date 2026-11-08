import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Institutional Options & Order-Flow Terminal",
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
    .signal-card-hold { background-color: #1f242c; border: 1px solid #8b949e; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Terminal Engine Controls")
symbol = st.sidebar.selectbox("Underlying Asset", ["NIFTY 50", "BANKNIFTY", "SPX", "AAPL", "TSLA"])
spot_price = st.sidebar.number_input("Base Spot Price", value=24550.0 if "NIFTY" in symbol else 5850.0)
auto_refresh = st.sidebar.toggle("🟢 Live Stream Simulation", value=True)
refresh_rate = st.sidebar.slider("Refresh Interval (sec)", 1.0, 10.0, 2.0)

# --- GENERATE SYNTHETIC REAL-TIME DATA ---
np.random.seed(int(time.time() // 10))  # Dynamic random seed for streaming simulation
prices = np.linspace(spot_price - 120, spot_price + 120, 30)

# Generate OHLC Candlestick Data with VWAP & Multi-Std Dev Bands
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

# Calculate CVD (Cumulative Volume Delta)
ohlc_df['Delta'] = np.random.randint(-1500, 1800, size=30)
ohlc_df['CVD'] = ohlc_df['Delta'].cumsum()

# ---------------------------------------------------------
# TOP METRICS & PREDICTIVE 5-MIN SIGNAL ENGINE
# ---------------------------------------------------------
st.title(f"⚡ Institutional Order-Flow & Options Terminal — {symbol}")

# Signal Prediction Logic (5-Min Early Exit/Hold Engine)
last_close = ohlc_df['Close'].iloc[-1]
last_vwap = ohlc_df['VWAP'].iloc[-1]
last_cvd = ohlc_df['CVD'].iloc[-1]
net_gex_status = "Positive (Dealer Long)" if last_close > last_vwap else "Negative (Dealer Short)"

# Predictive Decision Model
if last_close > last_vwap and last_cvd > 2000:
    signal_type = "BULLISH ABSORPTION / RALLY IMPULSE"
    exit_timer = "Hold Position (Trend Active)"
    action_color = "signal-card-buy"
    action_label = "🟢 CALL LONG / HOLD"
    guidance = "Strong buying pressure above VWAP with high CVD. Hold position. Next target: VAH."
elif last_close < last_vwap and last_cvd < -2000:
    signal_type = "BEARISH DISTRIBUTION / DOWNWARD SQUEEZE"
    exit_timer = "⚠️ EXIT SIGNAL IN 5 MINS (Target Reached)"
    action_color = "signal-card-sell"
    action_label = "🔴 PUT LONG / CLOSE CALLS"
    guidance = "Aggressive bid absorption below VWAP. Close call positions within 5 minutes."
else:
    signal_type = "AUCTION RANGE BOUND (VAL/VAH TEST)"
    exit_timer = "⚠️ EXIT / TRIM 50% POSITION IN 5 MINS"
    action_color = "signal-card-hold"
    action_label = "🟡 NEUTRAL / TRIM POSITION"
    guidance = "Price consolidating inside Value Area. Close short-term scalp trades to lock gains."

# Display Early Warning Banner
st.markdown(f"""
<div class="{action_color}">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h3 style="margin:0; color:#ffffff !important;">{action_label}: {signal_type}</h3>
            <p style="margin:5px 0 0 0; color:#d0d7de;"><b>Guidance:</b> {guidance}</p>
        </div>
        <div style="text-align: right;">
            <h2 style="margin:0; color:#f0f6fc !important;">{exit_timer}</h2>
            <span style="font-size: 0.85rem; color:#8b949e;">Next Algorithmic Refresh: 5:00 min window</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# TOP STATS ROW
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Spot Price", f"{last_close:,.2f}", f"{(last_close - ohlc_df['Open'].iloc[-1]):+.2f}")
m2.metric("Anchor VWAP", f"{last_vwap:,.2f}", f"Diff: {last_close - last_vwap:+.2f}")
m3.metric("Cumulative Delta (CVD)", f"{last_cvd:,} Lots", "Net Buying" if last_cvd > 0 else "Net Selling")
m4.metric("GEX Hedging Regime", net_gex_status, "Low Vol" if "Positive" in net_gex_status else "High Vol")
m5.metric("Market Profile POC", f"{spot_price:,.2f}", "Point of Control")

st.markdown("---")

# ---------------------------------------------------------
# SINGLE DASHBOARD GRID (ALL 9 TOOLS UNDER ONE ROOF)
# ---------------------------------------------------------

# ROW 1: LIVE MARKET CHART (OHLC + VWAP) & GAMMA EXPOSURE (GEX)
c1, c2 = st.columns([6, 4])

with c1:
    st.subheader("📈 Live Market Chart (Candlesticks + VWAP Bands)")
    fig_chart = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    # Candlestick Trace
    fig_chart.add_trace(go.Candlestick(
        x=ohlc_df['Time'], open=ohlc_df['Open'], high=ohlc_df['High'],
        low=ohlc_df['Low'], close=ohlc_df['Close'], name="Price"
    ), row=1, col=1)
    
    # VWAP Traces
    fig_chart.add_trace(go.Scatter(x=ohlc_df['Time'], y=ohlc_df['VWAP'], line=dict(color='gold', width=2), name="VWAP"), row=1, col=1)
    fig_chart.add_trace(go.Scatter(x=ohlc_df['Time'], y=ohlc_df['VWAP_Upper'], line=dict(color='rgba(255,215,0,0.4)', dash='dash'), name="VWAP +1.5 Std"), row=1, col=1)
    fig_chart.add_trace(go.Scatter(x=ohlc_df['Time'], y=ohlc_df['VWAP_Lower'], line=dict(color='rgba(255,215,0,0.4)', dash='dash'), name="VWAP -1.5 Std"), row=1, col=1)
    
    # CVD Line Trace
    fig_chart.add_trace(go.Scatter(x=ohlc_df['Time'], y=ohlc_df['CVD'], line=dict(color='#58a6ff', width=2), name="CVD"), row=2, col=1)
    
    fig_chart.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=20, b=10), showlegend=False, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_chart, use_container_width=True)

with c2:
    st.subheader("🎯 Gamma Exposure (GEX Profile)")
    strikes = np.linspace(spot_price - 150, spot_price + 150, 15)
    call_gex = np.random.normal(loc=10, scale=4, size=15) * 1e6
    put_gex = -np.abs(np.random.normal(loc=8, scale=3, size=15)) * 1e6
    
    fig_gex = go.Figure()
    fig_gex.add_trace(go.Bar(y=strikes, x=call_gex, orientation='h', name='Call GEX', marker_color='#238636'))
    fig_gex.add_trace(go.Bar(y=strikes, x=put_gex, orientation='h', name='Put GEX', marker_color='#da3633'))
    fig_gex.add_hline(y=spot_price, line_dash="solid", line_color="cyan", annotation_text="Spot Price")
    fig_gex.update_layout(barmode='relative', template="plotly_dark", height=420, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_gex, use_container_width=True)

# ROW 2: ORDER BOOK HEATMAP & MARKET/VOLUME PROFILE (AMT)
c3, c4 = st.columns([5, 5])

with c3:
    st.subheader("🔥 Order Book Liquidity Heatmap")
    heatmap_matrix = np.random.exponential(scale=40, size=(len(prices), 15))
    times_labels = [f"T-{i}m" for i in range(15)][::-1]
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_matrix, x=times_labels, y=prices, colorscale='Viridis', colorbar=dict(title='Depth')
    ))
    fig_heat.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

with c4:
    st.subheader("🏛️ Market & Volume Profile (Auction Market Theory)")
    vol_profile = np.random.poisson(lam=12, size=len(prices))
    
    fig_profile = go.Figure(data=go.Bar(
        x=vol_profile, y=prices, orientation='h',
        marker=dict(color=np.where((prices >= spot_price - 40) & (prices <= spot_price + 40), '#388bfd', '#21262d'))
    ))
    fig_profile.add_hline(y=spot_price, line_dash="solid", line_color="gold", annotation_text="POC")
    fig_profile.add_hline(y=spot_price + 50, line_dash="dash", line_color="cyan", annotation_text="VAH")
    fig_profile.add_hline(y=spot_price - 50, line_dash="dash", line_color="cyan", annotation_text="VAL")
    fig_profile.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_profile, use_container_width=True)

# ROW 3: FOOTPRINT IMBALANCE & TIME AND SALES WHALE TRACKER
c5, c6 = st.columns([4, 6])

with c5:
    st.subheader("👣 Footprint Chart (Bid-Ask Imbalances)")
    fp_prices = prices[5:20]
    bid_vol = np.random.randint(50, 1200, size=len(fp_prices))
    ask_vol = np.random.randint(50, 1200, size=len(fp_prices))
    
    fig_fp = go.Figure(data=[
        go.Bar(name='Bid Vol (Aggressive Sell)', y=fp_prices, x=-bid_vol, orientation='h', marker_color='#da3633'),
        go.Bar(name='Ask Vol (Aggressive Buy)', y=fp_prices, x=ask_vol, orientation='h', marker_color='#238636')
    ])
    fig_fp.update_layout(barmode='overlay', template='plotly_dark', height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
    st.plotly_chart(fig_fp, use_container_width=True)

with c6:
    st.subheader("⏱️ Time & Sales (Whale Orders & Large Sweeps)")
    ts_df = pd.DataFrame({
        "Timestamp": [datetime.now().strftime("%H:%M:%S") for _ in range(6)],
        "Order Type": ["SWEEP 🐋", "BLOCK", "TRADE", "SWEEP 🐋", "BLOCK", "TRADE"],
        "Strike / Price": [spot_price+10, spot_price-5, spot_price+20, spot_price+35, spot_price-15, spot_price],
        "Size (Lots)": [1500, 800, 250, 2200, 950, 120],
        "Side / Aggressor": ["ASK (Buy)", "BID (Sell)", "ASK (Buy)", "ASK (Buy)", "BID (Sell)", "ASK (Buy)"]
    })
    st.dataframe(ts_df, use_container_width=True, height=260)

# --- AUTO REFRESH LOOP ---
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()