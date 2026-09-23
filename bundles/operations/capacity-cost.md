---
type: Planning Model
title: Capacity and cost planning
description: Workload-driven sizing formulas and cost drivers without assumed enterprise volumes or prices.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-23T22:59:48+02:00"}
sources:
  - id: quotas
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/quotas.html
---
# Capacity and cost planning

Use measured node count, concurrency and launch patterns. Check current regional Roles Anywhere quotas and request adjustments before production; do not assume sample limits or adjustable status are universal.[^quotas] Also review STS, Private CA, API Gateway, Lambda concurrency, database transactions and IAM role/policy quotas.

Let `N` be enrolled nodes, `C` concurrent active jobs, `Tr` runner refresh interval in seconds, `Tj` job refresh interval, and `Tc` certificate renewal interval. Approximate steady state:

```text
Roles Anywhere CreateSession rate  ~= N / Tr
Broker/STS refresh rate            ~= C / Tj
Certificate issuance rate          ~= N / Tc
Daily certificate issuance        ~= N * 86400 / Tc
```

Add new launches, retries, failover and canaries. A lower-bound daily launch rate is insufficient for a batch scheduler that starts thousands of jobs at the same minute. Model peak launch rate separately and test at least twice the agreed peak, with controlled throttling and jitter.

Illustrative scenario only: `N=1,000`, `C=10,000`, refresh every 720 seconds and renew certificates every 12 hours. Steady runner refresh is about 1.39 requests/s; job refresh about 13.89 requests/s; certificate issuance about 2,000/day. This excludes launches, retries and cluster identities and is not a statement about the user's estate.

## Cost drivers

| Driver | Planning input |
|---|---|
| Private CA | Number of CAs, mode, regions and certificates issued |
| Private endpoints | Endpoint count, AZ count, service availability and traffic |
| Broker | Request count, execution time, reserved capacity and data-store operations |
| Audit | Management/data-event volume, retention, storage and analysis |
| Network | Existing DX capacity, redundant paths and inter-region transfer |
| Operations | Custom adapter/agent/broker ownership, testing and support |
| Isolation | Dedicated VMs/pools/clusters for high-assurance products |

Obtain current regional pricing during procurement. Optimize by caching runner credentials inside the privileged agent, separating certificate renewal from job launch, avoiding unnecessary per-run IAM roles, and enabling data events at the required scope. Do not reduce cost by sharing private keys or broadening target roles.

Monitor policy size and `PackedPolicySize`; generate compact policies with bounded resource lists. Use approved prefix-based staging where enumerating many object ARNs would exceed limits. The entitlement author must prove that a prefix does not include unrelated data.

[^quotas]: [Roles Anywhere quotas](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/quotas.html).
