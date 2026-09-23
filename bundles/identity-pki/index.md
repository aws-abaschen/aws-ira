---
okf_version: "0.2"
---
# Identity and PKI

- [On-premises server kinds](server-kinds.md) — Responsibilities, access patterns and identity boundaries by server kind.
- [Server identity model](server-identity.md) — Immutable identifiers and certificate fields.
- [CA and issuance design](ca-design.md) — Centralized hierarchy, issuance permissions and separation of duties.
- [Enrollment and renewal](enrollment-renewal.md) — Bootstrap, local keys, renewal and decommissioning.
- [Configuration automation](configuration-automation.md) — Configuration management and the custom renewal-agent contract.
- [Kubernetes integration](kubernetes.md) — Cluster controller identity and isolated job credentials.
- [Update log](log.md) — Bundle history.

# Related bundles

- [Architecture decision](../architecture/adr-001.md) — Governing design.
- [Job authorization](../job-authorization/index.md) — Product/run authorization after node authentication.
- [Operations](../operations/index.md) — Recovery and production verification.
