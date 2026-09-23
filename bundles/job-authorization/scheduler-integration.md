---
type: Integration Contract
title: Scheduler attestation and execution binding
description: Proposed adapter contract for authorizing runs dispatched to shared execution nodes.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
---
# Scheduler attestation and execution binding

The trusted scheduler adapter is a custom integration to implement against the enterprise's supported scheduler APIs/events. No specific scheduler feature, token format or version is assumed. The adapter runs in the scheduler control plane, outside product job code, and owns a signing key unavailable to workers.

## Job registration

Product owners submit the job ID, product, definition digest/version, approved image/script dependencies, target capability, execution pool and environment. Platform review publishes a versioned entitlement record. Scheduler deployment and entitlement publication reference the same immutable definition. Changes to Run As identity, scripts, images, mutable includes or target capabilities require reauthorization.

At dispatch, the adapter obtains the actual run ID and assigned node from authoritative scheduler state. It must not sign claims copied from job-controlled environment variables. If the scheduler can move a job, issue a new grant bound to the new node and a new placement generation; invalidate the old generation before redispatch.

## Proposed launch-grant payload

```json
{
  "iss": "https://scheduler.corp.example/attestor",
  "aud": "corp-aws-job-broker-prod",
  "sub": "scheduler:prod:job-a",
  "jti": "g-019abc",
  "iat": 1790164800,
  "nbf": 1790164800,
  "exp": 1790164920,
  "run_id": "r-01abc",
  "job_id": "job-a",
  "definition_digest": "sha256:EXAMPLE_REPLACE_WITH_REAL_DIGEST",
  "product_id": "product-a",
  "environment": "prod",
  "node_id": "n-0042",
  "placement_generation": 1,
  "capability_id": "product-a-job-a-prod",
  "registry_version": "entitlements-0042",
  "sandbox_binding": "sandbox-81b4"
}
```

Times and digest are illustrative. The broker validates a pinned algorithm and trusted issuer key, rejecting unsigned tokens, unknown `kid`, algorithm substitution and duplicate/ambiguous claims. Use a standard signed-token implementation; this document specifies claims, not a new cryptographic protocol. Publish signing keys through an authenticated, controlled channel. New issuer keys require explicit trust publication; a token cannot supply its own trusted key URL.

The grant intentionally contains a capability ID rather than an arbitrary role ARN or policy. The registry resolves the capability to account, role and scope. A valid signature is necessary but not sufficient: live run state, definition, registry and node placement must agree.

## Local execution contract

The platform launcher creates a distinct sandbox and a private credential socket. It registers the scheduler run-to-sandbox binding with the privileged agent before executing product code. Authentication uses kernel-provided peer credentials plus a trusted launch record; a caller cannot gain a run by passing its ID on the command line.

For concurrent jobs, use separate OS identities, private PID/filesystem namespaces or stronger VM isolation. A shared scheduler execution user with access to every credential directory does not meet this contract. Prevent ptrace, `/proc` environment inspection, inherited descriptors and writable helper replacement across jobs. Product-controlled scripts cannot invoke privileged launcher operations or edit registration state.

The launch grant is held by the agent, not added to job logs. For Kubernetes, include cluster ID, namespace, service account and pod UID as binding fields and use the [cluster adapter](../identity-pki/kubernetes.md).

## Cancellation and retry

Cancellation, job end and ownership withdrawal invalidate the active lease and stop refresh. A retry gets a new run/attempt identifier and nonce. A node failover changes placement generation and requires a new grant. The broker still applies the [issued-credential containment rules](../operations/incident-response.md): stopping refresh cannot revoke a credential already held by a job.

If reliable attestation and local sandbox binding are unavailable, route jobs to dedicated product pools with product-specific permissions. Do not approximate this contract by trusting a scheduler variable named `PRODUCT_ID`.
