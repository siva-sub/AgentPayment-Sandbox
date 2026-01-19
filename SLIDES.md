---
marp: true
theme: gaia
class: lead
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
style: |
  section {
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    padding: 30px;
  }
  h1 { color: #2D3E50; font-size: 1.4em; margin-bottom: 0.1em; }
  h2 { color: #E74C3C; font-size: 1.0em; margin-bottom: 0.3em; }
  strong { color: #2980B9; }
  img { box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; background-color: transparent; }
  .columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; align-items: start; }
  .profile-box { background: #f0f4f8; padding: 15px; border-radius: 8px; font-size: 0.8em; }
---

# **APS** 🤖💳
## AgentPayment Sandbox

<div class="columns">
<div>

**Sivasubramanian Ramanathan**
*Product Owner | Fintech & Innovation*
*Ex-BIS Innovation Hub Singapore*

**🌏 Seeking Opportunities in Singapore**
Product Management • Fintech • Payments • RegTech

</div>
<div class="profile-box">

"I am a Product person. **I build to understand.**"

The best Product Owners don't just write specs—they prototype. I built APS to deeply understand the protocols I might one day govern.

This is how I learn: by building.

</div>
</div>

---

# **The Paradigm Shift** 🌍

*Checkout forms were designed for humans. Agents don't have fingers.*

### 1. The Old World (Human Commerce) 👤
*   Human → Browser → Click "Buy" → CAPTCHA → Enter Card → Done
*   **Designed for**: Eyeballs and fingers
*   **Result**: CAPTCHAs actively block automation

### 2. The New World (Agentic Commerce) 🚀
*   Agent → API Discovery → Structured Checkout → Crypto Auth → Done
*   **Designed for**: Autonomous software agents
*   **Result**: Mandates and signatures replace passwords

> **The question is no longer IF agents will transact, but HOW.**

---

# **The Problem I Actually Solved** 🧩

*"I'm building an AI shopping agent. How do I test it?"*

| Challenge | Without Sandbox | With APS |
|-----------|-----------------|----------|
| Testing payments | Real money or test accounts | Free, instant, local |
| Protocol compliance | Read specs, hope you got it right | Automated Inspector |
| Multiple protocols | Implement each one separately | Unified testing for all 4 |
| Edge cases | Hard to reproduce | Controllable mock responses |

> **There was no "Postman for Agent Payments". So I built one.**

---

# **The Protocol Landscape** 📋

*Four major protocols have emerged. APS tests all of them.*

| Protocol | Maintainer | What It Does |
|----------|------------|--------------|
| **UCP** | **Google + Partners** | Universal checkout (Shopify, Walmart, Target) |
| **AP2** | **Google** | Agent-to-Agent mandates with A2A messaging |
| **ACP** | **OpenAI/Shopify** | OpenAPI-based e-commerce checkout |
| **x402** | **Coinbase** | HTTP 402 "Payment Required" for micropayments |

**How they relate:**
- **UCP** = The universal standard (broadest adoption)
- **AP2** = High-trust purchases (mandates, OTP challenges)
- **ACP** = E-commerce focus (fulfillment, variants)
- **x402** = Metered access (pay-per-request APIs)

---

# **Introducing APS** 🚀

*Unified Sandbox for Agentic Commerce*

<div class="columns">
<div>

![w:400](https://kroki.io/mermaid/svg/eNpLL0osyFDwCeJSAILi0qR0MN-tKD-vJDUvBSwKAqGe0QE5iZXpRfmleSmxcGGXxOKMaBCRlJ9YBBWHaYMb5pSYnI1ilnNANBAr-OYnZyOMcgSKOmKKBhhFAzGaaIWJgVE0iEASh9kAc7qCrq4dzGoAmGQ9qg==)

</div>
<div>

### What I Built
*   ⚡ **4 Mock Servers**: UCP, AP2, ACP, x402
*   🔍 **Inspector**: Validates requests against specs
*   🛡️ **Security Analyzer**: Signature verification
*   🎮 **Playground UI**: Interactive protocol explorer

### Tech Stack
*   Frontend: React + TypeScript + Vite
*   Backend: FastAPI + Pydantic (2,000+ lines)

</div>
</div>

---

# **UCP Flow: Universal Commerce** 💳

*Discovery → Session → Complete (Google + Shopify + Walmart)*

<div class="columns">
<div>

![w:400](https://kroki.io/mermaid/svg/eNp1jEEKgzAQRfc9xVzAC7gQpNl0URR6giH9tQOapJNR6O0rQVcls_zvzcv4rAgeTnhSXi60X2I18ZI4GPUTgv2td6h_8wGK0nTdObbkJPu4Qb-Fn3uzO8VtadT4khmV96uCDfRAzhJDrXFgurlaJi5phqEWGPQJ_QE801ME)

</div>
<div>

### APS Tests
1. **Discovery**: `/.well-known/ucp`
2. **Create Session**: POST `/checkout-sessions`
3. **Update Session**: PUT `/checkout-sessions/{id}`
4. **Complete**: POST `/complete`
5. **Idempotency**: `Idempotency-Key` header

**Code**: `ucp.py` (475 lines)

</div>
</div>

---

# **AP2 Flow: Agent Mandates** 🤖

*A2A Messaging + Intent/Cart Mandates + OTP (Google)*

<div class="columns">
<div>

![w:400](https://kroki.io/mermaid/svg/eNp1jUEKwzAMBO99hT6QD-QQSNNjAqU_EM6S6FDbkWUKfX1d05yKddydHSUcGd7hJrwpPy9ULrKaOInsjcYN3v7SBep2_hUV6YbhDHu6angl0F3Dmp2lSp1tV8i66GmW1DJMCjbQVH621t-OFvZrARuWMdseVN5oOR5wkGgf1LBUyA==)

</div>
<div>

### APS Tests
1. **Agent Card**: `/.well-known/a2a`
2. **Message Handler**: POST `/message` (JSON-RPC)
3. **Intent Mandate**: `ap2/createIntentMandate`
4. **Cart Mandate**: `ap2/createCart`
5. **OTP Flow**: `ap2/initiatePayment` → `submitOtp`

**Code**: `ap2.py` (727 lines)

</div>
</div>

---

# **x402 Flow: Micropayments** ⚡

*HTTP 402 + EIP-712 Signatures (Coinbase)*

<div class="columns">
<div>

![w:400](https://kroki.io/mermaid/svg/eNorTi0sTc1LTnXJTEwvSszlUgCCgsSikszkzILEvBIF55zM1LwSDOHg1KKy1CKwMESFrp0dRMxKwd01REG_KLU4v7QoORWsBCKjC1QDUWylYGJgpBAEtDqzKDUFtynaChG6AY6Rvq5-ITjMMTIwUHDOzysBcgD9NT9m)

</div>
<div>

### APS Tests
1. **Request Resource**: GET `/resource/{id}`
2. **402 Response**: PaymentRequired header
3. **Sign Payment**: EIP-712 + EIP-3009
4. **Retry**: GET + `X-PAYMENT` header
5. **Facilitator**: `/verify`, `/settle`

**Code**: `x402.py` (524 lines)

</div>
</div>

---

# **ACP Flow: E-commerce** 🛍️

*OpenAPI Checkout + Fulfillment (Shopify/OpenAI)*

<div class="columns">
<div>

![w:400](https://kroki.io/mermaid/svg/eNptjTEOwjAMRXdO4Qv0Ah0qIboz9ARW-Got0cTYBonbk2ZCEI_v_Sc7Hk_khFl4Nd5PVE_ZQpIo56Dzihx_dNmKNtj0ME0HGGkWT-UFezd3sKG6thnpqiEleye7GDhAC9zrotd-q5-27HpHoPvRbrAPB8lHSg==)

</div>
<div>

### APS Tests
1. **Discovery**: `/.well-known/checkout`
2. **Create Session**: POST `/checkout_sessions`
3. **Add Fulfillment**: Address + options
4. **Complete**: POST `/complete`
5. **API Version**: `API-Version: 2026-01-16`

**Code**: `acp.py` (340 lines)

</div>
</div>

---

# **Demo Mode: GitHub Pages** 🌐

*How I deployed a backend-heavy app to static hosting.*

<div class="columns">
<div>

### The Challenge
GitHub Pages = No Server.
API calls usually fail.

### The Solution
*   Detect `github.io` hostname
*   Return realistic mock data
*   Show clear Demo Mode banner

### Result
A frictionless live demo for recruiters.

</div>
<div>

```typescript
// frontend/src/services/api.ts
const IS_DEMO = window.location.hostname
  .includes('github.io');

if (IS_DEMO) {
  return DEMO_DATA[endpoint];
}
```

**Live Demo**:
[siva-sub.github.io/AgentPayment-Sandbox](https://siva-sub.github.io/AgentPayment-Sandbox/)

</div>
</div>

---

# **Why a Product Owner Built This** 👨‍💼

*"You wrote 2,000+ lines of code. Aren't you a PM?"*

### My Philosophy
1. **Build to Understand**: I prototype to deeply learn the problem space
2. **Bridge Gaps**: Translate complex specs into testable artifacts
3. **De-risk Decisions**: Validate ideas before committing teams

### What This Demonstrates
*   I can read protocol specs (AP2, x402, ACP, UCP)
*   I can implement working software (FastAPI, React)
*   I can document thoroughly (8 docs, 3 ADRs)

> **The best PMs accept complexity. They don't outsource understanding.**

---

# **Let's Connect** 🤝

I am ready to bring this level of product thinking and execution to your team.

*   🌐 **Portfolio**: [sivasub.com](https://sivasub.com)
*   💼 **LinkedIn**: [linkedin.com/in/sivasub987](https://www.linkedin.com/in/sivasub987/)
*   💻 **Code**: [GitHub/APS](https://github.com/siva-sub/AgentPayment-Sandbox)
*   📚 **Docs**: [Documentation](https://github.com/siva-sub/AgentPayment-Sandbox/tree/main/docs)

<br>

**Live Demo**:
[siva-sub.github.io/AgentPayment-Sandbox](https://siva-sub.github.io/AgentPayment-Sandbox/)
