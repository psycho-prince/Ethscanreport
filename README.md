# 🧿 Quantum Blue: Ethena Entropy Scan (Mantle)

## Mission Objective
Identify **Cross-Chain State Desynchronization** and **Logic Singularities** in the Ethena `StakedUSDeOFT` contract on the Mantle Network. Potential bounty value: **$3,000,000**.

## Target Contracts
- **sUSDe (StakedUSDeOFT):** `0x211Cc4DD073734dA055fbF44a2b4667d5E5fE5d2`
- **USDe:** `0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34`

## Scan Sub-routines

### Sub-routine B: The "Vesting Entropy" Leak
- **The Logic:** Ethena yield vests linearly over 8 hours on Ethereum L1.
- **The Singularity:** Check if the OFT bridging mechanism allows users to bypass this vesting by moving `sUSDe` to Mantle immediately after a reward distribution on L1.
- **Invariant:** `totalAssets` (vested) / `totalSupply` (shares) must be consistent across the bridge.

### Sub-routine C: The "Rounding Singularity"
- **The Logic:** LayerZero OFTs often use `sharedDecimals` (e.g., 6) which is lower than the standard 18 decimals.
- **The Singularity:** High-frequency, small-amount transfers may lead to 1-wei rounding errors that accumulate into protocol insolvency or "infinite mint" scenarios.
- **Check:** Monitor `sharedDecimals` vs `decimals`.

## Execution
Run the scanner script:
```bash
python3 ethena_fork_scanner.py
```

## Security Status
- **Framework:** Quantum Blue Entropy Mapping
- **Status:** Simulation Mode (Mantle Mainnet RPC)
- **Encryption:** PQC-Ready (ML-KEM-768)
