import streamlit as st
import requests

st.set_page_config(page_title="DEX Arbitrage Monitor", layout="wide")
st.title("💹 Orca vs Raydium Arbitrage Monitor (SOL/USDT)")

# Constants
ORCA_API = "https://api.mainnet.orca.so/v1/quote"
RAYDIUM_API = "https://api.raydium.io/pairs"

def get_orca_price():
    try:
        response = requests.get(ORCA_API, params={
            "inputMint": "So11111111111111111111111111111111111111112",   # SOL
            "outputMint": "Es9vMFrzaCERFBN5gdB34dFpgdQT1D9pU8WWvWrtCPSb",  # USDT
            "amount": str(10_000_000),  # 0.01 SOL in lamports
            "slippage": "1"
        }, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        data = response.json()
        return float(data["outAmount"]) / 1e6
    except Exception as e:
        st.error(f"❌ Orca fetch failed: {e}")
        return None

def get_raydium_price():
    try:
        response = requests.get(RAYDIUM_API)
        response.raise_for_status()
        for pair in response.json():
            if pair.get("name") == "SOL/USDT":
                return float(pair["price"])
        return None
    except Exception as e:
        st.error(f"❌ Raydium fetch failed: {e}")
        return None

# Manual refresh
if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

# Price fetching
orca_price = get_orca_price()
raydium_price = get_raydium_price()

# Display results
if orca_price and raydium_price:
    spread = abs(orca_price - raydium_price)
    spread_pct = (spread / min(orca_price, raydium_price)) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Orca Price", f"${orca_price:.4f}")
    col2.metric("Raydium Price", f"${raydium_price:.4f}")
    col3.metric("Spread %", f"{spread_pct:.2f}%")

    if spread_pct >= 0.1:
        st.success("🚨 Arbitrage opportunity! Spread ≥ 0.1%")
    else:
        st.info("📉 No arbitrage opportunity > 0.1%")
else:
    st.warning("⚠️ Failed to load both prices.")
