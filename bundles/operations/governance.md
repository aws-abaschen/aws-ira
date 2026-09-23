---
type: Operating Model
title: Governance and entitlement ownership
description: Ownership, review and lifecycle controls for products, jobs and target accounts.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
---
# Governance and entitlement ownership

| Activity | Accountable function | Implementer | Required consultation |
|---|---|---|---|
| CA hierarchy and issuance profile | Enterprise PKI | PKI platform | Security architecture |
| Node identity and retirement | Infrastructure platform | Provisioning and configuration team | Asset owner |
| Scheduler attestation | Batch platform | Scheduler integration team | Security engineering |
| Broker and replay controls | Identity platform | Platform engineering | Security engineering |
| Product/job resource access | Product owner | Product team and cloud platform | Resource/data owner |
| Target IAM policies and account baseline | Cloud platform | IaC pipeline | Product owner and security |
| Organization audit and incident coordination | Security operations | SOC and platform on-call | Affected product teams |
| Kubernetes identity controls | Container platform | Cluster operators | Product teams |

These are proposed functional owners. Assign actual teams and support rotations before production. Product ownership does not confer CA administration, broker administration or the right to modify the common runner role.

## Entitlement record

```yaml
capability_id: product-a-job-a-prod
product_id: product-a
owner_team: team-a
environment: prod
job_id: job-a
definition_digest: "sha256:EXAMPLE_REPLACE_WITH_REAL_DIGEST"
allowed_pools: [batch-prod-eu]
target_account: "222222222222"
target_role_arn: arn:aws:iam::222222222222:role/product/product-a/prod/job-a
session_policy_template: job-a-per-run-v1
max_session_seconds: 900
state: active
registry_version: entitlements-0042
```

Production records also contain approval evidence, validity/review date, resource ownership, target account/OU verification and a hash of deployed role policies. Use immutable snapshots with controlled activation; the broker reads only published snapshots. Jobs and node agents cannot publish registry entries.

## Change workflow

Product owner proposes capability and justification. Resource owner confirms scope. Cloud platform renders exact IAM policies and runs positive/negative checks. Independent reviewer approves. The pipeline deploys the target role before activating the matching registry version. The scheduler deploys the approved definition referencing that version. Record all hashes and approvals.

For permission reduction, stop new issuance first, deploy the narrower role/registry, and assess existing sessions. For emergency withdrawal, follow [incident response](incident-response.md). Avoid a rollout interval in which a new broad registry entry points at an old permissive role.

Review active entitlements periodically, proposed every 90 days, and immediately on ownership change, job retirement or account movement. Account offboarding removes capability mappings, invalidates leases and removes broker trust. Rotate or revoke machine identity when a node changes environment or trust domain.

Use organization guardrails and IaC drift detection to prevent bypass roles, alternate profiles, unapproved CA issuance and resource-policy grants. A service control policy is an upper bound, not a replacement for a target role permission policy. Related: [authorization model](../job-authorization/authorization-model.md).
