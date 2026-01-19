---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 24px;
    padding: 40px;
  }
  h1 { color: #1a365d; font-size: 1.6em; margin-bottom: 0.3em; }
  h2 { color: #2b6cb0; font-size: 1.1em; margin-bottom: 0.4em; }
  h3 { color: #2c5282; font-size: 0.95em; }
  strong { color: #2f855a; }
  code { background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }
  img { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
  .columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2rem; align-items: center; }
  table { font-size: 0.85em; margin: 0 auto; }
  th { background: #2b6cb0; color: white; }
  blockquote { background: #ebf8ff; padding: 15px; border-left: 4px solid #2b6cb0; border-radius: 8px; }
---

<!-- _class: lead -->

# 🤖 AgentPayment Sandbox

## Test AI Agent Payments Without Real Money

![bg right:40%](https://images.unsplash.com/photo-1676911809746-85b85f3d61fe?w=600&h=900&fit=crop)

**Sivasubramanian Ramanathan**
*Product Owner | Fintech & Innovation*

🌏 Open for roles in Singapore

---

# The Problem I Solved 🧩

![bg left:35%](https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=500&h=700&fit=crop)

*"I'm building an AI shopping agent. How do I test it?"*

| Without Sandbox | With APS |
|-----------------|----------|
| Real money | **Free, instant, local** |
| Hope you got it right | **Automated Inspector** |
| Build 4 mock servers | **Unified platform** |

> **There was no "Postman for Agent Payments". So I built one.**

---

# The Protocol Landscape 📋

![bg right:30%](https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=600&fit=crop)

*Google announced UCP with 20+ partners*

| Protocol | Owner | Purpose |
|----------|-------|---------|
| **UCP** | Google + Partners | Universal checkout |
| **AP2** | Google | Agent mandates (A2A) |
| **ACP** | OpenAI + Shopify | E-commerce checkout |
| **x402** | Coinbase | Micropayments |

**A2A** = Messaging protocol
**AP2** = Payment extension on A2A

---

# What APS Tests ✅

![bg left:40%](https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=500&h=700&fit=crop)

### Backend (2,700+ lines Python)
- `ucp.py` — 475 lines
- `ap2.py` — 727 lines  
- `x402.py` — 524 lines
- `acp.py` — 340 lines
- `inspector.py` — 491 lines

### Frontend (React + TypeScript)
- Interactive Playground UI
- Flow Runner (step-by-step)
- Security Analyzer

---

# The Inspector 🔍

<div class="columns">
<div>

![w:400](https://kroki.io/mermaid/svg/eNpLy8kvT85ILCpR8AniUgACx-jI_NIiheDUorLUolgFXV07Badoz7zigtTkkvyiWLAaJ7Cwc3VIanFJcS1YyBks5BL9aE6rQkBicXEskqhr9KO5PQpuiZk5EFEXsKhbdHByflGqlYKhgQFE3BUs7h4dlJqcn5ubmpeSWJKZn1ccCwCPty_K)

</div>
<div>

### Test Suites Per Protocol
- **UCP**: 5 tests
- **ACP**: 5 tests
- **x402**: 5 tests
- **AP2**: 2 tests

### Output
✅ Pass/Fail status
📊 Security Score (0-100)
💡 Recommendations

</div>
</div>

---

# UCP Flow 💳

*Discovery → Session → Complete*

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNp1jEEKgzAQRfc9xVzAC7gQpNl0URR6giH9tQOapJNR6O0rQVcls_zvzcv4rAgeTnhSXi60X2I18ZI4GPUTgv2td6h_8wGK0nTdObbkJPu4Qb-Fn3uzO8VtadT4khmV96uCDfRAzhJDrXFgurlaJi5phqEWGPQJ_QE801ME)

</div>
<div>

### Endpoints
1. `GET /.well-known/ucp`
2. `POST /checkout-sessions`
3. `PUT /checkout-sessions/{id}`
4. `POST /.../complete`

**Partners**: Shopify, Walmart, Target, Etsy

</div>
</div>

---

# AP2 Flow 🤖

*A2A Messaging + Mandates + OTP*

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNp1jUEKwzAMBO99hT6QD-QQSNNjAqU_EM6S6FDbkWUKfX1d05yKddydHSUcGd7hJrwpPy9ULrKaOInsjcYN3v7SBep2_hUV6YbhDHu6angl0F3Dmp2lSp1tV8i66GmW1DJMCjbQVH621t-OFvZrARuWMdseVN5oOR5wkGgf1LBUyA==)

</div>
<div>

### A2A Methods
- `ap2/createIntentMandate`
- `ap2/browseProducts`
- `ap2/createCart`
- `ap2/initiatePayment`
- `ap2/submitOtp`

**Result**: CartMandate → OTP → Receipt

</div>
</div>

---

# x402 Flow ⚡

*HTTP 402 + EIP-712 Signatures*

<div class="columns">
<div>

![w:380](https://kroki.io/mermaid/svg/eNorTi0sTc1LTnXJTEwvSszlUgCCgsSikszkzILEvBIF55zM1LwSDOHg1KKy1CKwMESFrp0dRMxKwd01REG_KLU4v7QoORWsBCKjC1QDUWylYGJgpBAEtDqzKDUFtynaChG6AY6Rvq5-ITjMMTIwUHDOzysBcgD9NT9m)

</div>
<div>

### x402 v2 Features
- CAIP-2 network IDs
- `PaymentRequired` response
- EIP-3009 authorization
- Facilitator: `/verify`, `/settle`

**Owner**: Coinbase

</div>
</div>

---

# Why a Product Owner Built This 👨‍💼

![bg right:40%](https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=700&fit=crop)

*"You wrote 2,700+ lines of code. Aren't you a PM?"*

### My Philosophy
1. **Build to Understand**
2. **Bridge Technical Gaps**
3. **De-risk Decisions**

> **The best PMs accept complexity. They don't outsource understanding.**

---

# GitHub Pages Demo 🌐

![bg left:35%](https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=500&h=700&fit=crop)

### The Challenge
GitHub Pages = No server.

### The Solution
```typescript
const IS_DEMO = hostname
  .includes('github.io');

if (IS_DEMO) {
  return DEMO_DATA[endpoint];
}
```

**Result**: Frictionless live demo!

---

# Let's Connect 🤝

![bg right:45%](https://images.unsplash.com/photo-1573164713988-8665fc963095?w=600&h=800&fit=crop)

**Sivasubramanian Ramanathan**
*Product Owner | Fintech & Innovation*

### Open for Roles
Product Management • Fintech
Payments • RegTech • Digital Assets

🌐 [sivasub.com](https://sivasub.com)
💼 [LinkedIn](https://www.linkedin.com/in/sivasub987/)
💻 [GitHub](https://github.com/siva-sub)

---

<!-- _class: lead -->

# Thank You! 🙏

## AgentPayment Sandbox
*The Postman for Agent Payments*

![bg right:40%](https://images.unsplash.com/photo-1673187636492-fec1c2e6e25c?w=600&h=900&fit=crop)

🔗 **[Live Demo](https://siva-sub.github.io/AgentPayment-Sandbox/)**
📚 **[Documentation](https://github.com/siva-sub/AgentPayment-Sandbox/tree/main/docs)**
