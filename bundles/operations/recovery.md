---
type: Runbook
title: Availability and recovery
description: Dependency failure behavior, regional fencing and certificate continuity.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
---
# Availability and recovery

Deploy broker/enrollment components and private endpoints across availability zones. Keep certificate issuance off the normal per-job path: valid node certificates and cached runner credentials can outlive a brief enrollment outage. The broker remains on the issue/refresh path and requires tested availability.

| Failure | New jobs / refresh | Running jobs | Recovery |
|---|---|---|---|
| Enrollment outage | Continue only with valid certificate and authorized broker flow | Existing target sessions unaffected until expiry | Retry renewal with jitter; page before certificate budget exhausted |
| Roles Anywhere outage | Cached valid runner credentials may still invoke broker | Existing target credentials continue within expiry | Restore endpoint/service path; no static-key fallback |
| Broker/registry/replay outage | Deny issuance/refresh; queue work | Existing target credentials expire normally | Restore consistency and audit before reopening |
| Scheduler liveness unavailable | Deny after permitted heartbeat age | Previously issued credentials remain until expiry/deny | Restore authoritative state and reconcile leases |
| DX/DNS outage | No new private-path access | Requests requiring the path fail | Use pre-approved redundant DX/VPN routing and DNS recovery |
| Regional outage | Fence affected issuer/broker domain | Existing credentials may work for reachable services | Activate preprovisioned recovery configuration with fresh grants |
| Clock drift | Authentication may fail; quarantine bad clock | Existing signed requests may fail | Restore trusted time and revalidate |

## Regional strategy

Start with one primary region and a tested standby if enterprise recovery needs justify it. Roles Anywhere anchors/profiles are regional. Provision standby CA trust, profile mappings, endpoints, policies, issuer permissions and audit paths explicitly. AWS Private CA private keys are not a file to export and copy to another region; use a separately provisioned approved CA hierarchy for standby issuance.

Do not run two independent nonce stores with asynchronous replication and claim global one-time token consumption. Use a single active authorization region with a fenced epoch, or a proven strongly consistent global protocol. In the initial design, the scheduler signs grants for the active region/audience and epoch. Failover stops old grant issuance, fences the old broker's STS access, activates the new epoch, and issues new grants. Existing sessions from the old region still need containment or expiry.

A DNS change alone does not fence an old broker. Target-role trust or equivalent effective denies must prevent both regions from independently authorizing the same stale grants. If fencing cannot be proved, pause issuance. Prefer safety over duplicate or stale authorization.

## Recovery objectives to approve

Proposed pilot targets: recover broker service within 30 minutes; retain committed entitlement and audit records with no accepted loss; do not lose or replay accepted launch decisions. These are architecture targets, not established capabilities. Measure actual replication/backup behavior and choose the implementation accordingly. Existing 15-minute credentials may expire before a 30-minute recovery; job retry/queue behavior must tolerate that gap.

Back up public configuration, registry history, issuer records and audit evidence. Protect signing keys through the appropriate managed key service/HSM recovery process. Never restore stale replay state into active service without fencing old grants and issuing a new epoch.

## CA rollover

Provision and approve new CA/anchor; add new anchor ARN to intended role trust; distribute public chains; issue canary leaves; validate mappings, CRLs and helper behavior; renew the fleet; disable old issuance; wait for old certificates/sessions and documented overlap; remove old anchor trust. Keep old and new asset registry associations during the overlap so incident response can cover both.

Test this sequence with one noncritical pool before fleet use. Related: [enrollment](../identity-pki/enrollment-renewal.md), [incident response](incident-response.md).
