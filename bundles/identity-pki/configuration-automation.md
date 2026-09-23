---
type: Implementation Guide
title: Automated enrollment and credential agents
description: Configuration-management responsibilities and the custom agent interface for automated certificates.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
sources:
  - id: helper
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html
---
# Automated enrollment and credential agents

The configuration-management platform installs pinned, verified packages, manages public configuration, enforces file/service permissions and reports health. A custom `corp-workload-agent` performs enrollment, renewal and per-job credential delivery. This name describes proposed software; it is not an existing platform component or AWS feature.

The management platform may supply approved machine identity evidence for enrollment. Its initial registration and approval process must establish trust: self-reported facts or an automatically signed arbitrary CSR are not proof of NodeId. If a management certificate is used for bootstrap, keep it separate from the AWS workload certificate and validate it against the approved registration policy.

## Desired state

| Resource | Desired state |
|---|---|
| AWS signing helper | Enterprise-pinned version, checksum/signature verification, supported architecture |
| Workload agent | Dedicated service account, startup enabled, restart and rate limits |
| Configuration | Root/platform-writable only; NodeId, endpoints, public CA roots and role/profile/anchor ARNs |
| Identity key | Locally generated; agent-readable only; never distributed through configuration payloads, central variable stores or reports |
| Certificate store | Versioned pairs, restricted owner, atomic active reference |
| Job sockets/cache | Separate per-run directories; no shared writable credential file |
| Monitoring | Expiry, last renewal, signer health, broker latency and lease failures |

Illustrative Linux layout:

```text
/etc/corp-workload-agent/config.yaml       # public identifiers, root-owned
/var/lib/corp-workload-agent/identity/     # protected key/certificate versions
/run/corp-workload-agent/jobs/<run-id>/    # private socket/cache for one sandbox
/usr/local/libexec/corp-job-credentials    # custom SDK credential_process adapter
```

Example configuration contract, not a runnable product configuration:

```yaml
node_id: n-0042
environment: prod
pool: batch-prod-eu
enrollment_url: https://enroll.corp.example
broker_url: https://broker.corp.example/prod
certificate_validity: 24h
renew_after: 12h
job_credentials_ttl: 15m
key_provider: os-protected
```

Use the AWS signing helper only inside the privileged agent to obtain runner credentials. Its `credential-process` mode outputs AWS-compatible temporary credentials; supported key-provider integrations must be checked against the pinned release and OS.[^helper] Do not expose its listener/serve mode to all jobs or the node network.

The job-facing `credential_process` invokes the custom adapter, which authenticates to a private local socket. On Windows, use a service SID, protected key storage and ACL-controlled named pipes; do not translate Linux mode bits into an assumption of equivalent isolation. Validate supported scheduler execution identities on each OS.

## Deployment order and rollback

Deploy trust roots/config, pinned helper, agent, enrollment, signer probe, private broker probe, then enable scheduler placement. The configuration-management platform should converge configuration without repeatedly issuing certificates. Canary new helper/agent releases on a small pool and verify renewal and long-running SDK refresh.

Rollback to a known agent version while retaining the currently valid identity pair. Never restore a revoked key from configuration backup. Fleet-management privileges remain a high-value trust boundary: a compromised management server can modify the credential agent or exfiltrate software keys.

A configuration-management platform, enterprise device-management system or dedicated PKI agent can perform this automation role. Keep the enrollment and broker protocols independent of the chosen tool so that all OS fleets share the same authorization rules.

[^helper]: [AWS Roles Anywhere credential helper](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html).
