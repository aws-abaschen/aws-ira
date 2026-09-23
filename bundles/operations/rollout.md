---
type: Implementation Plan
title: Rollout and onboarding
description: Deliverable list, phased implementation and production acceptance gates.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
---
# Rollout and onboarding

## Implementation components

| Component | Build/configure | Acceptance evidence |
|---|---|---|
| Network and DNS | DX routes, Resolver rules, regional interface endpoints, security groups | Private connectivity from every site and failover path |
| PKI | Hierarchy, profiles, issuance role, CRL publication/import | Enrollment, renewal, revocation and CA rollover tests |
| Roles Anywhere | Anchors, profiles, common runner roles, mappings | Unique node sessions and rejected invalid identities |
| Registration service | Custom bootstrap/asset registry validation and CSR workflow | Impersonation and duplicate-identity tests |
| Node agent | Custom signer integration, local authorization and refresh | Isolation and credential-provider tests per OS |
| Scheduler adapter | Custom trusted launch attestations and liveness feed | Definition/node binding, cancellation and retry evidence |
| Broker | Custom API, authorization, registry, replay store and audit | Cross-product denial and crash/replay tests |
| Target IAM | Job-class roles, resource/key policies, organizational guardrails | Access Analyzer and real service action tests |
| Kubernetes adapter | Pod identity validation, issuance restrictions, private delivery | Wrong-pod/service-account/namespace denial |
| Operations | Dashboards, paging, support ownership, incident automation | Tabletop and controlled failure drill |

This repository delivers architecture documentation and illustrative policies, not the implementations above. Do not treat names used in the contracts as installed software.

## Phases

1. **Confirm environment:** supported regions, scheduler version/API capabilities, Linux/Windows execution identities, asset registry source, CA hierarchy, compliance requirements and expected job volume. Assign owners.
2. **Establish nonproduction foundation:** identity account, CA, endpoints, audit, initial runner policy and one enrollment service. Demonstrate bootstrap without static AWS keys.
3. **Implement job boundary:** scheduler adapter, sandbox launcher, broker and two product roles. Use the [worked example](../job-authorization/worked-example.md) as the first fixture.
4. **Run adversarial pilot:** two shared nodes, concurrent jobs, long jobs and one cluster. Pass the [acceptance matrix](acceptance-tests.md), including policy omission and resource-policy cases.
5. **Operational readiness:** prove renewal through an outage, CRL lag alarms, emergency denies and regional fencing. Measure actual capacity, costs and recovery times.
6. **Production canary:** deploy separate production issuers/roles/registries, onboard a small product set and observe one complete certificate lifecycle and batch peak.
7. **Expand:** onboard by capability, retire old access keys only after usage review and cutover evidence, and review drift regularly.

## New server onboarding

Register machine identity and owner; classify its [server kind](../identity-pki/server-kinds.md), additional responsibilities and AWS access requirement; approve its environment and identity pattern. Machines without an outbound AWS use case do not need AWS credentials. For shared executors, approve the pool, install the managed agent, enroll a locally generated key, verify own-path broker access and other-path denial, then enable scheduler placement. Dedicated services follow their separately reviewed service-role configuration. A successful certificate issuance alone does not authorize jobs.

## New product/job onboarding

Identify accountable team and resource owners; specify exact actions/resources and downstream dependencies; create job-class role; register immutable definition and capability; validate grant binding; run allowed and forbidden operations; approve production activation. Add explicit KMS, S3 multipart or bucket-list permissions only when the workload requires them.

## Rollback

Disable new scheduler grants for the affected capability and revert to a previous reviewed registry/agent version. Existing sessions retain their original expiry unless denied. If the prior solution requires broad/static credentials, rollback means pausing jobs or using separately approved dedicated pools; do not automatically restore weaker permissions.

Production approval is an enterprise adoption gate for the future implementation, not a request to approve this documentation task.
