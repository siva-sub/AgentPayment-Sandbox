# APS API Reference

Complete API documentation for the AgentPayment Sandbox.

---

## Base URL

```
http://localhost:8080
```

---

## Mock Servers

### UCP (Universal Commerce Protocol)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mock/ucp/.well-known/ucp` | GET | Discovery profile |
| `/mock/ucp/products` | GET | List products |
| `/mock/ucp/checkout-sessions` | POST | Create session |
| `/mock/ucp/checkout-sessions/{id}` | GET | Get session |
| `/mock/ucp/checkout-sessions/{id}` | PUT | Update session |
| `/mock/ucp/checkout-sessions/{id}/complete` | POST | Complete payment |
| `/mock/ucp/checkout-sessions/{id}/cancel` | POST | Cancel session |
| `/mock/ucp/test/reset` | POST | Reset state |

**Create Session Request:**
```json
{
  "currency": "USD",
  "line_items": [{"item": {"id": "bouquet_roses"}, "quantity": 1}]
}
```

---

### ACP (Agentic Commerce Protocol)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mock/acp/.well-known/checkout` | GET | Discovery profile |
| `/mock/acp/checkout_sessions` | POST | Create session |
| `/mock/acp/checkout_sessions/{id}` | GET | Get session |
| `/mock/acp/checkout_sessions/{id}` | POST | Update session |
| `/mock/acp/checkout_sessions/{id}/complete` | POST | Complete payment |
| `/mock/acp/checkout_sessions/{id}/cancel` | POST | Cancel session |

**Headers:**
- `API-Version: 2026-01-16`
- `Idempotency-Key: {unique-key}` (optional)

---

### x402 (HTTP 402 Payment Required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mock/x402/info` | GET | Server info |
| `/mock/x402/supported` | GET | Supported networks/schemes |
| `/mock/x402/resource/{id}` | GET | Access protected resource |
| `/mock/x402/verify` | POST | Verify payment |
| `/mock/x402/settle` | POST | Settle payment |
| `/mock/x402/discovery/resources` | GET | Bazaar discovery |
| `/mock/x402/test/reset` | POST | Reset state |
| `/mock/x402/test/generate-payment` | POST | Generate test payment |

**PaymentRequired Response (402):**
```json
{
  "x402Version": 2,
  "resource": {"url": "...", "description": "..."},
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:84532",
    "amount": "10000",
    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "payTo": "0x209693Bc6afc0C5328bA36FaF03C514EF312287C"
  }]
}
```

---

### AP2 (Agent Payments Protocol)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mock/ap2/.well-known/a2a` | GET | Agent card |
| `/mock/ap2/message` | POST | A2A message handler |
| `/mock/ap2/products` | GET | List products (REST) |
| `/mock/ap2/cart` | POST | Create cart (REST) |
| `/mock/ap2/authorize` | POST | Authorize payment (REST) |
| `/mock/ap2/test/reset` | POST | Reset state |

**A2A Methods:**
- `ap2/createIntentMandate` - Create spending authorization
- `ap2/browseProducts` - Browse catalog
- `ap2/createCart` - Create cart with items
- `ap2/authorizePayment` - Authorize payment
- `ap2/getReceipt` - Get payment receipt
- `ap2/getMandateStatus` - Check mandate status
- `ap2/listPaymentMethods` - List wallet payment methods
- `ap2/selectPaymentMethod` - Select payment method
- `ap2/initiatePayment` - Initiate with OTP
- `ap2/submitOtp` - Complete OTP challenge

---

## Inspector API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/inspector/run` | POST | Run test suite |
| `/api/inspector/protocols` | GET | List protocols |
| `/api/inspector/tests/{protocol}` | GET | List tests for protocol |

**Run Test Suite Request:**
```json
{
  "target_url": "http://localhost:8080/mock/ucp",
  "protocol": "UCP"
}
```

**Test Report Response:**
```json
{
  "run_id": "run_abc123",
  "passed": 5,
  "failed": 0,
  "security_score": 100,
  "results": [...],
  "summary": "All 5 tests passed!"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid payload) |
| 402 | Payment required (x402) |
| 404 | Resource not found |
| 422 | Validation error |
| 500 | Server error |

---

## Test Helpers

Each mock provides test helpers:

```bash
# Reset all state
POST /mock/{protocol}/test/reset

# Generate valid test payment (x402)
POST /mock/x402/test/generate-payment?resource_id=premium-content

# Generate user signature (AP2)
GET /mock/ap2/test/generate-user-signature?cart_id=cart_xxx
```
