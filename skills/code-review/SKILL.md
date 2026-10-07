---
name: code-review
description: Comprehensive guidelines for automated code reviews, syntax validations, and architectural improvements.
---

# Code Review & QA Skill

## Checklist
1. **Correctness & Edge Cases**:
   - Null / Undefined checks
   - Error handling and recovery
   - Resource cleanup (files, sockets, database transactions)
2. **Design & Architecture**:
   - Adherence to project patterns
   - High cohesion, low coupling
   - Separation of I/O and business logic
3. **Performance**:
   - N+1 query prevention
   - Efficient memory allocations and streaming
4. **Testing**:
   - Unit tests covering happy and edge-case paths
