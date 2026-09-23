---
type: Security Model
title: Product and job authorization model
description: Distinguish machine authentication from product ownership and AWS permission enforcement.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
sources:
  - id: create-session
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/authentication-create-session.html
  - id: boundary
    resource: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
---
# Product and job authorization model

## Distinct identities

| Identity | Example | Established by |
|---|---|---|
| Team | `team-a` | Corporate ownership registry |
| Product | `product-a` | Product registry with accountable team |
| Job definition | `job-a@digest` | Reviewed scheduler deployment |
| Run | `r-01abc` | Trusted scheduler control plane |
| Node | `n-0042` | Asset registry and CA enrollment |
| Runner principal | `OnPremRunnerProd` | Roles Anywhere certificate authentication |
| Broker principal | `CredentialBrokerProd` | AWS runtime identity |
| Product session | Target `job-a` role, run-tagged | Broker-controlled STS request |

A team can own multiple products and ownership can change without changing NodeId. Product roles should not use a mutable team display name as their primary authorization key. A job can have explicit dependencies in several accounts; represent each approved capability separately rather than allowing arbitrary account selection.

## Enforcement layers

1. **Enrollment** admits an approved machine into a specified runner trust domain.
2. **Roles Anywhere trust/profile** permits that machine to obtain only the common runner role. `CreateSession` references a profile and role; profile session policies are not a per-job request policy API.[^create-session]
3. **Runner IAM policy** permits only the machine's broker path, with explicit denial of direct role assumption and paths for other nodes.
4. **Broker authorization** verifies the scheduler grant and registry, selects the role and constructs all authorization metadata.
5. **Target-role trust** admits only approved broker principals, with organization and required-tag restrictions.
6. **Target-role permissions** enforce product/job-class action and resource scope. Use different roles when jobs have materially different privileges.
7. **Run session policy** further limits particular inputs and outputs. Broker omission is a security failure; target baseline limits its impact.
8. **Resource policy, SCP/RCP where applicable, boundaries and service controls** must be evaluated for the actual service and principal type. Explicit denies take precedence, while direct resource-policy grants to session principals can bypass some implicit limits.[^boundary]

Session names are correlation labels. Tags can participate in authorization only because the broker controls their values and IAM policies enforce their use. Merely adding `ProductId` does not limit resource access.

## Role granularity

Default: one target role for each product, environment and stable job permission class. Multiple equivalent job definitions may share a class after review. Do not create one role per execution; that creates lifecycle churn. Do not create one broad product role when one product contains low- and high-privilege jobs.

Prefer explicit resource ARNs/prefixes initially. Use ABAC only where the service supports the necessary condition keys for every operation and resource-tag mutation is controlled. Keep object versus bucket actions, encryption-key permissions and downstream service roles in the entitlement review.

Generic execution permissions such as unrestricted `iam:PassRole`, starting arbitrary compute, changing Lambda code, reading unrelated secrets or decrypting a broad key can escape the intended job boundary. Model those as capabilities with additional constraints and tests.

Related: [broker](broker-contract.md), [policy examples](policy-examples.md), [governance](../operations/governance.md).

[^create-session]: [Roles Anywhere CreateSession request](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/authentication-create-session.html).
[^boundary]: [IAM permission evaluation and session principals](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html).
