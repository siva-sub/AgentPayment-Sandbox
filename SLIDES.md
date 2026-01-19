---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 22px;
    padding: 35px;
  }
  h1 { color: #1a365d; font-size: 1.6em; margin-bottom: 0.2em; }
  h2 { color: #2b6cb0; font-size: 1.1em; margin-bottom: 0.3em; }
  h3 { color: #2c5282; font-size: 0.95em; }
  strong { color: #2f855a; }
  code { background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
  img { border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
  .columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; align-items: start; }
  table { font-size: 0.8em; margin: 0 auto; margin-bottom: 1em; }
  th { background: #2b6cb0; color: white; }
  blockquote { background: #ebf8ff; padding: 12px; border-left: 4px solid #2b6cb0; border-radius: 6px; font-size: 0.9em; margin-top: 1em; }
  .big-title { font-size: 2.2em !important; }
---

<!-- _class: lead -->

# <span class="big-title">🤖 AI Agents Will Transact</span>

## But Today's Payments Weren't Built for Them

![bg right:45%](https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&h=900&fit=crop)

**Sivasubramanian Ramanathan**
*Product Owner | Fintech & Innovation*

💼 Looking for roles in Product, Fintech, Payments

---

# The Problem: Checkout Was Designed for Humans 🧩

*Agents don't have fingers to click "Buy Now".*

<div class="columns">
<div>

### What Developers Face Today
- No standard way for agents to pay
- Multiple competing protocols (UCP, AP2, x402, ACP)
- No testing tools — only real implementations
- Security concerns unclear

</div>
<div>

### What I Built
**AgentPayment Sandbox (APS)**
- Mock servers for 4 protocols
- Inspector for compliance testing
- Schema validators
- Works offline, no real money

</div>
</div>

> **The problem**: Developers building AI shopping agents have no way to test payment flows without implementing real protocol servers.

---

# The Emerging Protocols 📋

*Google, Coinbase, and OpenAI are defining how agents will pay.*

| Protocol | What It Does | Key Innovation |
|----------|--------------|----------------|
| **UCP** | Universal checkout | Shopify, Walmart, Stripe unified API |
| **AP2** | Agent Payments | Verifiable Credentials (Mandates) |
| **A2A** | Agent messaging | Agents talk to agents |
| **x402** | Micropayments | HTTP 402 + crypto signatures |
| **ACP** | E-commerce | OpenAI + Shopify checkout |
| **MCP** | Tool access | Claude/ChatGPT to APIs |

> **AP2 is built ON TOP of A2A. x402 extends AP2 for crypto.**

---

# UCP Flow: Universal Checkout 🛒

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNp1jkEKgzAQRfc9RS6QunchFC1dKljXJUymNqhJOkkqvX1DcFOMsxmY__5jHL4DasBGiZHEcmJxrCCvQFmhPbuMqP3uOtQdEy6tHumDlIjE8qqK55LdrndWnFecZz5ps-oigE1UTHmEElyyRjkwUfA9MFgyMoB3mWotvJjNuC92bR-b8EKYTPDcoXPK6Jxiix5KZixDTlJs6L9nsFJ4lIevmMXO6DHTbEkiMTD6qWhB-QMsLHpR)

</div>
<div>

### Endpoints Tested
- `GET /.well-known/ucp` → Discovery
- `GET /products` → Catalog
- `POST /checkout-sessions` → Create session
- `PUT /checkout-sessions/{id}` → Update cart
- `POST /complete` → Order confirmed

### Key Features
- Idempotency via `Idempotency-Key` header
- Fulfillment options calculation
- Order history tracking

</div>
</div>

---

# AP2 Flow: Agent Payments Protocol 💳

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNptkDFvxCAMhff-Co-94ZaON5yE0oxR0aU74sAiVhOg4FzVf1-SXtQ2hc1-n58fzvg-ozf4TNolPT1AeVEnJkNRe4ZegM7QDyFG8g6EQ8__oK5doA6TGZayDjVygZqEtqikxwwyhRtZTCvai-P53LUnEE_iBCahZlTkucBq0t6WcuW69ljAvjB_RUW24nNN4SOjiinY2XDeOcjf7WoAUz6wG1pa21J4zOQ82sOPQyPvDhlHNKyi_pzWmMhD-I7YyM1rEzm8oa-kIE_lVCXHHdxFeXmVUE4-jugdVsbzfJ2IVeC4G7ygQYr8Bcr2m2g=)

</div>
<div>

### A2A Methods Tested
- `create_intent_mandate` → User authorization
- `browse_products` → Catalog access
- `create_cart` → Merchant commits price
- `select_payment_method` → Credentials Provider
- `initiate_payment` → OTP challenge
- `submit_otp` → Complete payment

### Key Features
- Signed mandates (Intent, Cart, Payment)
- Multi-agent architecture
- OTP step-up challenge

</div>
</div>

---

# x402 Flow: HTTP 402 Micropayments ⚡

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNqNj70KwkAQhHufYnsJililEAR_KjVoEC2XyxoX4kX3NqKI7-4lEYyYwmuO25n7ZtbRpSBraMKYCp464M8ZRdnwGa3COCWrP9PbsD8AdPW9IbmS_HhmaDhjRc1rrSIFo1H5J4T5NIaekMsLMdR7cPKsTKUYeFNlDqHEdyHC-8k_174qCyVftEZKCNFq46m-DB_ulauhNqhbzDgBx6lFLYT-audr7IJovF9Ml_GnaWu-I9WM2vJreCxoHRrl3MIR3bFt8fU7G0xu1U9exMWFBw==)

</div>
<div>

### Endpoints Tested
- `GET /resource/{id}` → Returns 402
- `POST /verify` → Validate signature
- `POST /settle` → Execute on-chain
- `GET /info` → Server capabilities
- `GET /supported` → Payment networks

### Key Features
- CAIP-2 network identifiers
- EIP-3009 authorization format
- Facilitator API pattern
- Base Sepolia testnet support

</div>
</div>

---

# ACP Flow: Agentic Commerce Protocol 🏪

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNqN0D0LwjAQBuDdX3G71OwOBbHiqFA7l5Bc9TBfJqlFxP9uWi0idjDLwd17D0cCXlo0AgviR8_1DNJz3EcS5LiJsDqiib_d9R54GEqJ_op-SAzZLM9TewnbzQHYokOlsrOxnWHihOJs2xeWIlmf7DeWUFAQNik3cN42pPCX2-_K5I1GHTAEsiZMYO9RTRLmYF38xL68aopjd5KPCbNykkfswaZV6UClx1_558hBZcJqpzDiBL_zEj0IaxryGuUTvdeBhA==)

</div>
<div>

### Endpoints Tested
- `GET /.well-known/checkout` → Discovery
- `POST /checkout_sessions` → Create session
- `PUT /checkout_sessions/{id}` → Update items
- `POST /complete` → Finalize order
- `DELETE /checkout_sessions/{id}` → Cancel

### Key Features
- OpenAI + Shopify integration
- Fulfillment address handling
- API versioning support
- Session state machine

</div>
</div>

---

# Why I'm Exploring This 🔍

![bg left:35%](https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=700&fit=crop)

### My Curiosity
Agentic commerce sits at the intersection of **fintech**, **AI**, and **policy** — areas I find fascinating.

### Questions That Drew Me In
1. **Infrastructure Gap**: How will payments evolve for agents?
2. **Trust**: Who's liable when an agent buys wrong?
3. **Security**: Can attackers hijack agent purchases?

### My Approach
I build things to understand them. APS is how I learn.

---

# The Trust Crisis 🔐

*Payments assume a human clicked "Buy". Agents break that.*

<div class="columns">
<div>

### Old World Problems
- CAPTCHAs block agents
- Card forms need human input
- No proof of agent authority
- Who's liable for wrong purchases?

</div>
<div>

### New World Solutions (AP2)
- **Verifiable Credentials** (VCs)
- **Intent Mandates** (what user wants)
- **Cart Mandates** (what merchant agreed)
- **Payment Mandates** (audit trail)

</div>
</div>

> **AP2's core innovation**: Cryptographic proof of who authorized what.

---

# Life of a Transaction: Human Present 👤

*User is available to approve the final purchase.*

<div class="columns">
<div>

![w:420](https://kroki.io/mermaid/svg/eNptkEFOwzAQRfecYi7QC2RRKZiIlSWLwAFG9pCMSGxju616e8ZJES2Jl_Pn__c9mb5P5C29MA4J5yeQFzEVthzRF_jIlDbDvgXM0I8hRvYDtAP5slnSXV3SlOyIO7IyVVaJnJgZpwwmhTO7G65yD8dj3zZ_nFS75jWqb0XVXQPPKVwyQUzBnWzJi6i7w81r1jFMfO-r4UvuBUIsHHzeMGkisXGhOT_ypDEWAitf-cfqefDkQImi0TvZ2iVWJ3yGBBil9BmnDVty9lOUaeCVitzxOsvVYKYyBrfoyvzWeA9f5B87G7zedV27vJEljuUH0_mc4w==)

</div>
<div>

### The Flow
1. User → Shopping Agent: "Buy shoes"
2. Agent → Merchant: Browse products
3. Merchant → Agent: Signed CartMandate
4. Agent → User: Show cart for approval
5. User signs CartMandate
6. Agent → Credentials Provider: Get token
7. Pay → Receipt

</div>
</div>

---

# Life of a Transaction: Human NOT Present 🤖

*"Buy these shoes when price drops below $100"*

<div class="columns">
<div>

![w:420](https://kroki.io/mermaid/svg/eNptj01OxDAMhfecwnOAucAsRirQBYugkSIOYKWexELjBMel4vY0oYBQyTLv8_up9DaTBHpkjIq3O1hfQTUOXFAMXirp7tMPgBV8yqWwRBgiie0gNzbIkYaEm9zMjuezH05wP3_AkkigKAeCSXOpnfHDSjTwBA9Zrqw3YDHaO3iOAk9dcigTGnXiORtBfieFBvVqsCBbhWtWMOUYt0U9yY1rTqLw-lWkC248bhmXn3KFpsPfq8vcllWChS39U-TXxc8hUN3N-zaYDp_EB3lL)

</div>
<div>

### The Flow
1. User → Agent: "Buy when price drops"
2. User signs **Intent Mandate** (budget, constraints)
3. Agent waits for trigger
4. Price drops → Agent purchases
5. Merchant may force user confirmation
6. Receipt sent to user

**Key**: Intent Mandate limits agent scope.

</div>
</div>

---

# Security: What Could Go Wrong? ⚠️

*The protocol anticipates adversarial scenarios.*

| Threat | Description | AP2 Mitigation |
|--------|-------------|----------------|
| **Prompt Injection** | Attacker tricks agent into buying | Intent Mandate limits scope |
| **Agent Hallucination** | Agent misunderstands request | Cart Mandate requires user sign-off |
| **First-Party Misuse** | User claims fraud for refund | Signed mandate is evidence |
| **Account Takeover** | Fraudster uses victim's agent | Device-backed key attestation |
| **Man-in-the-Middle** | Attacker alters transaction | Cryptographic signature verification |

> **Dispute Resolution**: Mandates provide non-repudiable audit trail.

---

# The Mandate System 📜

*Verifiable Credentials are the trust anchors.*

<div class="columns">
<div>

### 1. Intent Mandate
- User's **shopping intent** in natural language
- Budget constraints
- **Signed by user's device key**
- Has expiration time (TTL)

### 2. Cart Mandate
- Final SKUs, price, shipping
- **Signed by merchant first**
- Then **signed by user**
- Binding contract

</div>
<div>

### 3. Payment Mandate
- Shared with network/issuer
- Contains: AI agent presence signals
- Enables: Risk assessment
- Evidence for disputes

### Key Property
**Non-repudiable**: Can't deny you signed it.

</div>
</div>

---

# How AP2, A2A, MCP Relate 🔗

*Three layers of agent infrastructure.*

| Layer | Protocol | Purpose |
|-------|----------|---------|
| **Data Access** | MCP | Agent ↔ Tools/APIs |
| **Agent Comms** | A2A | Agent ↔ Agent messaging |
| **Payments** | AP2 | Agent ↔ Payments (mandates) |

> **In short**:
> - MCP: Agents talk to **data**
> - A2A: Agents talk to **agents**
> - AP2: Agents talk about **payments**

---

# How AP2 and x402 Relate ⚡

*AP2 is payment-method agnostic. x402 is crypto payments.*

<div class="columns">
<div>

### AP2 (Google)
- Supports "pull" payments (cards)
- Roadmap: "push" payments (bank, crypto)
- **Payment agnostic framework**
- Partners: Visa, Mastercard, Adyen

</div>
<div>

### x402 (Coinbase)
- **HTTP 402 "Payment Required"**
- EIP-712 signatures
- Stablecoins (USDC on Base)
- Metered API access

</div>
</div>

> **Together**: AP2 provides the trust framework, x402 provides the crypto rails.

---

# What APS Tests 🧪

*I built a sandbox to learn by doing.*

<div class="columns">
<div>

### Mock Servers
| Protocol | What It Tests |
|----------|---------------|
| `ucp.py` | Discovery, checkout sessions, idempotency |
| `ap2.py` | Intent/Cart Mandates, OTP flow, A2A messages |
| `x402.py` | 402 response, CAIP-2 networks, EIP-3009 auth |
| `acp.py` | Sessions, fulfillment addresses, completion |

</div>
<div>

### Inspector Flow

![w:380](https://kroki.io/mermaid/svg/eNptj00KwjAQhfeeYi7gFYQ2_UEQlMaNFBc1HW2xTUoyUUS8u3XQGsG3-vjgDW-OnbmqprIEq2IGY5w_nGw1NLAz3oIwNbJ-JSrZSbQXtHvWqOvfVrSRsNRuQEXGTs243KIjKLzWn-Yr4i4aVGeQVJF3j8knb5-12NWBT99-WWM_GEKtbo__M9aeBk9TMSslKm9buoFUxuJ3Ql4WqEzfjxcqao12v39FMJ8vIGaOmUXAScAps2DOmJOA04Az5vwJoU1iIA==)

</div>
</div>

---

# Why a Product Owner Built This 👨‍💼

![bg right:40%](https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=700&fit=crop)

*"You built a testing sandbox. Aren't you a PM?"*

### My Philosophy
1. **Build to Understand**
2. Infrastructure needs PMs who get tech
3. De-risk by prototyping

### What This Shows
- I can read protocol specs
- I can implement working software
- I can document thoroughly (8 docs, 3 ADRs)

---

# Live Demo 🌐

![bg left:35%](https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=500&h=700&fit=crop)

### GitHub Pages Challenge
No server = No mock endpoints

### Solution
```typescript
const IS_DEMO = hostname
  .includes('github.io');

if (IS_DEMO) {
  return DEMO_DATA[endpoint];
}
```

**Live**: [siva-sub.github.io/AgentPayment-Sandbox](https://siva-sub.github.io/AgentPayment-Sandbox/)

---

# Let's Connect 🤝

![bg right:40%](https://images.unsplash.com/photo-1573164713988-8665fc963095?w=600&h=800&fit=crop)

**Sivasubramanian Ramanathan**
*Product Owner | Fintech & Innovation*

### 💼 Open for Roles In
Product Management • Fintech • Payments
RegTech • Digital Assets

*Also open to roles that sit between policy, technology, and stakeholder engagement.*

🌐 [sivasub.com](https://sivasub.com)
💼 [LinkedIn](https://www.linkedin.com/in/sivasub987/)
💻 [GitHub](https://github.com/siva-sub)

---

<!-- _class: lead -->

# Thank You 🙏

## AgentPayment Sandbox
*Testing the future of AI agent payments*

![bg right:40%](https://images.unsplash.com/photo-1673187636492-fec1c2e6e25c?w=600&h=900&fit=crop)

📄 **[Slides PDF](https://github.com/siva-sub/AgentPayment-Sandbox/raw/main/SLIDES.pdf)**
🔗 **[Live Demo](https://siva-sub.github.io/AgentPayment-Sandbox/)**
📚 **[Documentation](https://github.com/siva-sub/AgentPayment-Sandbox/tree/main/docs)**
