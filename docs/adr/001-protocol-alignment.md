# ADR-001: Using Official Protocol Specs as Source of Truth

**Date**: 2026-01-18  
**Status**: Accepted

## Context

APS (AgentPayment Sandbox) is a testing tool for agent payment protocols. Multiple protocols are supported:

| Protocol | Maintainer | Primary Spec Location |
|----------|------------|----------------------|
| AP2/A2A | Google | github.com/google-agentic-commerce/AP2 |
| ACP | OpenAI | github.com/agentic-commerce-protocol/agentic-commerce-protocol |
| x402 | Coinbase | github.com/coinbase/x402 |
| UCP | Stripe + Community | github.com/AiCommerce-Labs/universal-commerce-protocol |

## Decision

**Mock servers in APS MUST align with official specification sources:**

1. Use OpenAPI/JSON Schema definitions from official repos when available
2. Match endpoint paths, request/response formats, and status codes
3. Update mocks when upstream specs change

## Consequences

### Positive
- Test results are portable to real implementations
- Users learn actual protocol behavior
- Interoperability issues are caught early

### Negative
- Maintenance burden tracking upstream changes
- May not support protocol extensions immediately

## References

- [x402 v2 Spec](file:///home/siva/Projects/AP2/references/x402/specs/x402-specification-v2.md)
- [ACP OpenAPI](file:///home/siva/Projects/AP2/references/agentic-commerce-protocol/spec/openapi)
- [AP2 Samples](file:///home/siva/Projects/AP2/references/AP2/samples/python/scenarios)
