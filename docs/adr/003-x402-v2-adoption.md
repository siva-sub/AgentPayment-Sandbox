# ADR-003: Adoption of x402 Protocol Version 2

**Date**: 2026-01-18  
**Status**: Accepted

## Context

x402 has two protocol versions:

| Feature | v1 | v2 |
|---------|----|----|
| Network IDs | `base-sepolia` | `eip155:84532` (CAIP-2) |
| Payment Header | Simple JSON | Full PaymentPayload |
| Discovery | `/info` | `/supported` + Bazaar |

## Decision

**APS implements x402 v2** exclusively.

### Key v2 Features Implemented

1. **CAIP-2 Network Identifiers**
   ```python
   DEFAULT_NETWORK = "eip155:84532"  # Base Sepolia
   ```

2. **PaymentRequired with `accepts` Array**
   ```json
   {
     "x402Version": 2,
     "resource": {"url": "...", "description": "..."},
     "accepts": [{"scheme": "exact", "network": "eip155:84532", ...}]
   }
   ```

3. **PaymentPayload with EIP-3009 Authorization**
   ```json
   {
     "x402Version": 2,
     "accepted": {...},
     "payload": {
       "signature": "0x...",
       "authorization": {"from": "...", "to": "...", "value": "...", "nonce": "..."}
     }
   }
   ```

4. **Facilitator API**
   - `POST /verify` - Validate without settling
   - `POST /settle` - Execute on-chain
   - `GET /supported` - List supported schemes/networks

## Consequences

### Positive
- Future-proof: v2 is the direction of the protocol
- CAIP-2 enables multi-chain support
- Facilitator abstraction allows testing without blockchain

### Negative
- v1 clients cannot use APS mocks directly
- More complex response structures

## References

- [x402 v2 Specification](file:///home/siva/Projects/AP2/references/x402/specs/x402-specification-v2.md)
- [CAIP-2 Standard](https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-2.md)
