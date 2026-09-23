---
type: API Contract
title: Credential broker authorization contract
description: Private API request binding, authorization order, replay controls and credential leases.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
sources:
  - id: api-iam
    resource: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  - id: variables
    resource: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html
  - id: sts
    resource: https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
---
# Credential broker authorization contract

The broker is a custom platform service, proposed as a private API Gateway REST API with a Lambda integration, a versioned entitlement registry and a transactional lease/replay store. Equivalent implementations must preserve the same controls. The broker's AWS execution role, not the caller's runner credentials, assumes target roles.

## Authenticated node path

Use one method: `POST /nodes/{nodeId}/credentials`, under stage `prod`, with `authorizationType=AWS_IAM`. Sign the complete request using runner credentials. IAM authorization for API Gateway requires signed requests and an enabled IAM method.[^api-iam]

The runner identity policy allows only a path containing `${aws:PrincipalTag/x509Subject/CN}`. It also explicitly denies `execute-api:Invoke` for all other resources and denies requests with a missing CN tag. IAM supports policy variables in resource identifiers, including certificate-derived principal tags used by this design.[^variables]

**Why the broker can trust the path:** successful API IAM evaluation binds the path to a certificate-derived tag. The broker reads the path and authenticated integration context, validates exact NodeId grammar, and compares it with the signed grant and asset registry. It does not trust a `NodeId` header, job payload or session-name substring. Do not assume API Gateway automatically exposes all STS principal tags to Lambda. This path-binding construction must pass live IAM/API negative tests before production.

Restrict integration invocation to the expected API, stage and method. Reject any other integration route, unsigned invocation or alternate caller role. Test URL normalization, percent encoding, duplicate separators, unexpected suffixes and custom-domain base-path mapping; reject ambiguous paths before authorization logic. Keep explicit identity-policy denies when adding resource-policy allows.

## Requests

```json
{
  "operation": "issue",
  "launch_grant": "SIGNED_TOKEN_REDACTED",
  "idempotency_key": "request-810c"
}
```

For refresh, use `operation=refresh`, an opaque lease handle and a unique request key. Close uses `operation=close` and the same bound lease. The body never accepts role ARN, product override, session policy, arbitrary tags or custom duration.

## Authorization order

1. Verify trusted API invocation context and extract the canonical authenticated NodeId path.
2. Reject disabled nodes, expired asset registry eligibility and blocked pools; enforce environment.
3. Validate grant signature, allowed algorithm, issuer, audience, bounded clock skew, lifetime and required fields.
4. Match grant NodeId to the path and trusted scheduler placement; verify definition digest, sandbox binding and active placement generation.
5. Resolve product/job/capability in the approved registry. Confirm target-account membership and entitlement freshness. Reject drift, stale snapshots and unknown definitions.
6. Verify the run is active using authoritative scheduler state or a short-lived signed heartbeat lease. Proposed maximum heartbeat age is 60 seconds; inability to establish freshness denies issuance/refresh.
7. Atomically consume the launch nonce and establish a run lease, or resume the identical authenticated idempotent operation. Reject nonce reuse with a different node, run or request.
8. Select the exact target role, broker-set tags and run-specific policy from approved templates. Validate generated policy size, allowed actions and resource scope before STS.
9. Write durable authorization intent, call STS, then record request ID, role, expiration, access-key identifier, scope hash and decision version. If durable recording fails, do not release credentials; record/reconcile any orphan STS issuance.
10. Deliver only target-session credentials and the bound lease handle. Return `Cache-Control: no-store`; disable request/response body logging and tracing of secrets.

## Replay and concurrency

Store nonce consumption and lease transitions with transactional conditional writes. The key includes issuer, `jti`, run and placement generation. Keep a used-nonce record until after the longest grant validity plus skew/replay margin; database TTL cleanup is not an authorization check.

A retry of the exact request may return a previously issued result from an encrypted short-lived store, or issue a new equivalent bounded session after reconciling the prior attempt. Never consume a nonce and strand a legitimate request without a defined retry state. STS and the database cannot share a transaction; account for the crash window explicitly. A duplicate equivalent session does not expand permissions but increases the number of credentials to audit.

Cache by node, run, placement generation, capability, target role, registry version and policy hash. Do not cache by product alone. A lease handle is bound to the authenticated node/run and cannot authorize another node. Renewals recheck run liveness, denylist and current authorization; a handle is not permanent approval.

## Broker session fields

| Field | Rule |
|---|---|
| `RoleArn` | Exact registry value |
| `RoleSessionName` | Broker-generated short run label, valid STS syntax |
| `SourceIdentity` | `run-<immutable-run-id>`; never from raw job input |
| Tags | Exactly ProductId, Environment, JobId, RunId and NodeId |
| `DurationSeconds` | 900 proposed; cap by remaining authorized run window |
| `Policy` | Mandatory approved run restriction for capabilities requiring it |
| Transitive tags | None in baseline; jobs have no subsequent AssumeRole permission |

STS's minimum AssumeRole duration is 900 seconds.[^sts] When less than that remains in an authorization window, deny issuance or explicitly authorize a new full window; do not claim to issue a shorter STS session. Cancellation during a window requires the containment procedure. The two-minute launch grant authorizes the initial exchange; its expiration is distinct from the approved run window and resulting credential lifetime.

Return generic denial classes to callers (`invalid_grant`, `node_blocked`, `scope_denied`, `lease_expired`, `temporarily_unavailable`), with detailed reasons only in restricted audit logs. Use per-node/run rate limits and bounded retries. Operational behavior is defined in [recovery](../operations/recovery.md).

[^api-iam]: [API Gateway IAM invocation](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html).
[^variables]: [IAM variables and tags](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html).
[^sts]: [STS AssumeRole duration constraints](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html).
