# 🧿 Ethena Remediation Strategy: Closing the Liveness Gap

To resolve the identified vulnerabilities, Ethena should implement the following technical fixes in their `StakedUSDeOFT` and bridge adapter contracts.

## 1. Resolution for Rounding Singularity (Precision Loss)
The root cause is the silent truncation of "dust" (up to $10^{12}-1$ wei) during the `ldToSd` (Local Decimals to Shared Decimals) conversion.

### The "Clean Debit" Pattern
Modify the `_debitFrom` function to ensure that only the amount that can be successfully represented on the destination chain is removed from the user's balance.

```solidity
// Proposed fix for StakedUSDeOFT.sol
function _debitFrom(
    address _from,
    uint16 _dstChainId,
    bytes32 _toAddress,
    uint _amount
) internal virtual override returns (uint) {
    // 1. Convert to shared decimals (6)
    uint64 amountShared = _ldToSd(_amount);
    
    // 2. Re-convert back to local decimals (18) to get the 'clean' amount
    uint amountClean = _sdToLd(amountShared);
    
    // 3. Ensure we only burn/lock the amount that will actually be minted on L2
    // The 'dust' (remainder) stays in the user's wallet.
    return super._debitFrom(_from, _dstChainId, _toAddress, amountClean);
}
```
**Impact:** This maintains the 1:1 invariant between L1 backing and L2 supply, as the "loss" never leaves the user's wallet on the source chain.

---

## 2. Resolution for Temporal Yield Arbitrage
The "Gap Window" exists because L2 lacks real-time knowledge of L1 reward distributions.

### Implementation: The "Price-Aware Mint"
Instead of a standard `OFT`, Ethena should use a `ProxyOFT` pattern that includes the `pricePerShare` (PPS) in the LayerZero message payload or enforces a heartbeat-based price update.

**Option A: Heartbeat Slippage (Short-term fix)**
Add a `minPricePerShare` check on the destination chain's `_nonblockingLzReceive`.

```solidity
// Proposed check in L2 receiver
function _nonblockingLzReceive(
    uint16 _srcChainId,
    bytes memory _srcAddress,
    uint64 _nonce,
    bytes memory _payload
) internal virtual override {
    // Decode PPS from payload if included, or check against local Oracle
    uint256 currentL2Price = oracle.getPrice(sUSDe);
    uint256 expectedPrice = abi.decode(_payload, (uint256, ...)).price;
    
    require(currentL2Price >= expectedPrice, "Stale L2 State: Arbitrage Blocked");
    
    super._nonblockingLzReceive(_srcChainId, _srcAddress, _nonce, _payload);
}
```

**Option B: Synchronous Rebase (Long-term fix)**
Implement the `OFT` such that it isn't just a token but a **Cross-chain Vault**.
1. **L1:** When `transferInRewards` is called, trigger a broadcast to all destination chains via LayerZero.
2. **L2:** The contract pauses `stake`/`unstake` (or uses a "pending rebase" state) until the new PPS is acknowledged.

---

## 3. Corrected Invariant Documentation
Ethena's technical documentation should be updated to explicitly state the following invariant for cross-chain consistency:

> `Invariant_01`: `L1_Locked_Assets >= sum(L2_Supply_i * L1_Exchange_Rate)`
> 
> To maintain this, any rounding remainder `r` where `r = amount % 10^{12}` must never be subtracted from the `L1_Locked_Assets` without a corresponding `L2_Supply` increase.

---
**Prepared By:** Quantum Blue Security Research
**Date:** April 19, 2026
