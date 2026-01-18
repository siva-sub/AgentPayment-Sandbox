# APS Architecture

Deep dive into the AgentPayment Sandbox architecture.

---

## System Overview

```mermaid
flowchart TB
    subgraph Frontend["Frontend (React + TypeScript)"]
        Playground["Playground UI"]
        Dashboard["Dashboard"]
        FlowRunner["Flow Runner"]
    end

    subgraph Backend["Backend (FastAPI + Python)"]
        subgraph Mocks["Mock Servers"]
            UCP["/mock/ucp"]
            ACP["/mock/acp"]
            X402["/mock/x402"]
            AP2["/mock/ap2"]
        end

        subgraph Validators["Schema Validators"]
            V1["x402_schema.py"]
            V2["acp_schema.py"]
        end

        subgraph API["API Layer"]
            Inspector["/api/inspector"]
            Security["/api/security"]
        end
    end

    subgraph External["External Servers"]
        RealMerchant["Your Merchant API"]
    end

    Playground --> Mocks
    FlowRunner --> Mocks
    Inspector --> RealMerchant
    Mocks --> Validators
```

---

## Component Details

### Mock Server Architecture

Each mock server follows a consistent pattern:

```
/mock/{protocol}/
├── .well-known/{discovery}  # Discovery endpoint
├── {resource}               # CRUD operations
├── test/reset               # Reset state
└── test/generate-*          # Test helpers
```

```mermaid
classDiagram
    class MockServer {
        +router: APIRouter
        +_sessions: dict
        +_receipts: dict
        +discovery() dict
        +create() Session
        +get() Session
        +update() Session
        +complete() Receipt
        +reset() void
    }

    class UCPMock {
        +PRODUCTS: dict
        +checkout_sessions()
    }

    class ACPMock {
        +ITEMS: dict
        +API_VERSION: str
        +checkout_sessions()
    }

    class X402Mock {
        +RESOURCES: dict
        +verify() VerifyResponse
        +settle() SettleResponse
    }

    class AP2Mock {
        +PRODUCTS: dict
        +WALLET_METHODS: list
        +handle_message() A2AResponse
    }

    MockServer <|-- UCPMock
    MockServer <|-- ACPMock
    MockServer <|-- X402Mock
    MockServer <|-- AP2Mock
```

---

### Inspector Architecture

```mermaid
flowchart LR
    subgraph Input
        URL["Target URL"]
        Protocol["Protocol"]
    end

    subgraph TestRunner
        Tests["Test Definitions"]
        Client["httpx Client"]
        Context["Shared Context"]
    end

    subgraph Output
        Results["Test Results"]
        Score["Security Score"]
        Report["Test Report"]
    end

    Input --> TestRunner
    TestRunner --> Output
```

### Test Execution Flow

1. Load test definitions for protocol
2. Execute tests in order (respecting dependencies)
3. Accumulate context (session IDs, etc.)
4. Calculate security score based on weights
5. Generate comprehensive report

---

### Validator Architecture

```mermaid
flowchart TD
    subgraph Input
        Data["JSON Data"]
    end

    subgraph Validators
        Schema["Pydantic Schema"]
        Rules["Custom Validators"]
    end

    subgraph Output
        Valid["✅ Valid"]
        Errors["❌ Errors[]"]
    end

    Data --> Schema
    Schema --> Rules
    Rules -->|Pass| Valid
    Rules -->|Fail| Errors
```

---

## Data Flow

### Request Processing

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Router
    participant Mock
    participant Validator

    Client->>FastAPI: HTTP Request
    FastAPI->>Router: Route Match
    Router->>Mock: Handler

    alt Validation Required
        Mock->>Validator: Validate Input
        Validator-->>Mock: Valid/Errors
    end

    Mock->>Mock: Process Logic
    Mock-->>Router: Response
    Router-->>FastAPI: Response
    FastAPI-->>Client: HTTP Response
```

---

## Security Layer

### Signature Verification (Phase 6)

```mermaid
flowchart TD
    A["Payment Payload"] --> B["Parse Signature"]
    B --> C{"EIP-712 Valid?"}
    C -->|Yes| D["Recover Address"]
    C -->|No| E["❌ Invalid Signature"]
    D --> F{"Matches payTo?"}
    F -->|Yes| G["✅ Verified"]
    F -->|No| H["❌ Wrong Signer"]
```

### Security Scoring Algorithm

```python
score = 0
for test in tests:
    if test.passed:
        score += test.weight
    else:
        score -= test.weight * 0.5  # Penalty

security_score = normalize(score, 0, 100)
```

---

## Deployment Architecture

### Local Development

```
┌─────────────────────────────────────┐
│            Developer Machine         │
├─────────────────────────────────────┤
│  Frontend: http://localhost:5173    │
│  Backend:  http://localhost:8080    │
└─────────────────────────────────────┘
```

### GitHub Pages (Demo)

```
┌─────────────────────────────────────┐
│          GitHub Pages               │
│  siva-sub.github.io/APS             │
├─────────────────────────────────────┤
│  Static React Build                 │
│  Mock Data (localStorage)           │
└─────────────────────────────────────┘
```
