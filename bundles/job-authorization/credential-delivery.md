---
type: Implementation Guide
title: Credential delivery and refresh
description: Deliver only run-scoped AWS credentials to isolated jobs and support long-running SDK clients.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
sources:
  - id: process
    resource: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html
---
# Credential delivery and refresh

There are two separate credential providers. The privileged node agent uses the AWS signing helper to obtain common runner credentials. The product job uses a custom local credential adapter to obtain only its target-session credentials. Never configure an ordinary job with the Roles Anywhere runner helper directly.

Illustrative per-job AWS config:

```ini
[profile job]
region = eu-central-1
credential_process = /usr/local/libexec/corp-job-credentials
```

The custom adapter discovers the protected socket provided by the trusted launcher; a user-supplied run ID alone is insufficient. An SDK-compatible process credential response includes version, access key, secret key, session token and expiration.[^process] The adapter emits credentials only to its requesting process and sends diagnostics to a redacted channel. Avoid shell wrappers that log stdout or arguments.

Example response shape, with no real credentials:

```json
{
  "Version": 1,
  "AccessKeyId": "EXAMPLE_TEMPORARY_ACCESS_KEY",
  "SecretAccessKey": "REDACTED",
  "SessionToken": "REDACTED",
  "Expiration": "2026-09-23T12:15:00Z"
}
```

Verify `credential_process` support and refresh behavior for each deployed language SDK and application. Some applications resolve credentials once or use a different provider chain. For those, supply a supported refreshing provider or restartable job stages. Static environment credentials do not refresh themselves.

The launcher clears inherited AWS credential environment variables and alternate shared credential files that could take precedence. It supplies a private config/profile and prevents fallback to unrelated host metadata or another workload's credential endpoint. Do not let a cached broad identity hide a broken job provider during testing.

## Long-running jobs

Proposed target-session duration is 15 minutes; request refresh before expiration with jitter and a safety margin, for example three minutes. The broker rechecks live run authorization, entitlement version and denylist on each refresh. A two-hour job normally receives multiple independently audited sessions under the same RunId.

Cache only within the requesting run and authorization version. A job that changes capability gets a separate authorized lease. On loss of authorization, stop refresh and close the local lease. Already-issued credentials require expiry or AWS deny controls to cease working.

## Files, processes and cleanup

Use memory/private tmpfs where practical. If disk storage is required, encrypt at rest, restrict ownership, prevent inclusion in backups and remove on completion. Keep directory ownership and parent-path protections as strict as the credential file. Disable cross-job process inspection, core dumps with secrets and broad debug logging.

Do not use a shared `~/.aws/credentials` for concurrent jobs. Do not bind a credential server to `0.0.0.0`, share a node-global localhost metadata endpoint with all jobs, or let jobs access the container runtime socket. Localhost alone is not isolation when processes share the same network namespace.

Cancellation triggers lease close, local process termination as appropriate and cache removal. Preserve only nonsecret audit metadata. Related: [Scheduler launch contract](scheduler-integration.md), [incident containment](../operations/incident-response.md).

[^process]: [AWS external credential process format](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html).
