# Zero-Trust Prompting: Stopping PII Leaks and Compliance Traps in Enterprise AI

**Why local LLMs alone are not a silver bullet for data privacy, and how we built automatic PII redaction and tamper-proof audit trails into our gateway.**

---

![Zero-Trust PII Shield](../images/02_zerotrust_pii_shield.jpg)
*Figure 1: Zero-Trust Prompt Interception — Sensitive financial credentials, names, and API secrets sanitized in real time before reaching external cloud models.*

---

## 1. The Dangerous Myth of "We Just Run a Local Model"

When enterprise security teams express concern over language model compliance (GDPR, HIPAA, SOC 2, ISO 27001), engineering leads often respond with a reassuring wave of the hand:
> *"Don't worry. We run a local open-source model inside our private VPC. Our data never leaves our network."*

This is one of the most pervasive — and dangerous — myths in modern AI engineering.

In real-world production environments, pure isolation rarely holds:
1. **Dynamic Fallbacks Leak Plaintext:** As demonstrated in Part 1, high-reliability architectures use automatic cloud fallbacks (e.g. DeepSeek or Claude) when local inference nodes time out. The moment a fallback triggers, raw unscrubbed prompts leave your perimeter.
2. **Autonomous Agents Ingest External Data:** An autonomous agent reading customer tickets, parsing git commits, or scraping internal documentation will inevitably encounter real customer names, IBANs, internal IP addresses, and private API keys.
3. **Embeddings & Vector Stores are Long-Lived:** When unscrubbed prompts are embedded into vector databases (Qdrant), personal data is permanently stored in indexes without data subject deletion controls.

Running a local model is **not a data privacy strategy**. 

True enterprise compliance requires a **Zero-Trust Prompting Architecture**: an automated "Iron Curtain" situated directly at the proxy layer that inspects, sanitizes, and audits every character before an LLM ever sees it.

---

## 2. Shift-Left AI Security: Redaction Before Dispatch

Security cannot be the responsibility of individual agent developers. If five different teams write LangGraph agents, relying on each developer to manually sanitize strings will guarantee an eventual leak.

Instead, security must be enforced **centrally at the Gateway Layer**:

```
[Agent Micro-Worker]
       │
       ▼ (Raw Prompt with PII)
┌─────────────────────────────────────────────────────────────┐
│                 Central Gateway Proxy                       │
│  1. Secret Scanner (Detect API keys, passwords, private SSH)│
│  2. Entity Recognizer (Detect names, emails, phones, IBANs) │
│  3. Deterministic Pseudonymizer (Map to <PERSON_1>, etc.)   │
└─────────────────────────────────────────────────────────────┘
       │
       ▼ (Sanitized Prompt)
[Local Model / Cloud LLM Provider]
```

### Why Deterministic Pseudonymization Matters
Naive redaction replaces sensitive strings with static labels like `[REDACTED]`. This breaks language model reasoning:
> *"User [REDACTED] requested a transfer of €500 to recipient [REDACTED] using account [REDACTED]."*

The LLM cannot tell if the sender and recipient are the same entity!

**Deterministic Pseudonymization** preserves entity relationships without exposing real data:
> *"User `<PERSON_1>` requested a transfer of €500 to recipient `<PERSON_2>` using account `<IBAN_1>`."*

The model understands the business logic perfectly, yet zero Personally Identifiable Information (PII) is transmitted.

---

## 3. Implementing the Redaction Hook

Inside our gateway architecture ([`gateway/server.py`](https://github.com/wortkotze/medium-kruemel-ai-infra/blob/main/gateway/server.py)), we implement an asynchronous pre-call interceptor:

```python
import re
from typing import Dict, Tuple

class ZeroTrustSanitizer:
    # High-precision regex patterns for immediate scrubbing
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    IBAN_PATTERN = re.compile(r'\b[A-Z]{2}[0-9]{2}(?:[ ]?[0-9]{4}){4,7}\b')
    KEY_PATTERN = re.compile(r'(?:sk-[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9]{36}|AKIA[0-9A-Z]{16})')
    IPV4_PATTERN = re.compile(r'\b(?:10|172\.(?:1[6-9]|2[0-9]|3[01])|192\.168)\.[0-9]{1,3}\.[0-9]{1,3}\b')

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, Dict[str, str]]:
        entity_map = {}
        
        # 1. Scrub Secrets & API Tokens Immediately
        text = cls.KEY_PATTERN.sub("<SECRET_API_KEY_REDACTED>", text)
        
        # 2. Scrub Internal Infrastructure IP Addresses
        text = cls.IPV4_PATTERN.sub("<INTERNAL_IP_MASKED>", text)

        # 3. Deterministically Pseudonymize Personal Emails
        for idx, email in enumerate(cls.EMAIL_PATTERN.findall(text), 1):
            placeholder = f"<EMAIL_{idx}>"
            entity_map[placeholder] = email
            text = text.replace(email, placeholder)

        # 4. Deterministically Pseudonymize Financial IBANs
        for idx, iban in enumerate(cls.IBAN_PATTERN.findall(text), 1):
            placeholder = f"<IBAN_{idx}>"
            entity_map[placeholder] = iban
            text = text.replace(iban, placeholder)

        return text, entity_map
```

When an agent invokes `/v1/chat/completions`:
1. The incoming message payload passes through `ZeroTrustSanitizer.sanitize()`.
2. Any hardcoded API keys or private VPC subnets are irreversibly redacted.
3. Personal entities are replaced with consistent tokens.
4. The sanitized payload is forwarded to LiteLLM.

---

## 4. Re-Hydration: Returning Natural Answers to Authorized Users

If an agent is generating an email response or drafting a customer service reply, the end-user expects to see the actual customer name, not `<PERSON_1>`.

This is solved via **Egress Re-Hydration**:
1. The gateway retains the transient `entity_map` in memory during the request lifecycle.
2. When the model streams its completion chunks back, the gateway substitutes the tokens in reverse:
   `<PERSON_1>` $\rightarrow$ `Alice Schmidt`.
3. The response delivered to the verified end-user is complete and natural.
4. **The provider logs, vector memory, and cloud traces only ever saw the pseudonyms.**

---

## 5. Tamper-Proof Audit Trails in Langfuse

Security teams require proof that compliance rules are functioning as designed.

In our stack, LiteLLM and Langfuse are configured to log the **sanitized request trace**:
* System administrators reviewing execution traces in Langfuse (`:3000`) see the reasoning chain, tool inputs, and performance metrics without seeing customer PII.
* If a security incident occurs, compliance officers can cross-reference the anonymized trace ID with internal encrypted audit logs.

---

## The CISO Sign-Off Checklist

Before shipping an autonomous multi-agent platform into production, ensure you can answer "Yes" to each of the following:

- [x] **Pre-Call Interception:** Are all outgoing prompt payloads scanned for secrets and PII prior to network transmission?
- [x] **Deterministic Pseudonymization:** Are entities replaced with consistent relational tokens rather than static strings?
- [x] **Secret Scanning:** Are cloud tokens (`sk-...`, AWS keys, GitHub PATs) irreversibly scrubbed at the gateway?
- [x] **Audit Trace Sanitization:** Do observability systems (Langfuse, ClickHouse) store scrubbed payloads rather than raw customer data?
- [x] **Air-Gapped Tooling:** Are search tools (SearXNG) and browser scraping engines (Browserless) hosted locally without third-party tracking?

---

*Inspect the complete Zero-Trust Gateway implementation on GitHub:*  
👉 **[GitHub: wortkotze/medium-kruemel-ai-infra](https://github.com/wortkotze/medium-kruemel-ai-infra)**  
👉 **[GitHub: wortkotze/medium-kruemel-ai-agents](https://github.com/wortkotze/medium-kruemel-ai-agents)**
