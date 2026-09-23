---
type: Taxonomy
title: On-premises server kinds and AWS identity patterns
description: Classify server responsibilities and select the appropriate machine, service or job identity boundary.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
sources:
  - id: decision
    resource: ../architecture/adr-001.md
  - id: identity
    resource: server-identity.md
---
# On-premises server kinds and AWS identity patterns

Classify each server by its operational responsibility before granting AWS access. A **server kind** describes what the machine does; it is not an IAM role, product entitlement or proof of workload identity. This is a proposed enterprise classification for the [architecture](../architecture/adr-001.md), not an AWS-defined taxonomy.[^decision]

Keep four identities distinct: the machine identified by NodeId, the platform service running on it, the product workload, and the individual job run or service instance. A Kubernetes node and a pod are different entities. A scheduler control-plane server and a batch execution agent have different privileges even when operated by the same team.

## Server-kind catalog

AWS access in this table is conditional on an approved use case. A server that only accepts network connections or provides an on-premises service does not need AWS credentials merely because it can reach a VPC.

| Kind identifier | Responsibility and examples | AWS identity and access pattern | Critical separation |
|---|---|---|---|
| `orchestrator-control` | Schedule work, maintain job definitions and assign runs; scheduler control plane | A protected scheduler adapter attests runs. Any AWS API access uses a dedicated control-plane service identity | Signing a job grant does not grant the orchestrator product data access; signing keys stay outside execution nodes |
| `batch-executor` | Execute scheduled product jobs; execution agents or batch workers | Unique node certificate, common runner role for the approved pool, broker-issued credentials per run | Isolate jobs from each other and from the node key; never assign the combined permissions of all products to the host |
| `identity-service` | Authenticate principals or supply identity evidence; directory, IdP, registration gateway | No AWS workload role by default. A required connector uses a dedicated, narrowly scoped service identity | Directory administration, certificate issuance and product-role assumption are separate capabilities; authentication does not imply authorization |
| `configuration-service` | Configure systems and distribute approved software; configuration servers or management controllers | Dedicated service identity only for approved artifacts or management APIs | Fleet administration is highly privileged; it must not provide a reusable fleet AWS key or product credentials through configuration |
| `application-service` | Host an API, application service or long-running daemon for one or more products | Identity per approved service/deployment; use a dedicated service role or a separately designed service-credential lease | A machine hosting several applications must not give them one combined AWS identity |
| `resource-server` | Serve files, databases, object storage or another on-premises application resource | No AWS role is needed for serving inbound requests. A process calling AWS uses its own service identity | TLS server identity and client authorization are separate from outbound IAM Roles Anywhere credentials |
| `integration-gateway` | Transfer messages/data or bridge protocols between systems | Dedicated connector identity scoped to approved source/destination resources; separate identities for different products | A relay handling multiple products must not let one request select another product's credentials |
| `ci-runner` | Execute build, test or deployment steps | Shared runners require trusted pipeline attestations and isolated per-build credentials, analogous to the batch broker pattern | Build input is executable code; deployment credentials require a distinct approved capability and must not be available to arbitrary builds |
| `k8s-control-plane` | Run the API server, controllers and scheduling components | No product AWS role by default; approved infrastructure controllers use dedicated service identities | Cluster administration is distinct from pod authorization; cluster trust does not grant every pod AWS access |
| `k8s-worker` | Run kubelet, container runtime and product pods | A node identity is for approved node operations only; pods obtain workload-specific credentials through the trusted adapter | Never share a worker certificate or node-wide credential endpoint with all pods |
| `k8s-identity-adapter` | Validate pod/run binding and obtain credentials for authorized workloads | Protected adapter certificate and broker admission; validate cluster, namespace, service account and pod UID | This is usually a service hosted in the cluster, not a separate physical server; keep its service account and keys inaccessible to tenants |
| `backup-recovery` | Perform backup, restore, replication or recovery automation | Dedicated backup and restore capabilities scoped to the relevant resources and environment | Broad read/decrypt and restore/write privileges can cross product boundaries; separate them and approve each explicitly |
| `observability-collector` | Forward logs, metrics, traces or security telemetry | Dedicated ingestion identity, preferably limited to the approved telemetry destinations | Collecting from many products does not justify reading their AWS application data or administering the logging destination |
| `administration-host` | Provide controlled interactive administration; bastion or jump host | Human AWS access uses the enterprise human-federation path; unattended agents have separate service identities | Do not use a machine certificate as a shared human administrator identity |
| `network-appliance` | Provide DNS, routing, proxy, firewall or load-balancing functions | No AWS credentials for packet forwarding alone; any cloud API integration uses a dedicated identity | Reachability and source IP are not product authorization; configuration privileges remain separate from data-plane traffic |
| `virtualization-host` | Run hypervisor or bare-metal management services hosting guest servers | Dedicated infrastructure integration identity only where required; guests have their own machine/workload identities | Host administration can compromise guests; high-assurance products need an appropriate host trust boundary |

## Choosing an access pattern

| Pattern | When to use it | Identity boundary |
|---|---|---|
| **No AWS caller identity** | The server only provides an on-premises resource, forwards traffic or performs local work | Record its NodeId and owner; do not issue an AWS authentication certificate without a caller use case |
| **Dedicated service identity** | A protected daemon performs a fixed, reviewed AWS integration | Separate key/certificate per service instance, exact initial role and explicit target permissions; no arbitrary user-selected product scope |
| **Per-run broker identity** | A shared executor runs code for different products | Node authentication plus trusted run attestation; issue only the run's target credentials |
| **Per-workload cluster identity** | Pods or controllers share Kubernetes infrastructure | Validate workload identity and execution binding; keep node, adapter and pod credentials separate |
| **Human federated identity** | A person performs interactive administration | Individual enterprise identity and approved human roles, independent of the host's certificate |

The implemented design target in these bundles is the **per-run broker** path and its Kubernetes adaptation. The other patterns classify the rest of the estate; they do not implicitly add permissions to the common runner role. A dedicated service integration needs its own reviewed trust/profile/policy configuration before onboarding. If a service broker is chosen for long-running daemons, define a trusted deployment attestation and liveness contract first; do not fabricate a scheduler run for a daemon.

The central AWS CA may issue certificates for multiple approved service classes, with separate issuance profiles/trust domains as appropriate. An on-premises identity server does not become a subordinate CA or obtain `IssueCertificate` solely because it is classified as `identity-service`.

## Classification fields

Extend the [machine record](server-identity.md) with a primary kind, additional responsibilities and the intended AWS access pattern.[^identity] The primary kind identifies the machine's operational owner; additional kinds make co-located responsibilities visible. Record hosted workloads separately from host-level permissions.

```yaml
node_id: n-0042
asset_id: asset-78c2
primary_kind: batch-executor
additional_kinds: []
owner_team: batch-platform
environment: prod
execution_pool: batch-prod-eu
tenancy: shared-products
aws_access_pattern: per-run-broker
identity_class: batch-prod
hosted_workload_refs: [scheduler-managed]
```

`identity_class` is an approved enrollment configuration reference, not a caller-provided role selector. The registration authority checks kind, ownership, environment and approved use case before mapping the machine to its certificate profile. Keep the kind in the asset registry by default; adding a custom certificate field does not automatically create an AWS authorization condition.

For clusters, record the cluster ID, separate NodeIds for control-plane and worker machines, and deployment/service-account identities for trusted adapters. Record pod UID and RunId on each workload binding. Do not use one cluster certificate as the identity of every worker and workload.

## Mixed responsibilities and reclassification

A server can have several responsibilities, but it must not automatically receive the union of their permissions. For example, a `resource-server` can host a backup agent: the backup process receives its own credentials, while the database service retains its existing identity. A `k8s-worker` can host an observability agent: that agent's telemetry permissions are separate from product pod permissions.

Co-location of an orchestrator, identity authority or fleet-management service with untrusted job execution weakens the trust boundary. Prefer separate hosts for these privileged services. If co-location is unavoidable, document the shared-host administrator exposure and apply the required isolation tier from the [threat model](../architecture/trust-model.md).

A change of kind or workload ownership requires an entitlement review. Disable obsolete admission, update scheduler placement and registry mappings, rotate/re-enroll when identity class or trust domain changes, and account for existing sessions. Reclassification is not a metadata-only mechanism for acquiring a more privileged role.

## Classification acceptance checks

- Every in-scope machine has a primary kind, owner, environment and explicit AWS-access requirement or a recorded no-access decision.
- Orchestrators, executors, identity services, Kubernetes nodes and workload adapters have distinct admission rules where their responsibilities differ.
- Resource servers serving only inbound traffic have no unnecessary AWS caller credentials.
- Co-located services and pods cannot read or obtain each other's credentials.
- Changing a kind in self-reported host facts does not change CA issuance eligibility, broker admission or AWS permissions.

[^decision]: [Governing architecture decision](../architecture/adr-001.md).
[^identity]: [Machine identity model](server-identity.md).
