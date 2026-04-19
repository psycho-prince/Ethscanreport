import os
import time
from web3 import Web3
from eth_abi import encode

# --- CONFIGURATION ---
# Using public Mantle RPC for initial scan
MANTLE_RPC = "https://rpc.mantle.xyz"
# Ethena sUSDe (StakedUSDeOFT) on Mantle
STAKED_USDE_MANTLE = "0x211Cc4DD073734dA055fbF44a2b4667d5E5fE5d2"
# Ethena USDe on Mantle
USDE_MANTLE = "0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34"

# Minimal ABIs for the scan
SUSDE_ABI = [
    {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    # LayerZero OFT functions
    {"inputs": [], "name": "sharedDecimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
]

USDE_ABI = [
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
]

def run_quantum_blue_scan():
    print("🧿 Quantum Blue v2.0.0: Ethena Entropy Scan Initiated")
    print(f"Target: StakedUSDeOFT (Mantle) @ {STAKED_USDE_MANTLE}")
    
    w3 = Web3(Web3.HTTPProvider(MANTLE_RPC))
    if not w3.is_connected():
        print("Error: Could not connect to Mantle RPC.")
        return

    latest_block = w3.eth.block_number
    print(f"Connected to Mantle. Latest Block: {latest_block}")

    susde = w3.eth.contract(address=STAKED_USDE_MANTLE, abi=SUSDE_ABI)
    usde = w3.eth.contract(address=USDE_MANTLE, abi=USDE_ABI)

    print("\n--- Sub-routine B: Vesting Entropy Leak ---")
    total_supply_susde = susde.functions.totalSupply().call()
    decimals_susde = susde.functions.decimals().call()
    
    # On Mantle, sUSDe is an OFT. We check if it holds underlying USDe or if it's purely a mint/burn bridge.
    # Often, the OFT contract itself or a proxy holds the assets if it's not a native mint.
    contract_usde_balance = usde.functions.balanceOf(STAKED_USDE_MANTLE).call()
    
    print(f"sUSDe Total Supply (Mantle): {total_supply_susde / 10**decimals_susde:,.2f}")
    print(f"USDe held by sUSDe Contract: {contract_usde_balance / 10**18:,.2f}")

    # Logic: If sUSDe is supposed to be backed 1:1 by USDe on this chain (which it usually isn't for OFT v2),
    # we'd check for a gap. For OFT, the "Singularity" is the exchange rate desync.
    
    # --- Sub-routine C: Rounding Singularity ---
    print("\n--- Sub-routine C: Rounding Singularity Check ---")
    try:
        shared_decimals = susde.functions.sharedDecimals().call()
        print(f"Shared Decimals (LayerZero): {shared_decimals}")
        if shared_decimals < decimals_susde:
            precision_loss = 10**(decimals_susde - shared_decimals)
            print(f"Alert: Precision loss detected during bridging! Factor: {precision_loss}")
            print("Potential for 1-wei rounding entropy accumulation.")
    except Exception as e:
        print(f"Shared Decimals check skipped: {e}")

    print("\n--- Invariant Monitor ---")
    # Monitor: If sUSDe supply on Mantle ever exceeds the global locked amount (requires multi-chain scan)
    # For now, we flag if local assets < local shares (if applicable)
    if contract_usde_balance > 0 and total_supply_susde > contract_usde_balance:
        print("!!! CRITICAL: LOCAL INSOLVENCY DETECTED !!!")
        print(f"Gap: {(total_supply_susde - contract_usde_balance) / 10**decimals_susde:,.2f} tokens")
    else:
        print("Invariant Check: Local state remains within expected entropy bounds.")

    print("\nScan Complete. Report Generated.")

if __name__ == "__main__":
    run_quantum_blue_scan()
