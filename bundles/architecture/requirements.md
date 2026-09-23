---
type: Requirements
title: Requirements and assumptions
description: Business scope, security invariants and decisions to confirm during implementation.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
---
# Requirements and assumptions

| ID | Requirement | Design response |
|---|---|---|
| R01 | Datacenter and AWS VPCs have bidirectional Direct Connect routing | Reuse transport; explicitly add AWS API endpoints and DNS |
| R02 | Identify each on-premises server | Immutable asset registry ID, unique key and unique certificate |
| R03 | Several batch execution nodes perform the same function | One common runner role per environment/security zone |
| R04 | A node executes jobs from several products | Scheduler attestation plus broker authorization for each run |
| R05 | Teams own products; products own jobs | Versioned product/job/account entitlement registry |
| R06 | Jobs access only their authorized resources | Job-class target roles, run-specific session policies and isolated credential delivery |
| R07 | Target accounts belong to the corporate Organization | Explicit role allowlist, account lifecycle checks and organization conditions |
| R08 | Centralized AWS CA and automated certificates | AWS Private CA in the identity account; enrollment service and centrally managed agent |
| R09 | Include Kubernetes workloads | Per-workload grants and isolation; restricted controller certificate issuance |
| R10 | One ADR and detailed OKF bundles | [ADR 001](adr-001.md) and linked concept bundles |
| R11 | Distinguish on-premises server responsibilities | [Server-kind catalog](../identity-pki/server-kinds.md) with separate machine, service, job and cluster identity boundaries |

## Security invariants

1. A certificate proves a registered machine identity. It does not prove product ownership of arbitrary code running there.
2. Every run has an immutable identifier, a definition digest/version, a product owner and an approved target role.
3. Job input cannot select an unapproved account, role, policy, product or authorization tag.
4. The common runner role has no product-resource permissions and cannot assume target roles.
5. Only the trusted broker can exchange an approved run for product credentials. Certificate enrollment and AWS target-role administration use different privileged identities.
6. A job cannot read another job's credentials or the node identity key. Shared root or shared privileged service accounts violate this assumption.
7. Expired, replayed, canceled, unknown or ambiguous grants fail closed. Outages never enable a broad fallback role.
8. Revoking a certificate does not constitute revocation of already-issued AWS credentials.

## Design assumptions to confirm

The scheduler has a trusted control-plane integration point that can observe approved job definitions and actual node assignment. We propose a custom scheduler adapter; no built-in scheduler signed-token feature is assumed. If this cannot be implemented, use dedicated product execution pools until it can.

Illustrative AWS accounts: identity `111111111111`, product-a production `222222222222`, product B production `333333333333`; Organization `o-exampleorg`; region `eu-central-1`. Replace all values. Production and nonproduction use separate CA issuing hierarchies, profiles, runner roles, broker execution roles and entitlement registries.

Jobs are untrusted relative to other products. Platform administrators, the kernel/hypervisor, scheduler control plane, CA enrollment authority, broker and entitlement pipeline are trusted. For protection against a compromised shared host administrator, allocate separate VMs or nodes per trust domain; ordinary process/container isolation is insufficient.

No AWS estate size, scheduler version, OS mix, compliance retention, CA budget or region pair was supplied. [Rollout](../operations/rollout.md) records the corresponding implementation gates without inventing enterprise facts.
