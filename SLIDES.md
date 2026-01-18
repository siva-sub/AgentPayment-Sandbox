---
marp: true
theme: gaia
class: lead
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
style: |
  section {
    font-family: 'Inter', sans-serif;
    font-size: 26px;
    padding: 30px;
  }
  h1 { color: #2D3E50; font-size: 1.5em; margin-bottom: 0.1em; }
  h2 { color: #E74C3C; font-size: 1.1em; margin-bottom: 0.4em; }
  strong { color: #2980B9; }
  blockquote { background: #f9f9f9; border-left: 8px solid #ccc; padding: 10px 15px; font-style: italic; font-size: 0.9em; }
  img { box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; background-color: transparent; }
  .columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; align-items: center; }
  .small-text { font-size: 0.7em; }
  .center { text-align: center; }
  .profile-box { background: #f0f4f8; padding: 15px; border-radius: 8px; font-size: 0.85em; }
---

# **APS** 🤖💳
## AgentPayment Sandbox

<div class="columns">
<div>

**Sivasubramanian Ramanathan**
*Product Owner | Fintech & Innovation*
*Ex-BIS Innovation Hub Singapore*

**🌏 Seeking Opportunities in Singapore**
I am looking for roles in **Product Management, Fintech, Payments, RegTech**, and **Digital Assets**.

</div>
<div class="profile-box">

"I am a Product person. **I build.**"

I have worked across product delivery, user research, and cross-agency collaboration. I enjoy solving complex problems and bringing structure to early ideas.

**I care deeply about building products that create real impact.**

</div>
</div>

---

# **The Vision: Agents Will Shop For You** 🌍

We are moving from a world where **humans click buttons** to a world where **agents negotiate protocols**.

![h:300](https://kroki.io/mermaid/svg/eNqFj88KgkAQxu89xeQ1TOjoQTD7JyR06AUmd9RFnbVtRXr7tg3BEGouw8z8vm_4HnTviXPaSSw1tguw1aE2MpcdsoFT3yLPtnEKcUlsZoeMdF454pK6o9P7UTQqQvC2_ROKRpaVAaPgrFgo9hw8QpafGoVw3F8hWA_UNH7NauAAN-gUU8z_euMaJKjFb-tEExp6gwZWkCELO_7xThQXUrc0s3ZpbcTDJ95NqZrE0nsBfgpuTw==)

### **The Shift**
*   **Today**: Humans navigate UI, solve CAPTCHAs, enter details.
*   **Tomorrow**: Agents use APIs JSON-RPC, and Crypto Signatures.

> **Prediction**: By 2027, a significant % of eCommerce will be Agent-to-Agent.

---

# **The Reality: A Testing Nightmare** 🧩

*The infrastructure is here, but it is fragmented.*

| Protocol | Company | Approach |
|----------|---------|----------|
| **AP2** | Google | "Agent-to-Agent" mandates |
| **x402** | Coinbase | HTTP 402 Micropayments |
| **ACP** | Shopify + OpenAI | E-commerce checkout |
| **UCP** | Stripe | Universal payment API |

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

*A Unified Sandbox for Agentic Commerce Protocols*

![h:300](https://kroki.io/mermaid/svg/eNpLy0kvT85ILCpRCHHiUgCC4tKk9KLEggwFt6L8vJLUvBSwKAgE5CRWphfll-alRCOYCqGesXAVLonFGUn5iUUp0XAWRBJmDNxwp8TkbGSzQ50DovVz85Oz9UuTCxAGOsKFE5GFI0wMjKDiFUAmkvoAmHhiAZKwZ15xQWpySX5RNFA8Uz8TxkV1HMzDCrq6djAHAgC1wlLn)

*   ⚡ **Mock Servers**: Instant endpoints for UCP, ACP, x402, AP2.
*   🔍 **Inspector**: Validates your requests against official schemas.
*   🛡️ **Security Overview**: Verifies cryptographic signatures (EIP-712).
*   🎮 **Playground**: Learn by doing in the UI.

---

# **Testing Flow 1: x402 (Coinbase)** ⚡

*The Standard for Micropayments & Metered Access.*

![h:350](https://kroki.io/mermaid/svg/eNqNjjELwkAMhXd_RUZFDmsRhA4FqUUcLMV20DG0oQa863leBf-9oaeTCGZ7L99L3p1uA5mGtoydQz0BGYvOc8MWjYfsymT8l12Re5Ab7UCoNA1eAru8hoV1pHnQCi2PVFgqwQKfwCqKYQ4lPrXIo9RgRy1cCNv34aL3BL2k4BOpuDNSY0zANN-Xar2MZ_-1kF8nVW7Oh7yofzSKo0iorDde5As4LFiw)

### **What APS Tests:**
1.  **Header Parsing**: Does the agent correctly parse `402 Payment Required` headers?
2.  **Signature Validation**: Is the `X-Payment` header signature valid?
3.  **Payload Structure**: Does the payment payload match the resource price?

---

# **Testing Flow 2: AP2 (Google)** 🤖

*High-Trust Commerce with User Mandates.*

![h:350](https://kroki.io/mermaid/svg/eNqNT70KwkAM3n2KjDp0cexQKHZVxOIDhGtoA_Yu5q6CPr1nnaIVzHLhvr98ka4TeUcNY684riCPoCZ2LOgTtEMQYd9D3ZNPX_Ce1A2vZRk-4n0kg1q_oqqsQwkNRxdupLCut_Vm1lhKkUXWpXw_sEPt_gvJzHw7-g4TzYpDSARz7Kf1OeZPFNGMRrjwyD-KmK75pCkNQflBJseQlpqcyBFLegL8d4jH)

### **What APS Tests:**
1.  **Discovery**: Can the agent find and parse the `/.well-known/a2a` card?
2.  **Mandate Limits**: Does the agent respect the spending limit in the Mandate?
3.  **OTP Challenge**: Can the agent handle user intervention flows?

---

# **Testing Flow 3: ACP (Shopify + OpenAI)** 🛍️

*Agentic Commerce Protocol: Specialized for E-commerce.*

![h:350](https://kroki.io/mermaid/svg/eNqVjcEKgzAQRO_9ir0X692DUNrSU0mo_YElLhqMSUxWxL9vrD0IBaFznHkzE2kYySq6amwC9gdI8hhYK-3RMpwbsvzrXiQ8KKgWv-EHy8pyGxRwv70gP01kTNZZN9k8ts6v_IbLlt7SL6BKOdTEqE3c2ZWiSsOqJdW5kfNIMWpnd4dXBI4gce6TBcJzMv548TjvPYhQU4AnKdKe36hvbaA=)

### **What APS Tests:**
1.  **Session Management**: Can the agent maintain session state across requests?
2.  **Product Selection**: Does the agent correctly select variants (size/color)?
3.  **Checkout Validity**: Is the shipping address and payment method valid?

---

# **Testing Flow 4: UCP (Stripe)** 💳

*Universal Commerce Protocol: The "Stripe for Agents".*

![h:350](https://kroki.io/mermaid/svg/eNqFjUEKwjAQRfeeYlbuYvddFCSIC5EWqgeIydgOTZOYpBQR726oCgWhznL---8HvA1oJCoSjRf9CtI54SNJcsJE2DZo4s_3zCs4opet-IQTxopiHuSw350g24yoNeuMHU02SDfhc4yl2lTPgQsnLqQpEgZYwwHvYcFelXXSyxZlZ4fIAoZA1oSlgfrNAPcoIqq_8q8ze5B6ZtL2TmPEpYXSK_TArbmS79PCC4-lcfM=)

### **What APS Tests:**
1.  **Capability Discovery**: Can the agent identify supported payment methods?
2.  **Idempotency**: Does the agent safely retry requests without double-charging?
3.  **Card Validation**: Are the card details (simulated) correctly formatted?

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

> **Result**: A frictionless live demo for recruiters and developers.

</div>
</div>

---

# **About Me** 👨‍💼

**Sivasubramanian Ramanathan**
*Product Owner | Fintech, Payments & Digital Innovation*

I specialize in **simplifying complexity**.

*   **Experience**: BIS Innovation Hub Singapore (CBDCs, Cross-Border Payments).
*   **Skills**: Product Management, Rapid Prototyping, Technical Strategy.
*   **Focus**: Bridging the gap between Policy/Regulation and Engineering.

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
