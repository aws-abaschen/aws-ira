---
type: Acceptance Plan
title: Security and operational acceptance tests
description: Required evidence before deploying shared-runner workload identity in production.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
---
# Security and operational acceptance tests

These are future integration tests for the implementation, not claims of completed execution. Use separate sandbox accounts and synthetic data. Capture configuration hashes, request IDs, timestamps and actual allowed/denied service operations. IAM policy simulation is useful but cannot replace end-to-end certificate, API, broker and resource-policy tests.

| ID | Scenario | Required result |
|---|---|---|
| A01 | Two valid unique node certificates use the same runner role | Success; distinct node identity and certificate audit |
| A02 | Unknown CA, wrong OU, missing CN mapping, expired/revoked leaf | No runner credentials |
| A03 | Certificate for n-0042 invokes n-0043 path | Explicit IAM denial, including with API resource-policy allow |
| A04 | Missing tag or encoded/ambiguous node path | Denial; no parser discrepancy |
| A05 | Valid runner calls target STS or product S3 directly | Denial |
| A06 | Valid node and valid assigned run | Only registered target role and scope returned |
| A07 | Modified product/job/role/digest in grant | Denial |
| A08 | Valid grant submitted by different node or old placement generation | Denial |
| A09 | Expired token, wrong audience/issuer/algorithm or unknown key | Denial |
| A10 | Concurrent launch-token replay with different request IDs | No independent unauthorized lease |
| A11 | Exact retry during broker crash before/after STS | Recoverable, scoped result with reconciled audit; no scope expansion |
| A12 | Product A job accesses product-b resources or another run's data | Denial at actual resource API |
| A13 | Broker omits required narrowing policy or adds extra tag | Broker rejects; verify target baseline limits blast radius |
| A14 | Same-account resource policy grants a session extra access | Explicit denies or guardrails block it; otherwise fail readiness |
| A15 | Adjacent job reads socket/cache, ptraces or reuses another run ID | Denial at OS/agent boundary |
| A16 | Job accesses node key or node-wide credential listener | Denial |
| A17 | Long job refreshes across two certificate rotations | Success with fresh authorization each time |
| A18 | Job SDK ignores credential_process or inherits broad credentials | Detected; launch fails or corrected provider used |
| A19 | Cancellation with already-issued target session | Refresh denied; document residual access; emergency deny stops real data operation |
| A20 | Node revoked during CA publication/import lag | Broker deny blocks issuance immediately after committed update; CRL eventually rejects new sessions |
| A21 | CA rollover and expired-issuer bootstrap recovery | Tested continuation/re-enrollment without static AWS keys |
| A22 | Kubernetes wrong namespace, SA, pod UID, audience or deleted pod | Denial |
| A23 | Tenant tries to use issuance controller or trusted adapter SA | Admission/RBAC denial |
| A24 | Region failover with old grants and stale replay replica | Old epoch fenced; only fresh active-region grants accepted |
| A25 | Broker loses audit, replay store or current scheduler liveness | Issuance fails closed |
| A26 | Target account leaves approved Org/OU or capability is withdrawn | Registry disabled; target trust/active sessions handled per runbook |
| A27 | Peak launch burst and two-times capacity target | Controlled queuing/retries; no authorization shortcuts |
| A28 | S3/KMS/multipart or other actual application dependencies | Required operations pass; unrelated operations still fail |
| A29 | Reconstruct one resource event to node/product/team/definition | Complete audit linkage without secret logging |
| A30 | Broker or registration role compromise drill | Containment covers future issuance and already-issued credentials |

## Evidence and sign-off

For each test, retain expected/actual outcome, responsible owner, test environment, policy/agent version, evidence URI and unresolved limitations. Security engineering owns the negative-test review; product owners confirm functional scope; platform operations confirms recovery and alerting. Failed authorization-boundary tests block shared-pool production use.

Repository validation checks document structure, JSON syntax, links and diagram consistency. It does not run this matrix or certify the security implementation. See [rollout](rollout.md) for implementation dependencies.
