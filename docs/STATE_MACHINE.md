# APS State Machines

This document describes the state machines for sessions and payments across protocols.

---

## Checkout Session States

All protocols follow a similar session lifecycle:

```mermaid
stateDiagram-v2
    [*] --> Created: Create Session

    Created --> NotReady: Items Added
    NotReady --> Ready: Fulfillment Selected

    Ready --> Processing: Payment Submitted
    Processing --> Completed: Payment Success
    Processing --> Failed: Payment Declined

    NotReady --> Canceled: User Cancels
    Ready --> Canceled: User Cancels

    Completed --> [*]
    Canceled --> [*]
    Failed --> Ready: Retry
```

### UCP Session States

| State | Description | Allowed Actions |
|-------|-------------|-----------------|
| `created` | Session initialized | Update, Cancel |
| `ready` | Ready for payment | Complete, Cancel |
| `completed` | Payment captured | None |
| `cancelled` | Session cancelled | None |

### ACP Session States

| State | Description | Transition Condition |
|-------|-------------|---------------------|
| `not_ready_for_payment` | Missing fulfillment | Add address + select option |
| `ready_for_payment` | Can submit payment | Fulfillment complete |
| `completed` | Order placed | Payment success |
| `canceled` | Session cancelled | User or timeout |

---

## AP2 Mandate States

### IntentMandate Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PendingSignature: Create Intent

    PendingSignature --> Active: User Signs
    PendingSignature --> Rejected: User Rejects

    Active --> Exhausted: Limit Reached
    Active --> Expired: Time Expired
    Active --> Revoked: User Revokes

    Exhausted --> [*]
    Expired --> [*]
    Revoked --> [*]
    Rejected --> [*]
```

### CartMandate Lifecycle

```mermaid
stateDiagram-v2
    [*] --> AwaitingApproval: Merchant Creates

    AwaitingApproval --> UserApproved: User Signs
    AwaitingApproval --> UserRejected: User Rejects
    AwaitingApproval --> Expired: Timeout

    UserApproved --> PaymentPending: Initiate Payment
    PaymentPending --> OtpRequired: Card Payment
    PaymentPending --> Completed: x402 Payment

    OtpRequired --> Completed: OTP Valid
    OtpRequired --> Failed: OTP Invalid

    Completed --> [*]
    Failed --> [*]
    Expired --> [*]
    UserRejected --> [*]
```

---

## x402 Payment States

```mermaid
stateDiagram-v2
    [*] --> PaymentRequired: Access Resource

    PaymentRequired --> PayloadReceived: Submit Payment
    PayloadReceived --> Verifying: Parse Payload

    Verifying --> Valid: Signature OK
    Verifying --> Invalid: Validation Failed

    Valid --> Settling: Call Settle
    Settling --> Settled: TX Confirmed
    Settling --> Failed: TX Failed

    Settled --> [*]: Return Resource
    Invalid --> PaymentRequired: Try Again
    Failed --> PaymentRequired: Try Again
```

### Verification Checks

| Check | Error Code | Description |
|-------|------------|-------------|
| Version | `invalid_x402_version` | Must be 2 |
| Signature | `invalid_exact_evm_payload_signature` | EIP-712 invalid |
| Amount | `invalid_exact_evm_payload_authorization_value` | Insufficient |
| Recipient | `invalid_exact_evm_payload_recipient_mismatch` | Wrong payTo |
| Time Window | `invalid_exact_evm_payload_authorization_valid_*` | Time expired |
| Nonce | `nonce_already_used` | Replay attack |

---

## OTP Challenge States

```mermaid
stateDiagram-v2
    [*] --> Generated: Create Challenge

    Generated --> Pending: OTP Sent
    Pending --> Validated: Correct OTP
    Pending --> Retry: Wrong OTP

    Retry --> Pending: Attempt < 3
    Retry --> Locked: Attempt >= 3

    Validated --> [*]: Payment Proceeds
    Locked --> [*]: Payment Failed
```

| State | Max Attempts | Timeout |
|-------|--------------|---------|
| `pending` | 3 | 5 minutes |
| `validated` | - | - |
| `locked` | - | 30 minutes |
