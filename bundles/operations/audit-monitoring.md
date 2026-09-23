---
type: Observability Design
title: Audit correlation and monitoring
description: Evidence linking server identity, scheduler ownership and resource access.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
sources:
  - id: trail
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/logging-using-cloudtrail.html
---
# Audit correlation and monitoring

Use an organization trail and centralized, access-controlled audit storage. Roles Anywhere emits CloudTrail records including CreateSession; retain these alongside STS and policy/CA administration events.[^trail] Enable relevant resource data events, such as S3 object access, explicitly; management-event history alone is not evidence of every data operation.

## Required evidence chain

| Record | Correlation fields |
|---|---|
| Asset registry | NodeId, asset, pool, environment, owner, lifecycle state |
| Enrollment | NodeId, approved bootstrap identity, issuer, certificate serial, key fingerprint, validity |
| Scheduler | RunId, definition digest, product, team snapshot, node placement/generation, start/end/cancel |
| Broker request | API request ID, authenticated caller, canonical NodeId path, grant issuer/jti, capability |
| Broker decision | Allow/deny reason, registry version, policy hash, role ARN, RunId, audit intent ID |
| STS issuance | STS request ID, target account/role, source identity, controlled tags, access-key ID, expiration |
| Resource access | Event ID, API/action, resource, account, session issuer, access-key ID, source identity where present |

Access-key IDs are correlation identifiers; secret access keys, session tokens, private keys and raw launch grants are never logged. Treat identity metadata as restricted operational data. Do not assume all downstream CloudTrail events repeat every session tag. Join resource events to STS/broker records using access-key ID and source identity, then to scheduler and asset registry records.

The node-to-broker and broker-to-product sessions are distinct. A product resource event will identify the broker-issued job session, not automatically inherit the node certificate's source identity. The durable broker ledger provides that link. Prefer authenticated API context over NodeId values copied from request bodies.

## Alerts and proposed objectives

| Signal | Proposed response |
|---|---|
| Certificate remaining validity under six hours | Warning to platform; page under two hours |
| Revocation published but not imported within five minutes | Page identity platform; inspect CA publication lag separately |
| Invalid grant signatures, wrong-node requests, replay bursts | Security alert with rate and node context |
| Broker cannot durably audit or obtain fresh authorization | Deny issuance and page service owner |
| New trust anchor/profile, role trust or issuer permission drift | Security review; block unapproved deployment |
| Credentials issued without required tags/policy hash | Critical authorization invariant failure |
| Unknown product/account/definition version | Deny and notify deployment owner |
| Rising denial or throttling rate around batch peak | Capacity investigation; no scope broadening |

Suggested service objective: 99.9% successful authorized credential requests monthly, excluding legitimate denials but including dependency failures. Measure end-to-end latency separately; begin with a p95 target of two seconds and revise using pilot evidence. These are proposed operational targets, not AWS service guarantees.

Store audit evidence under retention/immutability rules chosen by security and compliance. Test the forensic question: “Which node, product, team, definition and authorization version caused this object write?” A log pipeline is accepted only when that reconstruction works for both successful and rejected requests.

[^trail]: [Roles Anywhere CloudTrail logging](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/logging-using-cloudtrail.html).
