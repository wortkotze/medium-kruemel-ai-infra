---
name: devops-triage
description: Incident triage protocol for DNS, Cloudflare tunnels, and CI/CD pipelines.
---

# DevOps & Incident Triage Skill

## Triage Protocol
1. **Network & DNS Health**:
   - Query Cloudflare DNS records for correct proxy / orange-cloud settings.
   - Inspect Tunnel daemon connectivity.
2. **CI/CD Pipeline Diagnostics**:
   - Query GitHub Actions workflow runs for the failing commit.
   - Extract the failure step and traceback from execution logs.
3. **Rollback & Mitigation**:
   - Generate actionable CLI commands to rollback deployments or toggle DNS failovers.
