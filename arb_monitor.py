import requests
import time

# Token mints on Solana
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "Es9vMFrzaCERFBN5gdB34dFpgdQT1D9pU8WWvWrtCPSb"

def get_quote(input_mint, output_mint, amount):
    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,   # in smallest units (e.g. lamports)
        "slippage": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # Find Orca and Raydium routes prices from the data
        orca_price = None
        raydium_price = None
        for route in data.get("data", []):
            market_names = [market["name"].lower() for market in route.get("marketInfos", [])]
            if any("orca" in name for name in market_names):
                orca_price = route["outAmount"] / route["inAmount"]
            if any("raydium" in name for name in market_names):
                raydium_price = route["outAmount"] / route["inAmount"]
        return orca_price, raydium_price
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None, None

def monitor_arbitrage():
    amount = 10 ** 9  # 1 SOL = 1e9 lamports (smallest unit)
    while True:
        orca_price, raydium_price = get_quote(SOL_MINT, USDC_MINT, amount)
        if orca_price is None or raydium_price is None:
            print("Failed to fetch prices from one or both DEXes.")
        else:
            spread = abs(orca_price - raydium_price)
            spread_pct = (spread / min(orca_price, raydium_price)) * 100
            print(f"Orca price: {orca_price:.6f} | Raydium price: {raydium_price:.6f} | Spread: {spread_pct:.4f}%")
            if spread_pct >= 0.1:
                print("⚡ Arbitrage opportunity detected! ⚡")
        time.sleep(30)  # wait 30 seconds before checking again

if __name__ == "__main__":
    monitor_arbitrage()

