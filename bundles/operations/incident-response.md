---
type: Runbook
title: Credential and identity incident response
description: Contain compromised nodes, runs, issuers and broker identities without confusing future issuance with active credentials.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-23T22:59:48+02:00"}
sources:
  - id: deny
    resource: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_disable-perms.html
---
# Credential and identity incident response

Certificate revocation, disabling a profile and closing a broker lease address future issuance. Already-issued target credentials need expiry or effective AWS authorization denies. IAM permission changes can affect existing sessions, with propagation delay; consider resource policies as well.[^deny]

## Compromised node

1. Security operations records NodeId, suspected time, certificate serials and active runs. Stop scheduler placement and isolate the node through the established incident process.
2. Deny the NodeId in the broker and close its leases. This blocks refresh even while existing runner credentials remain valid.
3. Identify all issued target sessions from the ledger. Deploy a temporary deny for `aws:PrincipalTag/NodeId` on affected target roles/resources where supported, or deny each known run source identity. Verify actual resource requests fail.
4. Revoke relevant leaf certificates, publish/import the CRL to every active anchor, and verify fresh Roles Anywhere requests fail. Monitor propagation, rather than treating the CA revoke response as completion.
5. Preserve evidence; rebuild the host, create a fresh key and re-enroll through approved provisioning. Remove containment only after verifying the new state and all old sessions have expired or remain denied.

## Compromised or canceled run

Stop the run, close its lease and block refresh. For immediate AWS containment, attach an explicit deny scoped to the run's source identity on affected roles, supplemented by resource policy controls when necessary. The following is an illustrative emergency identity policy, not a command to execute:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ContainRun",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {"StringEquals": {"aws:SourceIdentity": "run-r-01abc"}}
  }]
}
```

Keep the deny until all issued credentials and any authorized downstream activity are accounted for. STS credential expiration does not necessarily cancel work already started in another service; investigate queued messages, launched tasks, copied secrets and generated artifacts separately.

## CA or issuer compromise

Disable affected trust anchors/profiles and broker admission for the trust domain. Revoke affected leaves or retire the hierarchy as required. A stolen issuer role may have created unknown certificates, so enumerating known leaf serials alone is insufficient. Deny active target sessions for the affected domain and re-establish trust with a clean CA/registration authority. Validate every regional anchor and backup configuration before reopening.

## Broker compromise

Stop its ability to assume roles by removing or denying target trust and its execution-role permissions. Stopping the broker alone leaves its already-issued target sessions alive. Apply broad target-role session containment where necessary, then use ledger and CloudTrail to scope impact. Rebuild the broker, rotate signing/administrative credentials as applicable, and independently review registry and target policy changes.

## Completion evidence

Record measured times for admission block, refresh block, certificate rejection and active-session data denial. Capture at least one real denied service operation; a denied `AssumeRole` call proves only that a new session cannot be created. Document business impact and remove emergency denies through controlled review.

See [audit](audit-monitoring.md) and [recovery](recovery.md).

[^deny]: [Disabling permissions for temporary credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_disable-perms.html).
