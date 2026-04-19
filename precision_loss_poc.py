import math

def simulate_precision_loss():
    print("🧿 Quantum Blue: Rounding Singularity (Precision Loss) PoC")
    
    # Configuration based on Ethena StakedUSDeOFT (Mantle)
    LOCAL_DECIMALS = 18
    SHARED_DECIMALS = 6
    CONVERSION_RATE = 10 ** (LOCAL_DECIMALS - SHARED_DECIMALS) # 10^12
    
    # Attack Scenario: 10,000 micro-transfers designed to trigger rounding
    num_transactions = 10000
    
    # Amount: 1.000000000000999999 tokens (just under the next shared decimal unit)
    # This maximizes the truncation loss per transaction.
    amount_ld = (1 * 10**18) + (CONVERSION_RATE - 1) 
    
    print(f"--- Simulation Parameters ---")
    print(f"Local Decimals: {LOCAL_DECIMALS}")
    print(f"Shared Decimals: {SHARED_DECIMALS}")
    print(f"Truncation Factor: {CONVERSION_RATE}")
    print(f"Amount per TX (Wei): {amount_ld}")
    print(f"Number of TXs: {num_transactions}")

    total_burned_l1 = 0
    total_minted_l2 = 0

    for i in range(num_transactions):
        # 1. Source Chain: Truncation happens before sending the message
        amount_sd = amount_ld // CONVERSION_RATE
        
        # 2. Amount actually burned on L1 (the full amount the user sent)
        burned = amount_ld 
        
        # 3. Destination Chain: Re-inflated to local decimals
        minted = amount_sd * CONVERSION_RATE
        
        total_burned_l1 += burned
        total_minted_l2 += minted

    total_loss = total_burned_l1 - total_minted_l2
    loss_percentage = (total_loss / total_burned_l1) * 100

    print("\n--- Results ---")
    print(f"Total USDe Burned (L1): {total_burned_l1 / 10**18:.18f}")
    print(f"Total USDe Minted (L2): {total_minted_l2 / 10**18:.18f}")
    print(f"Total Value Lost to Entropy: {total_loss / 10**18:.18f} USDe")
    print(f"Loss Percentage: {loss_percentage:.10f}%")

    print("\n--- Security Impact ---")
    print("1. Protocol Insolvency: If the bridge adapter tracks totalAssets based on L1 deposits")
    print("   but totalSupply is minted on L2, the 1:1 invariant is permanently broken.")
    print("2. Yield Dilution: This 'dust' is essentially stolen from the global staking pool")
    print("   and trapped in the bridge contract or lost to the void.")
    print("3. Systematic Drain: An automated bot could execute millions of these transfers")
    print("   to intentionally de-peg the sUSDe exchange rate on destination chains.")

if __name__ == "__main__":
    simulate_precision_loss()
