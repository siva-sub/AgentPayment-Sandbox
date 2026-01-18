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

# **The Agentic Commerce Vision** 🌍

*Your AI assistant wants to book you a flight. What happens next?*

**Today, the agent hits a wall.**

### The Current Reality 🚫
*   Agent navigates to airline website.
*   Encounters **CAPTCHA**: "Select all traffic lights."
*   **Game Over**. Agent cannot proceed.

### The Emerging Future 🚀
*   Agent discovers airline's **Agent API** (like `/.well-known/a2a`).
*   Sends structured **payment mandate** with your pre-approved limits.
*   Receives confirmation. **You just flew.**

> **This is not science fiction. Four protocols are making this real today.**

---

# **The Paradigm Shift** 💡

Just like SWIFT transformed paper-based banking, **agentic protocols** are transforming online commerce.

### **It is not about the AI itself. It is about designing infrastructure FOR agents.**

![h:280](https://kroki.io/mermaid/svg/eNpVjzFuwzAMRfc9BWcHcIqsXeq5mzxkUGRRNhFJFCRKTXL4ymoRoCAg_v_-hy_zPTdLlvFXM0X8WvMV_WjZ-pVxpZMBTX3b-S8LILOlp3XxQs03pBzrQ0L_ChFIbJHZujHjd8YBSF3TQeJKO3e8gJ0v2knbDr4cWXx2N7eLt8p3P0xf2q8u9B9nN8Zj)

*   **From**: "Prove you're human" (CAPTCHAs, forms, clicks).
*   **To**: "Prove you're authorized" (Cryptographic signatures, mandates).

> This treats the **Agent** as a first-class participant in commerce.

---

# **The Problem: No Testing Infrastructure** 🧪❌

*I am building an AI shopping agent. How do I test it?*

<div class="columns">
<div>

### **Option 1: Real Services** 💸
*   Sign up for Stripe Test Mode.
*   Configure Shopify sandbox.
*   Apply for API keys from each provider.
*   **Spend days** on setup.

### **Option 2: Build Mock Servers** 🔧
*   Read 4 different protocol specs.
*   Implement each from scratch.
*   Maintain parity with spec changes.
*   **Spend weeks** on infrastructure.

</div>
<div>

### **The Gap**
There is no **"Postman for agentic commerce"**.

Developers cannot:
*   ✗ Test flows without real money
*   ✗ Validate compliance easily
*   ✗ Reproduce edge cases
*   ✗ Learn protocols interactively

> **APS fills this gap.**

</div>
</div>

---

# **Four Protocols, One Problem** 📋

*The agentic commerce landscape is fragmenting. Each solves part of the puzzle.*

![h:350](https://kroki.io/mermaid/svg/eNp1kMFqwzAMhu99Cl0CGWTkuntPPewy6HEPoBhJoqzGVrCVlb79nKRkpDA4CPH9n_QJz-4YRxz8o5kDfM_5iGG0Yt3EtNLVgqG-nfwTAxjmFHc-xN2WemL7sUXmKRJLnfORgAc5nM3qnL8L9kBmj82EU_ShThvE4V8rr_pPJYQmMM3S3sP7lMJf9V6f-dkqxXQY79IFl-iKVd9upzaGCMXuZi6R1DvhCNm-Yap_ckO2gE7epzR2J4rP4aOWy4BDz3Ufj3GNNxU7cOLjKfEn_n25kA==)

> **Question**: How do developers test against all 4 without building 4 mock servers?

---

# **Introducing APS** 🚀

*Postman + Chaos Monkey + Case Manager for Agent Payments*

![h:300](https://kroki.io/mermaid/svg/eNplkM1qwzAQhO9-iqWnBALJvRfTntokpIQQJzlVPcjWxhGVJKNdjPP2lWP3p_Qlszt8Mwie7DGN2OpHM0X4mvMJw2A5hIlppbMFQ30L4RMDOGaKOx8ct0SN7b9WyDTGwqXJWRB4ksNZr8754-AEZPbYFjhNPuq6gu__tfKqflVC0wnT5HVAb1MKf9R7e-YnqxjT4dWyC85Bixlfd0cIVspYmQWGGUmlU44QHGum5ievyJaAd-lmHLquVCv34q2W04BDz3Wf3uM13uRsgAsfj4k_8e_LBekPz76Lcw==)

APS provides **mock servers** for all 4 protocols, plus:
*   🔍 **Inspector**: Validate your implementation against specs.
*   🎮 **Playground**: Explore protocols interactively.
*   🛡️ **Security Analyzer**: Check signatures and mandates.

---

# **The x402 Flow: Micropayments** ⚡

*HTTP 402 "Payment Required" for pay-per-request APIs.*

![h:400](https://kroki.io/mermaid/svg/eNptkLFuwzAMRHd9BWcHcIJsXeq5mzJkUGRRMRFJFCRKTfL1lWMnCIoCgsC7O95hLbdcLNnHR80M8GvOO_SjZQ8T00qjBE19O_gndsCCsKU-eLpB0uXsG5gpXCNy5-GCRLexGP5OOADJa3pM4kkva-rR2-daefNfKiEYwTz19w7ek0r4I_JNz_JklaJ6MFhxQRM4h62hXs7RxRChmN0sOZJ6J5wg2TemTaF-CXMCH9LLOA7tzfqLfzU9e-xnrvt0jAvoLmcNnP14TPyJv1-uSL8BJbaI2Q==)

**Use Case**: AI model access, premium data APIs, content paywalls.

> APS simulates the **402 response** and **signature verification**.

---

# **The AP2 Flow: Multi-Agent** 🤖🤖

*Google's AP2 enables agent-to-agent commerce with user protection.*

![h:380](https://kroki.io/mermaid/svg/eNp1kMFqwzAMhu99Cm0aJLQl9NpLTzsMdtgDKEZSiGtsB1tp0reflCxhZRgMQvz_J30ihLNvPNd4LaYB8GvOe3SjJQ8909oWBmbq28FPCWB_MrRRFxW3kUxy1q4sMY_lWdBPWqFzP6C4k93Rlc7-K9A7ku80J3GzXjZbxxfstfLyL0UIjsE2-Xr3byGFP6J99EyPGhTF3dWMPRrI8bbQ0Ef4R6YSsfLDNHmye5FXxvHQ3dFNlrZxDZv-Xc0fU5g47KNwjEvYb3IWwNm3Q6Bv_PpyAdZvC6qR2A==)

**Key Innovation**: Mandates ensure agents can't spend beyond limits.

> APS includes **OTP challenge** and **credentials provider** simulation.

---

# **The Technical Architecture** ⚙️

I built a full-stack testing platform to demonstrate end-to-end agent payment flows.

![h:280](https://kroki.io/mermaid/svg/eNp1j8EKwjAQRO_5imVPCgXxbr14UhFED0Ive1iTtQnGTdhshX6926oiepi7vJl5e6bFhCOjf9XJBn5TG4AMSugCp6IHT9Q0X-_AqEFkF9yFPExEbr67ISHOQyj2wk9TOpnQWj9bYKssDZqVPjrIIlCn4gOJ9DJY2-F7TxuE86gRSr8gJ1i6UT-q3VDdMvKlFN8d53iBH6_3g40Lv7BzprMnHNjz9AP6WIAc)

*   **Frontend**: React + TypeScript + Vite
*   **Backend**: FastAPI + Pydantic (Mock Servers)
*   **Docs**: 8 documentation files, 3 Architecture Decision Records

---

# **Demo Mode: Works Everywhere** 🌐

*The live demo runs on GitHub Pages (static hosting). How?*

<div class="columns">
<div>

### **The Challenge**
GitHub Pages has **no server**.
API calls would fail.

### **The Solution**
*   Detect `github.io` hostname.
*   Return **realistic mock data**.
*   Show clear **Demo Mode** banner.

</div>
<div>

### **Developer Experience**

```
⚠️ Demo Mode

Running with mock data. 
For live API calls, run:

uvicorn app.main:app --port 8080
```

> Users understand the limitation and can run locally for full testing.

</div>
</div>

---

# **Why This Matters** 🌟

This project reflects my ability to bridge **Emerging Tech** and **Real Products**:

1.  **Problem-First Thinking**: 
    Started with "developers can't test agent payments" - not "let me build cool tech".

2.  **Protocol Expertise**: 
    Deep understanding of 4 competing agentic commerce standards.

3.  **Full-Stack Execution**: 
    Built React frontend, Python backend, documentation, and CI/CD.

4.  **Developer Experience**: 
    Focused on making complex protocols **accessible and testable**.

---

# **About Me** 👨‍💼

**Sivasubramanian Ramanathan**
*Product Owner | Fintech, Payments & Digital Innovation*
*PMP | PSM II | PSPO II*

I specialize in taking messy, real-world complexity and structuring it into reliable products.

**Open for roles that sit between policy, technology, and stakeholder engagement.**

Previous: **BIS Innovation Hub Singapore** - Cross-border payments, CBDCs, regulatory innovation.

---

# **Let's Connect** 🤝

I am ready to bring this level of product thinking and technical depth to your team.

*   🌐 **Portfolio**: [sivasub.com](https://sivasub.com)
*   💼 **LinkedIn**: [linkedin.com/in/sivasub987](https://www.linkedin.com/in/sivasub987/)
*   💻 **Code**: [github.com/siva-sub/AgentPayment-Sandbox](https://github.com/siva-sub/AgentPayment-Sandbox)
*   📚 **Docs**: [Full Documentation](https://github.com/siva-sub/AgentPayment-Sandbox/tree/main/docs)

<br>

**Live Demo**:
[siva-sub.github.io/AgentPayment-Sandbox](https://siva-sub.github.io/AgentPayment-Sandbox/)
