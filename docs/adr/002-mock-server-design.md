# ADR-002: Mock Server Design

**Date**: 2026-01-18  
**Status**: Accepted

## Context

APS mock servers simulate merchant/payment backends. Key design questions:

1. State management: In-memory vs persistent?
2. Test isolation: Shared state vs per-session?
3. Realistic behavior: Delay simulation, failure modes?

## Decision

### 1. In-Memory State
Mock servers use Python dictionaries, not databases:
```python
_sessions: dict[str, dict[str, Any]] = {}
_nonces: set[str] = set()
```

**Rationale**: Simplicity. Restart clears state automatically.

### 2. Test Isolation via `/test/reset`
Each mock provides a reset endpoint:
```python
@router.post("/test/reset")
async def reset_test_state():
    _sessions.clear()
    _nonces.clear()
    return {"status": "reset"}
```

### 3. Idempotency Support
Requests with `Idempotency-Key` header are cached and return identical responses on retry.

### 4. Mock Signatures
Signatures are not cryptographically verified - any properly formatted signature is accepted. This enables testing without wallet setup.

## Consequences

### Positive
- Zero dependencies beyond FastAPI
- Fast test execution
- Easy to understand and modify

### Negative
- State lost on restart (use Inspector for persistence)
- Not suitable for load testing
- No actual crypto verification

## Implementation

| Mock | State Variables | Reset Endpoint |
|------|----------------|----------------|
| UCP | `_sessions`, `_orders` | `/test/reset` |
| ACP | `_sessions`, `_idempotency_cache` | N/A (add if needed) |
| x402 | `_payments`, `_nonces`, `_settlements` | `/test/reset` |
| AP2 | `_mandates`, `_receipts` | `/test/reset` |
