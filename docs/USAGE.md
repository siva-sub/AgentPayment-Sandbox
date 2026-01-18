# APS Usage Guide

This guide explains how to use the AgentPayment Sandbox for testing agent payment integrations.

---

## Table of Contents
1. [Understanding the Sandbox](#understanding-the-sandbox)
2. [Testing Scenarios](#testing-scenarios)
3. [Using Mock Servers](#using-mock-servers)
4. [Using the Inspector](#using-the-inspector)
5. [Using the Playground UI](#using-the-playground-ui)
6. [Connecting Your Agent](#connecting-your-agent)
7. [Connecting Your Merchant Backend](#connecting-your-merchant-backend)

---

## Understanding the Sandbox

### What is APS?

APS (AgentPayment Sandbox) is a **local testing environment** for AI agent commerce protocols. Think of it as:

- **Postman** for agent payments - explore and test APIs interactively
- **Mock Server** - simulate merchants/payment processors without real infrastructure  
- **Compliance Checker** - validate your implementation against official specs

### Why Use a Sandbox?

| Problem | Without Sandbox | With Sandbox |
|---------|----------------|--------------|
| Testing payments | Requires real money or test accounts | Free, instant, local |
| Protocol compliance | Manual spec reading | Automated Inspector tests |
| Edge cases | Hard to reproduce | Controllable mock responses |
| Development speed | Wait for partners | Start immediately |

### What Can You Test?

```
┌────────────────────────────────────────────────────────────────┐
│                    What APS Tests                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   Agent     │────▶│    APS      │────▶│  Protocol   │       │
│  │ (Your Code) │     │   Mocks     │     │ Compliance  │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
│  ✅ Checkout flow      ✅ Payment capture   ✅ Error handling  │
│  ✅ Signature format   ✅ Idempotency       ✅ State machine   │
│  ✅ Discovery          ✅ Mandate flow      ✅ 402 response    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Testing Scenarios

### Scenario 1: Agent Shopping Flow

Test your agent's ability to browse, add to cart, and complete purchase.

```bash
# 1. Discovery - Agent finds merchant capabilities
curl http://localhost:8080/mock/ucp/.well-known/ucp

# 2. Browse products
curl http://localhost:8080/mock/ucp/products

# 3. Create checkout
curl -X POST http://localhost:8080/mock/ucp/checkout-sessions \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD", "line_items": [{"item": {"id": "bouquet_roses"}, "quantity": 2}]}'

# 4. Complete payment
curl -X POST http://localhost:8080/mock/ucp/checkout-sessions/{id}/complete \
  -H "Content-Type: application/json" \
  -d '{"payment_data": {"token": "tok_test"}}'
```

### Scenario 2: x402 Micropayment

Test your agent paying for API access.

```bash
# 1. Request resource (get 402)
curl -i http://localhost:8080/mock/x402/resource/premium-content
# Response: 402 with X-Payment-Required header

# 2. Generate test payment
curl -X POST "http://localhost:8080/mock/x402/test/generate-payment?resource_id=premium-content"

# 3. Access with payment
curl http://localhost:8080/mock/x402/resource/premium-content \
  -H 'X-PAYMENT: {"x402Version":2,...}'
```

### Scenario 3: AP2 Mandate Flow

Test the full AP2 human-present purchase flow.

```bash
# 1. Get agent card
curl http://localhost:8080/mock/ap2/.well-known/a2a

# 2. Browse products
curl -X POST http://localhost:8080/mock/ap2/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"ap2/browseProducts","params":{}}'

# 3. Create cart mandate  
curl -X POST http://localhost:8080/mock/ap2/message \
  -d '{"jsonrpc":"2.0","id":"2","method":"ap2/createCart","params":{"items":[{"product_id":"laptop_pro","quantity":1}]}}'

# 4. Authorize payment
curl -X POST http://localhost:8080/mock/ap2/message \
  -d '{"jsonrpc":"2.0","id":"3","method":"ap2/authorizePayment","params":{"cart_mandate_id":"cart_xxx","user_authorization":"sig_xxx"}}'
```

---

## Using Mock Servers

### Available Mocks

| Mock | Base URL | Protocol |
|------|----------|----------|
| UCP | `/mock/ucp` | Universal Commerce Protocol |
| ACP | `/mock/acp` | Agentic Commerce Protocol (OpenAI) |
| x402 | `/mock/x402` | HTTP 402 Payment Required |
| AP2 | `/mock/ap2` | Agent Payments Protocol (Google) |

### Mock Behavior

- **In-Memory State**: Sessions persist until server restart
- **Reset Endpoint**: `POST /mock/{protocol}/test/reset` clears state
- **Mock Signatures**: Any properly formatted signature is accepted
- **Idempotency**: Requests with `Idempotency-Key` header are cached

### Test Helpers

```bash
# Generate valid payment for x402
POST /mock/x402/test/generate-payment?resource_id=premium-content

# Reset all x402 state
POST /mock/x402/test/reset
```

---

## Using the Inspector

The Inspector validates external servers against protocol specifications.

### Run a Test Suite

```bash
curl -X POST http://localhost:8080/api/inspector/run \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://your-merchant.com",
    "protocol": "UCP"
  }'
```

### Response

```json
{
  "run_id": "run_abc123",
  "passed": 5,
  "failed": 0,
  "security_score": 100,
  "results": [
    {"test_id": "ucp_discovery", "name": "Discovery endpoint", "passed": true},
    {"test_id": "ucp_checkout_create", "name": "Create checkout", "passed": true}
  ],
  "summary": "All 5 tests passed! Server is fully compliant with UCP."
}
```

### Available Tests

| Protocol | Tests | Focus |
|----------|-------|-------|
| UCP | 5 | Discovery, checkout CRUD, idempotency |
| ACP | 3 | Discovery, session states |
| x402 | 2 | Info, 402 response |
| AP2 | 2 | Agent card, message handler |

---

## Using the Playground UI

The Playground provides an interactive protocol explorer.

### Access
```
http://localhost:5173
```

### Features

1. **Protocol Selector** - Switch between AP2, x402, UCP
2. **Step Navigator** - Walk through protocol flows step-by-step
3. **Payload Editor** - Edit JSON payloads before sending
4. **Execute Button** - Send request to mock server
5. **Response Panel** - View server response with formatting
6. **Validation Cards** - See security warnings and score

---

## Connecting Your Agent

### Python Example

```python
import httpx

# Point your agent at APS instead of real merchant
APS_BASE = "http://localhost:8080/mock/ucp"

async def agent_checkout():
    async with httpx.AsyncClient() as client:
        # Discovery
        discovery = await client.get(f"{APS_BASE}/.well-known/ucp")
        
        # Create checkout
        checkout = await client.post(
            f"{APS_BASE}/checkout-sessions",
            json={
                "currency": "USD",
                "line_items": [{"item": {"id": "bouquet_roses"}, "quantity": 1}]
            }
        )
        session = checkout.json()
        
        # Complete payment
        result = await client.post(
            f"{APS_BASE}/checkout-sessions/{session['id']}/complete",
            json={"payment_data": {"token": "tok_test"}}
        )
        return result.json()
```

### JavaScript Example

```javascript
const APS_BASE = "http://localhost:8080/mock/x402";

async function payForResource(resourceId) {
  // Try to access (get 402)
  let response = await fetch(`${APS_BASE}/resource/${resourceId}`);
  
  if (response.status === 402) {
    // Generate test payment
    const payment = await fetch(
      `${APS_BASE}/test/generate-payment?resource_id=${resourceId}`,
      { method: "POST" }
    ).then(r => r.json());
    
    // Retry with payment
    response = await fetch(`${APS_BASE}/resource/${resourceId}`, {
      headers: { "X-PAYMENT": payment.x_payment_header }
    });
  }
  
  return response.json();
}
```

---

## Connecting Your Merchant Backend

If you're building a merchant server, use the Inspector to validate your implementation.

### Step 1: Implement Protocol Endpoints

```python
# Your merchant server
from fastapi import FastAPI

app = FastAPI()

@app.get("/.well-known/ucp")
async def ucp_discovery():
    return {
        "name": "My Store",
        "version": "1.0",
        "payment": {"handlers": [{"id": "stripe", "name": "Stripe"}]}
    }

@app.post("/checkout-sessions")
async def create_checkout(request: dict):
    # Your implementation
    pass
```

### Step 2: Run Inspector

```bash
# Start your server
uvicorn yourserver:app --port 9000

# Validate against spec
curl -X POST http://localhost:8080/api/inspector/run \
  -d '{"target_url": "http://localhost:9000", "protocol": "UCP"}'
```

### Step 3: Fix Issues

The Inspector returns specific recommendations:
```json
{
  "test_id": "ucp_discovery",
  "passed": false,
  "error": "Missing required field: payment",
  "recommendation": "Include 'payment' in the response"
}
```
