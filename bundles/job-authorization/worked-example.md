---
type: Example
title: Two products on a shared batch execution pool
description: End-to-end example showing node reuse, distinct job permissions and denied substitutions.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
---
# Two products on a shared batch execution pool

The pool contains `n-0042` and `n-0043`. Each has a unique key/certificate; both authenticate as `OnPremRunnerProd`. They can run any product assigned to this pool by the trusted scheduler. Their node certificates have no product claim.

| Run | Product / accountable team | Job class | Node | Target account and role |
|---|---|---|---|---|
| `r-01abc` | product-a / team-a | job-a | n-0042 | 222222222222 / product-a job-a |
| `r-01def` | product-b / team-b | job-b | n-0042 | 333333333333 / product-b job-b |
| `r-01ghi` | product-a / team-a | job-a | n-0043 | 222222222222 / product-a job-a |

For `r-01abc`, the broker validates node path `n-0042`, signed run assignment and the approved definition. It sets source identity `run-r-01abc`, tags the session with the five controlled identity fields, and applies the [job-a run policy](policy-examples.md). The job reads only its staged input and writes only its output prefix.

The product-b job receives a separate socket, lease, target role and cache. It cannot use the product-a role even though both jobs execute on the same host. The job on `n-0043` shares the product-a job-class baseline, but its run policy references `r-01ghi`, not `r-01abc`.

## Expected decisions

| Attempt | Result | Enforcement |
|---|---|---|
| Job A reads its approved staged input | Allow | Target role and run policy |
| Job A reads Product B resources | Deny | No target permission and strict session deny |
| Job A reads input for another run | Deny | Run policy resource confinement |
| Job B changes `product_id` in grant | Deny | Invalid signature |
| Job B requests the Product A role ARN in the body | Deny | Unsupported request field / server-side capability resolution |
| Node n-0043 uses n-0042 API path | Deny | Runner IAM explicit path deny |
| Node n-0043 sends n-0042 grant on own path | Deny | Broker NodeId mismatch |
| Either job calls helper with node key | Deny | OS key/signer isolation |
| Runner directly assumes job-a role | Deny | Runner deny and target trust |
| Completed job asks for refreshed credentials | Deny | Closed run lease |
| Canceled job uses an unexpired issued credential | May still succeed | Apply incident deny when immediate containment is required |

## Failure example

Suppose both jobs run under one Unix UID and can read each other's socket or credential cache. The IAM policies can be correct while isolation fails: product-b can use a stolen product-a session. The remedy is execution isolation or dedicated pools, not an additional session-name convention.

This example is a test fixture specification. It is not a record of an executed AWS test. Use it in the [acceptance matrix](../operations/acceptance-tests.md).
