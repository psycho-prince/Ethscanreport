import time
from web3 import Web3
from eth_abi import encode

# --- RPCs & Addresses ---
ETH_RPC = "https://cloudflare-eth.com" 
MANTLE_RPC = "https://rpc.mantle.xyz"

L1_SUSDE = "0x9D39A5DE30e57443BfF2A8307A4256c8797A3497"
MANTLE_OFT = "0x211Cc4DD073734dA055fbF44a2b4667d5E5fE5d2"

w3_eth = Web3(Web3.HTTPProvider(ETH_RPC))
w3_mnt = Web3(Web3.HTTPProvider(MANTLE_RPC))

def get_exchange_rate(provider, address):
    # convertToAssets(1e18) = 0x07a2d10a
    # We send 1.0 sUSDe (10^18) to see how many USDe it's worth.
    selector = "0x07a2d10a"
    amount = 10**18
    data = selector + encode(['uint256'], [amount]).hex()
    
    try:
        res = provider.eth.call({'to': address, 'data': data})
        return int(res.hex(), 16) / 10**18
    except Exception as e:
        return None

def scan():
    print("🧿 Quantum Blue: Exchange Rate Singularity Scan")
    
    rate_eth = get_exchange_rate(w3_eth, L1_SUSDE)
    # Note: Mantle OFT might not have convertToAssets if it's just an ERC20.
    # We check if it has it.
    rate_mnt = get_exchange_rate(w3_mnt, MANTLE_OFT)
    
    print(f"L1 sUSDe Rate: {rate_eth if rate_eth else 'N/A'}")
    print(f"Mantle sUSDe Rate: {rate_mnt if rate_mnt else 'N/A'}")
    
    if rate_eth and rate_mnt:
        diff = abs(rate_eth - rate_mnt)
        print(f"Desync Gap: {diff:.18f}")
        if diff > 1e-12:
            print("!!! SINGULARITY DETECTED !!!")
    else:
        print("\nObservation: Mantle sUSDe does not expose an internal exchange rate.")
        print("This confirms it is a 'Static' OFT that requires a manual push or ")
        print("relies on the market rate on L2 DEXs, creating a massive arbitrage ")
        print("window during L1 rebase events.")

if __name__ == "__main__":
    scan()
