# APS Protocol Flows

This document describes the message flows for each supported protocol.

---

## UCP (Universal Commerce Protocol)

```mermaid
sequenceDiagram
    participant Agent
    participant Merchant
    participant Payment

    Agent->>Merchant: GET /.well-known/ucp
    Merchant-->>Agent: Discovery Profile

    Agent->>Merchant: POST /checkout-sessions
    Merchant-->>Agent: Session Created (id, status)

    Agent->>Merchant: PUT /checkout-sessions/{id}
    Merchant-->>Agent: Session Updated

    Agent->>Payment: Obtain Payment Token
    Payment-->>Agent: Token

    Agent->>Merchant: POST /checkout-sessions/{id}/complete
    Note over Merchant: Validate & Capture
    Merchant-->>Agent: Order Confirmation
```

---

## ACP (Agentic Commerce Protocol)

```mermaid
sequenceDiagram
    participant Agent
    participant Merchant
    participant Stripe

    Agent->>Merchant: GET /.well-known/checkout
    Note over Merchant: API-Version: 2026-01-16
    Merchant-->>Agent: Discovery + Payment Providers

    Agent->>Merchant: POST /checkout_sessions
    Merchant-->>Agent: Session (status: not_ready_for_payment)

    Agent->>Merchant: POST /checkout_sessions/{id}
    Note over Agent: Add fulfillment address
    Merchant-->>Agent: Session + Fulfillment Options

    Agent->>Merchant: POST /checkout_sessions/{id}
    Note over Agent: Select fulfillment option
    Merchant-->>Agent: Session (status: ready_for_payment)

    Agent->>Stripe: Create Payment Method
    Stripe-->>Agent: Token

    Agent->>Merchant: POST /checkout_sessions/{id}/complete
    Merchant->>Stripe: Charge
    Stripe-->>Merchant: Success
    Merchant-->>Agent: Session (status: completed)
```

---

## x402 (HTTP 402 Payment Required)

```mermaid
sequenceDiagram
    participant Client
    participant Resource Server
    participant Facilitator
    participant Blockchain

    Client->>Resource Server: GET /resource/{id}
    Resource Server-->>Client: 402 + PaymentRequired

    Note over Client: Parse accepts array
    Note over Client: Build PaymentPayload
    Note over Client: Sign with EIP-712

    Client->>Resource Server: GET /resource/{id}
    Note over Client: X-PAYMENT header

    Resource Server->>Facilitator: POST /verify
    Facilitator-->>Resource Server: isValid: true

    Resource Server->>Facilitator: POST /settle
    Facilitator->>Blockchain: transferWithAuthorization
    Blockchain-->>Facilitator: tx hash

    Facilitator-->>Resource Server: Settlement Response
    Resource Server-->>Client: 200 + Resource Content
```

---

## AP2 (Agent Payments Protocol)

### Human-Present Purchase Flow

```mermaid
sequenceDiagram
    participant User
    participant Shopping Agent
    participant Merchant Agent
    participant Credentials Provider
    participant Payment Processor

    User->>Shopping Agent: "Buy a laptop"

    Shopping Agent->>Merchant Agent: ap2/browseProducts
    Merchant Agent-->>Shopping Agent: Products List

    Shopping Agent->>User: Show options
    User->>Shopping Agent: Select laptop_pro

    Shopping Agent->>Merchant Agent: ap2/createCart
    Note over Merchant Agent: Merchant signs CartMandate
    Merchant Agent-->>Shopping Agent: CartMandate

    Shopping Agent->>User: Approve purchase?
    Note over User: Signs CartMandate

    Shopping Agent->>Credentials Provider: ap2/listPaymentMethods
    Credentials Provider-->>Shopping Agent: Cards, USDC Wallet

    User->>Shopping Agent: Use Visa ****4242
    Shopping Agent->>Credentials Provider: ap2/selectPaymentMethod
    Credentials Provider-->>Shopping Agent: selection_id

    Shopping Agent->>Payment Processor: ap2/initiatePayment
    Payment Processor-->>Shopping Agent: OTP Required

    User->>Shopping Agent: Enter OTP: 123456
    Shopping Agent->>Payment Processor: ap2/submitOtp
    Payment Processor-->>Shopping Agent: PaymentReceipt

    Shopping Agent->>User: Purchase Complete! 🎉
```

---

## Security Considerations

### Signature Verification Flow

```mermaid
flowchart TD
    A[Receive Payment] --> B{Has Signature?}
    B -->|No| C[Reject: Missing Signature]
    B -->|Yes| D[Parse Signature]
    D --> E{Valid Format?}
    E -->|No| F[Reject: Invalid Format]
    E -->|Yes| G[Recover Signer Address]
    G --> H{Matches Expected?}
    H -->|No| I[Reject: Wrong Signer]
    H -->|Yes| J[Check Nonce]
    J --> K{Nonce Used?}
    K -->|Yes| L[Reject: Replay Attack]
    K -->|No| M[Accept Payment]
```
