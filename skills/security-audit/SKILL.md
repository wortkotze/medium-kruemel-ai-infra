---
name: security-audit
description: Protocols for vulnerability scanning, secret leakage prevention, and RBAC analysis.
---

# Security & Vulnerability Audit Skill

## Verification Workflow
1. **Secret Scanning**:
   - Check `.env`, source code, and commit diffs for hardcoded tokens (PATs, API keys, JWT secrets).
2. **Access Control (RBAC)**:
   - Validate that tokens adhere to the Principle of Least Privilege (PoLP).
   - Ensure write tools are restricted to authorized identities.
3. **Data Protection**:
   - Verify that PII is masked before forwarding prompts to external LLMs.
