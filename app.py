import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Institutional Options & Order-Flow Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Bloomberg/Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stSidebar { background-color: #161b22; }
    h1, h2, h3 { color: #58a6ff !important; }
    .metric-card { background-color: #21262d; border: 1px solid #30363d; padding: 15px; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("⚙️ Terminal Controls")
symbol = st.sidebar.selectbox("Underlying Asset", ["NIFTY 50", "SPX", "BANKNIFTY", "AAPL", "TSLA"])
spot_price = st.sidebar.number_input("Base Spot Price", value=24550.0 if "NIFTY" in symbol else 5850.0)
update_speed = st.sidebar.slider("Tick Refresh Rate (s)", 0.5, 5.0, 1.0)
live_feed = st.sidebar.toggle("🟢 Live Stream Simulation", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Analytical Modules")
active_tab = st.sidebar.radio("Select View", [
    "Decision Matrix & Overview",
    "Order Book Heatmap & Depth",
    "Footprint & Delta",
    "Market Profile (TPO) & AMT",
    "Gamma Exposure (GEX)"
])

# Synthetic Data Generation Helpers
np.random.seed(42)
prices = np.linspace(spot_price - 100, spot_price + 100, 40)

def generate_heatmap_data():
    depth = np.random.exponential(scale=50, size=(len(prices), 20))
    return depth

def generate_gex_data():
    strikes = np.linspace(spot_price - 200, spot_price + 200, 25)
    call_gex = np.random.normal(loc=15, scale=5, size=25) * 1e6
    put_gex = -np.abs(np.random.normal(loc=12, scale=4, size=25)) * 1e6
    return strikes, call_gex, put_gex

# --- MODULE 1: DECISION MATRIX & OVERVIEW ---
if active_tab == "Decision Matrix & Overview":
    st.title(f"⚡ Institutional Order Flow & GEX Terminal — {symbol}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Spot Price", f"{spot_price:,.2f}", "+0.45%")
    with col2:
        st.metric("Net Gamma Regime", "Positive (Mean Reverting)", "Dealer Long")
    with col3:
        st.metric("Cumulative Delta (CVD)", "+14,250 Lots", "Aggressive Buying")
    with col4:
        st.metric("Zero-Gamma Flip", f"{spot_price - 85:,.2f}", "Key Pivot")
        
    st.markdown("### 🤖 Algorithmic Decision & Setup Matrix")
    
    signals_df = pd.DataFrame([
        {
            "Strategy": "Gamma Pin / Squeeze",
            "Bias": "Bullish",
            "Entry Zone": f"{spot_price - 20:,.2f} - {spot_price:,.2f}",
            "Stop Loss": f"{spot_price - 65:,.2f}",
            "Target 1": f"{spot_price + 75:,.2f}",
            "Target 2": f"{spot_price + 140:,.2f}",
            "Confidence": "High (88%)"
        },
        {
            "Strategy": "Value Area Breakout (AMT)",
            "Bias": "Neutral-Bullish",
            "Entry Zone": "VAL Test (Value Area Low)",
            "Stop Loss": "VAL - 30 pts",
            "Target 1": "Point of Control (POC)",
            "Target 2": "Value Area High (VAH)",
            "Confidence": "Moderate (74%)"
        }
    ])
    st.dataframe(signals_df, use_container_width=True)
    
    # Real-time Time & Sales feed
    st.subheader("⏱️ Live Time & Sales (Whale Tracker)")
    ts_data = pd.DataFrame({
        "Time": [datetime.now().strftime("%H:%M:%S") for _ in range(5)],
        "Type": ["SWEEP 🐋", "BLOCK", "TRADE", "SWEEP 🐋", "TRADE"],
        "Strike/Price": [spot_price+20, spot_price-10, spot_price+5, spot_price+50, spot_price-5],
        "Size (Contracts)": [1250, 500, 150, 2100, 85],
        "Side": ["ASK (Buy)", "BID (Sell)", "ASK (Buy)", "ASK (Buy)", "BID (Sell)"]
    })
    st.table(ts_data)

# --- MODULE 2: ORDER BOOK HEATMAP ---
elif active_tab == "Order Book Heatmap & Depth":
    st.title("🔥 Order Book Liquidity Heatmap & Depth")
    st.markdown("Visualizes resting limit order clusters across strikes to identify institutional iceberg orders.")
    
    depth_matrix = generate_heatmap_data()
    times = [f"10:{i:02d}" for i in range(20)]
    
    fig = go.Figure(data=go.Heatmap(
        z=depth_matrix,
        x=times,
        y=prices,
        colorscale='Viridis',
        colorbar=dict(title='Liquidity Depth')
    ))
    fig.update_layout(
        title=f"{symbol} - Depth of Book Liquidity Heatmap",
        xaxis_title="Time Horizon",
        yaxis_title="Strike / Price Level",
        template="plotly_dark",
        height=650
    )
    st.plotly_chart(fig, use_container_width=True)

# --- MODULE 3: FOOTPRINT & DELTA ---
elif active_tab == "Footprint & Delta":
    st.title("👣 Footprint Chart & Bid-Ask Imbalances")
    st.markdown("Diagonal delta calculations highlighting aggressive buying vs. selling absorption.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fp_prices = prices[10:30]
        bid_vol = np.random.randint(100, 2000, size=len(fp_prices))
        ask_vol = np.random.randint(100, 2000, size=len(fp_prices))
        
        fig = go.Figure(data=[
            go.Bar(name='Bid Volume (Aggressive Sell)', y=fp_prices, x=-bid_vol, orientation='h', marker_color='indianred'),
            go.Bar(name='Ask Volume (Aggressive Buy)', y=fp_prices, x=ask_vol, orientation='h', marker_color='mediumseagreen')
        ])
        fig.update_layout(barmode='overlay', template='plotly_dark', title="Footprint Volume Delta Profile", height=600)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### Cumulative Volume Delta (CVD)")
        cvd_series = np.cumsum(np.random.randint(-500, 600, size=30))
        st.line_chart(cvd_series)

# --- MODULE 4: MARKET PROFILE (TPO) & AMT ---
elif active_tab == "Market Profile (TPO) & AMT":
    st.title("🏛️ Market Profile (TPO) & Auction Market Theory")
    st.markdown("Tracking Value Area High (VAH), Value Area Low (VAL), and Point of Control (POC).")
    
    tpo_counts = np.random.poisson(lam=10, size=len(prices))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tpo_counts,
        y=prices,
        orientation='h',
        marker=dict(
            color=np.where((prices >= spot_price - 30) & (prices <= spot_price + 30), '#58a6ff', '#30363d')
        )
    ))
    
    # Add VAH, VAL, POC lines
    poc = spot_price
    vah = spot_price + 45
    val = spot_price - 45
    
    fig.add_hline(y=poc, line_dash="solid", line_color="gold", annotation_text="POC (Point of Control)")
    fig.add_hline(y=vah, line_dash="dash", line_color="cyan", annotation_text="VAH (Value Area High)")
    fig.add_hline(y=val, line_dash="dash", line_color="cyan", annotation_text="VAL (Value Area Low)")
    
    fig.update_layout(title="Auction Market Theory TPO Distribution", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

# --- MODULE 5: GAMMA EXPOSURE (GEX) ---
elif active_tab == "Gamma Exposure (GEX)":
    st.title("🎯 Gamma Exposure (GEX) & Dealer Hedging Profile")
    st.markdown("Strike-by-strike dealer net gamma. Positive GEX dampens volatility; Negative GEX accelerates moves.")
    
    strikes, call_gex, put_gex = generate_gex_data()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Call GEX (Dealer Short Gamma)', x=strikes, y=call_gex, marker_color='green'))
    fig.add_trace(go.Bar(name='Put GEX (Dealer Long Gamma)', x=strikes, y=put_gex, marker_color='red'))
    
    fig.update_layout(
        barmode='relative',
        title=f"{symbol} - Dealer Gamma Exposure Profile by Strike",
        xaxis_title="Strike Price",
        yaxis_title="Gamma Exposure ($ Notional / 1% Move)",
        template="plotly_dark",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

# Auto-refresh loop for live mode simulation
if live_feed:
    time.sleep(update_speed)
    st.rerun()