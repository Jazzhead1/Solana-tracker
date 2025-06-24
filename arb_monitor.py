import requests
import time

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "Es9vMFrzaCERFBN5gdB34dFpgdQT1D9pU8WWvWrtCPSb"
HEADERS = {"User-Agent": "ArbSurferBot/1.0"}

def get_price_for_dex(input_mint, output_mint, amount, dex_name):
    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,
        "slippage": 1,
        "onlyDirectRoutes": True  # direct routes only
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        for route in data.get("data", []):
            markets = [m["name"].lower() for m in route.get("marketInfos", [])]
            if any(dex_name.lower() in m for m in markets):
                price = float(route["outAmount"]) / float(route["inAmount"])
                return price
        print(f"⚠️ No direct {dex_name} route found for this pair.")
        return None
    except Exception as e:
        print(f"Error fetching price for {dex_name}: {e}")
        return None

def monitor_arbitrage():
    amount = 10**9  # 1 SOL in lamports
    while True:
        orca_price = get_price_for_dex(SOL_MINT, USDC_MINT, amount, "orca")
        raydium_price = get_price_for_dex(SOL_MINT, USDC_MINT, amount, "raydium")
        if orca_price is None or raydium_price is None:
            print("Failed to fetch prices from one or both DEXes.")
        else:
            spread = abs(orca_price - raydium_price)
            spread_pct = (spread / min(orca_price, raydium_price)) * 100
            print(f"Orca price: {orca_price:.6f} | Raydium price: {raydium_price:.6f} | Spread: {spread_pct:.4f}%")
            if spread_pct >= 0.1:
                print("⚡ Arbitrage opportunity detected! ⚡")
        time.sleep(30)

if __name__ == "__main__":
    monitor_arbitrage()
