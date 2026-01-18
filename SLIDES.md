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
  .small-text { font-size: 0.7em; }
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

"I am a Product person. **I build.**"

I have worked across product delivery, user research, and cross-agency collaboration. I enjoy solving complex problems.

**I care deeply about building products that create real impact.**

</div>
</div>

---

# **The Vision: Agents Will Shop For You** 🌍

We are moving from a world where **humans click buttons** to a world where **agents negotiate protocols**.

![h:250](https://kroki.io/mermaid/svg/eNorTi0sTc1LTnXJTEwvSszlUgCCgsSikszkzILEvBIFj9LcxDwMUUdPTKEAiBhYg66dnaOnlYKSU2mlQlpOZnpGiRJY0tETJBMAlPJLTc8vyUwsSYWIB3jqQvX4JualwIXhyoMz0_MU1BQCEivR1Tvn56VlFuWmpiB0gJ0AtN0lPy9VUQkAOQtAlA==)

### **The Paradigm Shift**
*   **Today**: Humans navigate UI, solve CAPTCHAs, enter details.
*   **Tomorrow**: Agents use UCP to discover products and fill carts.

> **Prediction**: By 2027, a significant % of eCommerce will be Agent-to-Agent.

---

# **The Reality: A Testing Nightmare** 🧩

*The infrastructure is here, but it is fragmented.*

| Protocol | Company | Approach |
|----------|---------|----------|
| **UCP** | **Google + Partners** | Universal Commerce |
| **ACP** | **Shopify + OpenAI** | E-commerce checkout |
| **x402** | **Coinbase** | Micropayments |
| **AP2** | **Agent Standard** | Mandate-based A2A |

> **The Problem**: Developers need to validate signatures, parse headers, and handle mandates across 4 disparate specs.

---

# **The Developer Pain Point** 😤

*"I am building an AI shopping agent. How do I test it?"*

<div class="columns">
<div>

### **Option A: Real Test Accounts** 💸
*   Sign up for Stripe/Shopify.
*   Get API keys.
*   Configure webhooks.
*   **Days of setup.**

</div>
<div>

### **Option B: Build Mock Servers** 🔧
*   Read 4 different PDF specs.
*   Code endpoints from scratch.
*   Handle encryption manually.
*   **Weeks of work.**

</div>
</div>

> **There was no "Postman for Agent Payments". So I built one.**

---

# **Introducing APS** 🚀

*Unified Sandbox for Agentic Commerce*

![h:220](https://kroki.io/flowchart/svg/eNpLy8kvT85ILCpRCHHiUgCC4tKk9KLEggwFt6L8vJLUvBSwKAiEekYH5CRWphfll-alxMKFXRKLM6JBRFJ-YhFUHKYNbphTYnI2ilnOAdH6ufnJ2fqlyQX6CMMc4eKJKOIVJgZGUAkQE1lHAEwisQAmDrMJ5gUFXV07mBMAj_NCjg==)

*   ⚡ **Mock Servers**: Instant endpoints for UCP, ACP, x402, AP2.
*   🔍 **Inspector**: Validates requests against schemas.
*   🛡️ **Security**: Verifies EIP-712 signatures.
*   🎮 **Playground**: Learn by doing in the UI.

---

# **Flow 1: x402 (Coinbase)** ⚡

*For Micropayments & Metered Access.*

<div class="columns">
<div>

![w:450](https://kroki.io/mermaid/svg/eNp9zrEKwkAMBuDdp8guxaM4deiioiCoWAfXcP0pAXtX06vg23vc6SSaLX8-koy4T3AWa-FOuZ9RrIE1iJWBXaDVTeDCV9xAH9AUZ1HUdc4q2m4utFCMflKLRPKkiCbjipampBM_-9ic4weiaJM8-ADyEdNHNtI52oHbf-fmdC3e634cLI2h4_4FXgBLkg==)

</div>
<div>

### **What APS Tests**
1.  **Header Parsing**: Can agent handle `402 Payment Required`?
2.  **Signatures**: Is `X-Payment` header valid?
3.  **Payload**: Does payment match price?

</div>
</div>

---

# **Flow 2: AP2 (Agent Standard)** 🤖

*High-Trust Mandates for Agent-to-Agent.*

<div class="columns">
<div>

![w:450](https://kroki.io/mermaid/svg/eNorTi0sTc1LTnXJTEwvSszlUgCCgsSikszkzILEvBIFj9LcxDwMUUdPTKEAiBhYg66dnaOnlYKSU2mlQlpOZnpGiRJY0tETJBMAlPJLTc8vyUwsSYWIB3jqQvX4JualwIXhyoMz0_MU1BQCEivR1Tvn56VlFuWmpiB0gJ0AtN0lPy9VUQkAOQtAlA==)

</div>
<div>

### **What APS Tests**
1.  **Discovery**: Finding `/.well-known/a2a`.
2.  **Mandates**: Respecting spending limits.
3.  **OTP**: Handling user approval.

</div>
</div>

---

# **Flow 3: ACP (Shopify + OpenAI)** 🛍️

*Specialized for E-commerce Checkout.*

<div class="columns">
<div>

![w:450](https://kroki.io/mermaid/svg/eNorTi0sTc1LTnXJTEwvSszlUgCCgsSikszkzILEvBIFx_TUvBIM0eCM_AKwIFha184OJGCl4O4aoqBfDJMDiekC5cBqrBScE0sSc_LTsWgL8A8G6kvOSE3Ozi8twaY3OLW4ODM_D6fegsRKbNqCUpNTMwtKABNkRlM=)

</div>
<div>

### **What APS Tests**
1.  **Sessions**: Maintaining state.
2.  **Variants**: Selecting size/color.
3.  **Checkout**: Validating payments.

</div>
</div>

---

# **Flow 4: UCP (Google + Partners)** 💳

*Universal Commerce Protocol (Shopify, Stripe, Visa, etc)*

<div class="columns">
<div>

![w:450](https://kroki.io/mermaid/svg/eNp9jjEKwzAQBPu84j7gD7gwGKtxFwh5wEVemwPrpEiXvD9GBFwEZcvdYdiC5wvq4YS3zOFCRxJnEy-J1WjcoPbT3lVWwTJe5zpVqBuGs-7JSfHxjVyBc-gOrOI9TZz4IbuYoDQ1UwYb6IZSJGpb9gVodm1VDGmH4c-jqKvkgOUDGKhZEw==)

</div>
<div>

### **What APS Tests**
1.  **Discovery**: Unified product search.
2.  **Carts**: Filling carts autonomously.
3.  **Purchase**: Completing orders.

</div>
</div>

---

# **Demo Mode: GitHub Pages** 🌐

*How I deployed a backend-heavy app to static hosting.*

<div class="columns">
<div>

### **The Challenge**
GitHub Pages = No Server.
API calls usually fail.

### **The Solution**
*   **Context-Aware API**: Detects `github.io`.
*   **Service Worker Logic**: Intercepts requests.
*   **Mock Data Layer**: Returns valid JSON responses.

</div>
<div>

```typescript
// frontend/src/services/api.ts
const IS_DEMO = window.location.hostname
  .includes('github.io');

if (IS_DEMO) {
  return MOCK_DATA.ap2_response;
}
```

> **Result**: A frictionless live demo.

</div>
</div>

---

# **About Me** 👨‍💼

**Sivasubramanian Ramanathan**
*Product Owner | Fintech, Payments & Innovation*

I specialize in **simplifying complexity**.

*   **Experience**: BIS Innovation Hub Singapore (CBDCs, Cross-Border Payments).
*   **Skills**: Product Management, Rapid Prototyping, Technical Strategy.
*   **Focus**: Bridging Policy/Regulation and Engineering.

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
