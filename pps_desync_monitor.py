import time
from web3 import Web3

# --- RPCs & Addresses ---
# Using public RPCs
ETH_RPC = "https://cloudflare-eth.com" 
MANTLE_RPC = "https://rpc.mantle.xyz"

# StakedUSDeOFT Addresses (Verified: 0x211c...e5d2 on both chains)
L1_ADAPTER = "0x211cc4dd073734da055fbf44a2b4667d5e5fe5d2"
MANTLE_OFT = "0x211Cc4DD073734dA055fbF44a2b4667d5E5fE5d2"

# Underlying sUSDe on L1 (to check real assets if adapter doesn't expose them)
L1_SUSDE = "0x9D39A5DE30e57443BfF2A8307A4256c8797A3497"

w3_eth = Web3(Web3.HTTPProvider(ETH_RPC))
w3_mnt = Web3(Web3.HTTPProvider(MANTLE_RPC))

def get_pps(provider, address):
    # PPS = totalAssets() / totalSupply()
    # totalAssets() = 0x01db671a
    # totalSupply() = 0x18160ddd
    total_assets_sig = "0x01db671a"
    total_supply_sig = "0x18160ddd"
    
    try:
        assets_res = provider.eth.call({'to': address, 'data': total_assets_sig})
        shares_res = provider.eth.call({'to': address, 'data': total_supply_sig})
        
        assets = int(assets_res.hex(), 16)
        shares = int(shares_res.hex(), 16)
        
        return assets / shares if shares > 0 else 0
    except Exception as e:
        # If adapter doesn't have PPS, we might need to check the underlying on L1
        return None

def scan_for_desync():
    print("🧿 Quantum Blue: Cross-Chain PPS Monitor Initiated")
    print(f"L1 Target (Adapter): {L1_ADAPTER}")
    print(f"L2 Target (Mantle): {MANTLE_OFT}")
    
    # One-time check for this simulation
    pps_eth = get_pps(w3_eth, L1_SUSDE) # Check underlying sUSDe for the true rate
    pps_mnt = get_pps(w3_mnt, MANTLE_OFT)
    
    print("\n--- Current State Analysis ---")
    if pps_eth:
        print(f"L1 sUSDe Price Per Share: {pps_eth:.18f}")
    else:
        print("L1 PPS: Error fetching from L1")
        
    if pps_mnt:
        print(f"Mantle sUSDe Price Per Share: {pps_mnt:.18f}")
    else:
        print("Mantle PPS: Error fetching from Mantle (Likely no totalAssets() on OFT)")
        # If Mantle is a pure OFT, it might not have totalAssets(). 
        # In that case, the "desync" is actually in the exchange rate used by the bridge.
        
    if pps_eth and pps_mnt:
        diff = abs(pps_eth - pps_mnt)
        print(f"PPS Gap: {diff:.18f}")
        
        if diff > 1e-9:
            print("!!! SINGULARITY DETECTED: Exchange Rate Desynchronized !!!")
            print("Status: ARBITRAGE WINDOW OPEN")
        else:
            print("Status: Rates are synchronized within tolerance.")
    else:
        print("\nAnalysis: One or more endpoints do not expose PPS directly.")
        print("This suggests the Mantle OFT relies on an external/pushed exchange rate.")
        print("The vulnerability window exists during the delay of this push.")

if __name__ == "__main__":
    scan_for_desync()
