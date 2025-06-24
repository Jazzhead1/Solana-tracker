import streamlit as st
import requests

st.set_page_config(page_title="DEX Arbitrage Monitor", layout="wide")
st.title("💹 Orca (via Jupiter Lite) vs Raydium Arbitrage Monitor (SOL/USDT)")

def get_orca_price_jupiter():
    try:
        url = "https://lite-api.jup.ag/quote"
        params = {
            "inputMint": "So11111111111111111111111111111111111111112",
            "outputMint": "Es9vMFrzaCERFBN5gdB34dFpgdQT1D9pU8WWvWrtCPSb",
            "amount": str(10_000_000),  # 0.01 SOL in lamports
            "slippageBps": 100  # 1% slippage
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        out = float(data["outAmount"]) / 1e6
        return out
    except Exception as e:
        st.error(f"❌ Jupiter Lite fetch failed: {e}")
        return None

def get_raydium_price():
    try:
        resp = requests.get("https://api.raydium.io/pairs")
        resp.raise_for_status()
        for pair in resp.json():
            if pair.get("name") == "SOL/USDT":
                return float(pair["price"])
        st.warning("⚠️ SOL/USDT not found on Raydium")
        return None
    except Exception as e:
        st.error(f"❌ Raydium fetch failed: {e}")
        return None

if st.button("🔄 Refresh"):
    st.experimental_rerun()

o_price = get_orca_price_jupiter()
r_price = get_raydium_price()

if o_price and r_price:
    spread = abs(o_price - r_price)
    pct = (spread / min(o_price, r_price)) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("⚓ Jupiter (SOL→USDT)", f"${o_price:.4f}")
    c2.metric("🧪 Raydium", f"${r_price:.4f}")
    c3.metric("📈 Spread %", f"{pct:.2f}%")

    if pct >= 0.1:
        st.success("🚨 Arbitrage opportunity detected (≥ 0.1%)")
    else:
        st.info("📉 No arbitrage above 0.1%")
else:
    st.warning("⚠️ Failed to fetch both prices")

