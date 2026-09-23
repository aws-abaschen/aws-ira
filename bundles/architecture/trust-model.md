---
type: Threat Model
title: Trust boundaries and threat model
description: Threats, preventive controls and residual risks for shared enterprise runners.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
---
# Trust boundaries and threat model

The design in [ADR 001](adr-001.md) protects one ordinary job from another, assuming the scheduler, broker, registration authority and execution isolation are trustworthy. It does not claim to protect jobs from a compromised host kernel or platform administrator.

| Boundary | Trusted assertion | Untrusted input |
|---|---|---|
| Asset registry to registration authority | Approved immutable NodeId, environment and node lifecycle | Hostname, IP, self-reported facts and CSR subject |
| Certificate to Roles Anywhere | Possession of approved node key | Desired AWS role/profile and session label |
| Scheduler to broker | Approved definition, assigned node, active run and product mapping | Job environment variables and command-line arguments |
| Broker to target account | Authorized job class and constrained run metadata | Caller-selected role ARN, policy JSON or session tags |
| Agent to job | Credentials for the authenticated local sandbox | Socket client claims about UID, PID or run ID |
| Job to AWS resource | Signed requests authorized by target session | Resource names outside the approved scope |

## Attack analysis

| Threat | Required control | Residual exposure / evidence |
|---|---|---|
| Job says it belongs to another product | Signed scheduler grant; server-side registry mapping | Scheduler administrators remain trusted; test altered grant |
| Node A replays a grant assigned to node B | Certificate-bound API path and grant NodeId comparison | Node B root can impersonate B; test wrong-node invocation |
| Job steals another job's credentials | Distinct sandbox identity, private socket and cache | Same UID and privileged containers defeat isolation |
| Copied VM clones machine identity | Generate keys after provisioning; prohibit key-bearing images | Nonexportable key plus asset registry duplicate detection improves assurance |
| Enrollment request asks for another CN or production OU | Registration authority constructs approved identity fields | CA issuer credentials can mint arbitrary identities if compromised |
| Common runner directly assumes product role | Explicit STS deny; target trust admits only broker | Administrators could change policy; monitor drift |
| Broker omits run session policy | Target role limited to job class; explicit deny in narrowing policy when present | Same-job-class runs may overlap if broker fails; high assurance needs separate role/resource boundary |
| Resource policy bypasses intended limits | Prohibit direct session-ARN grants; review service-specific authorization; explicit deny confinement | Service semantics need live negative tests |
| Product changes tags to gain access | No resource-tag mutation in job roles; controlled registry updates | ABAC is unsuitable where tags cannot be governed |
| Compromised CA or broker | Separate issuers, environments and target-role allowlists; emergency denies | A central trust service has a broad blast radius |
| Replayed launch token or refresh capability | Atomic consumption, per-run lease, short TTL, node and sandbox binding | Region failover must preserve replay guarantees |
| Workload executes arbitrary privileged AWS code | No IAM write, PassRole or generic compute-launch privileges by default | Approved delegation requires a separate escalation analysis |
| Log or artifact exfiltrates credentials | Redaction, no debug body logging, restrictive runtime mounts | Jobs can intentionally disclose their own credentials; restrict egress where justified |

## Stronger isolation tiers

**Tier 1:** trusted internal batch jobs, distinct OS users/containers and agent-enforced access control. **Tier 2:** separate VM or microVM per product/run, hardened host administration. **Tier 3:** dedicated product hosts or clusters and separately scoped broker role. Select the tier based on impact and adversarial assumptions, not just container availability.

Explicitly review the scheduler as a privileged code-execution system. A user able to modify a trusted product job definition can act with that job's permissions. Approval of a definition digest must include its scripts, image digest, referenced secrets, execution identity and mutable dependencies.

See [acceptance tests](../operations/acceptance-tests.md) for adversarial evidence and [incident response](../operations/incident-response.md) for containment.
