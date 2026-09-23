---
type: Runbook
title: Node enrollment and certificate renewal
description: Automated bootstrap, local key generation, renewal, rotation and retirement.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
---
# Node enrollment and certificate renewal

## First enrollment

1. Asset registry creates the NodeId, environment, pool, owner and expected hardware/VM evidence. The platform pipeline installs the approved agent and trust bundle.
2. Establish bootstrap trust through an already-approved management-agent identity or a one-use enrollment token delivered by the provisioning system. Bind tokens to NodeId and an expected CSR/public-key fingerprint where available; short expiration and atomic one-time consumption are mandatory. Never put a reusable fleet secret in an image.
3. Generate the identity key on the node. Prefer a supported hardware-backed provider; otherwise use an OS-protected key owned by the dedicated agent account. The private key is not sent to the configuration-management platform or the registration service.
4. Submit a CSR over TLS. The registration service checks bootstrap proof, asset registry eligibility, identity uniqueness, public-key strength and CSR signature. It refuses self-selected environment, pool or subject changes.
5. The service issues a leaf using the approved [CA profile](ca-design.md), records serial/key fingerprint/NodeId, and returns only certificate and public chain.
6. The agent verifies key match, chain, identity, validity and permissions, writes a new versioned directory, then atomically switches its active reference. It probes Roles Anywhere and the node's broker path before marking enrollment healthy.

The first certificate cannot require credentials that can only be obtained using that same certificate. Bootstrap uses an independent provisioning trust path; subsequent issuance can authenticate with the current identity plus fresh asset registry authorization.

## Renewal contract

Proposed schedule: 24-hour validity; begin renewal at 12 hours plus bounded jitter, retry with exponential backoff, alert when six hours remain, page at two hours, and stop new AWS credential requests at certificate expiry. Tune for outage tolerance and CA mode. Renewal is a resident service/timer responsibility, not a dependency on the next configuration-management cycle.

Use a fresh key on renewal where the platform supports reliable rollover. Keep old and new pairs only for a bounded overlap. A signer must load a consistent key/certificate pair; update a versioned directory reference rather than overwriting two files independently. Avoid retaining old private keys in backups, package caches or telemetry.

Renewal must recheck asset registry status, environment and key possession. Possession of a still-valid certificate alone is insufficient after quarantine. The service denies active renewal for retired nodes even before the CA revocation pipeline completes.

## Failure handling

| Failure | Behavior |
|---|---|
| Enrollment service unavailable | Retry; retain current valid pair; alert before the renewal budget is exhausted |
| New certificate identity/key mismatch | Reject pair, preserve valid old pair, raise security alert |
| New pair cannot authenticate | Diagnose profile/anchor/clock; do not silently accept weaker validation |
| Current certificate expired | Quarantine new launches; use provisioning recovery path for re-enrollment |
| Key suspected copied | Deny node at broker, revoke serials, rebuild and enroll fresh key |
| CA rotation | Deploy new anchor and trust policy first, canary new leaves, overlap, then retire old hierarchy |

Decommissioning disables scheduler placement, closes leases, denies the NodeId, revokes outstanding certificates and destroys local keys. Reconcile asset registry, issuer records and scheduler nodes daily to find orphaned identities.

Related: [Configuration automation](configuration-automation.md), [incident response](../operations/incident-response.md), [recovery](../operations/recovery.md).
