---
type: Identity Model
title: Server identity model
description: Stable machine identity and controlled X.509 attributes for IAM Roles Anywhere.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
sources:
  - id: trust
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html
  - id: mapping
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/attribute-mapping.html
---
# Server identity model

Assign every server or trusted cluster adapter an immutable asset registry identifier, for example `n-0042`. The identifier is allocated by the registration authority, not selected by a job. Keep stable identity separate from hostname, IP address, physical asset and certificate serial. A rebuilt or reassigned machine must undergo explicit asset registry lifecycle handling; never silently inherit a retired identity's key.

| Field | Example | Authority / purpose |
|---|---|---|
| NodeId | `n-0042` | Asset registry; primary machine key |
| AssetId | `asset-78c2` | Asset management; links hardware or VM |
| PrimaryKind / AdditionalKinds | `batch-executor` / `[]` | Approved operational responsibilities; see [server kinds](server-kinds.md) |
| AwsAccessPattern | `per-run-broker` | Approved identity pattern; classification alone grants no permission |
| IdentityClass | `batch-prod` | Registration authority's certificate/admission configuration reference |
| NodePool | `batch-prod-eu` | Platform approval; permitted scheduler placements |
| Environment | `prod` | Platform approval; separate trust domain |
| OwnerTeam | `batch-platform` | Operational accountability, not product authorization |
| Hostname | `batch-exec-42.corp.example` | Mutable operational locator |
| Public-key fingerprint | SHA-256 SPKI digest | Enrollment continuity and clone detection |
| Certificate serial and issuer | Issuance outputs | Revocation and audit |

## Proposed leaf certificate

The example below is for a batch execution node. The [server-kind catalog](server-kinds.md) distinguishes other machines, dedicated services and Kubernetes workloads. A server that does not call AWS does not require an IAM Roles Anywhere authentication certificate simply to maintain a machine record.

```text
Subject: O=ExampleCorp, OU=batch-prod, CN=n-0042
SAN URI: urn:examplecorp:node:n-0042
Basic constraints: CA=false
Key usage: digitalSignature
Extended key usage: clientAuth
Public key: ECDSA P-256 or approved RSA profile
Validity: 24 hours (proposed)
```

Roles Anywhere requires a suitable X.509v3 end-entity certificate and a signature-capable key; its trust policy supports certificate-derived attributes.[^trust] The chosen `clientAuth` EKU is an enterprise profile choice, not a claim that Roles Anywhere requires this EKU. Use one CN, one OU and one identity SAN. Restrict NodeId to `n-[a-z0-9-]{1,40}` and do not embed wildcards, slashes or user-controlled Unicode in IAM policy-variable values.

Configure the Roles Anywhere profile to map subject CN and OU explicitly. Mappings control which certificate attributes become principal tags.[^mapping] The role trust requires the expected OU and a present NodeId. The runner's invoke policy uses `aws:PrincipalTag/x509Subject/CN` to bind the broker API path. Mapping drift must fail the deployment checks.

Each node in the same pool has a different certificate and key but assumes the same role. Do not include `ProductId` in the shared node certificate: its lifetime and ownership differ from those of individual runs. Product identity is established by the [scheduler grant](../job-authorization/scheduler-integration.md).

For this short CN format, expect the Roles Anywhere source identity to use its documented `CN=` prefix, for example `CN=n-0042`; confirm the exact event field during the pilot.[^trust] Do not parse an arbitrary caller-selected role session name as NodeId.

[^trust]: [Roles Anywhere trust and certificate rules](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html).
[^mapping]: [Certificate attribute mapping](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/attribute-mapping.html).
