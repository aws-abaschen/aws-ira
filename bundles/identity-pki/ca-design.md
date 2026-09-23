---
type: Architecture
title: Central CA and issuance authority
description: Hierarchy, issuer restrictions and revocation plumbing for a centralized AWS Private CA.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:01:25+02:00"}
sources:
  - id: pca
    resource: https://aws.amazon.com/blogs/security/set-up-aws-private-certificate-authority-to-issue-certificates-for-use-with-iam-roles-anywhere/
  - id: crl
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html
---
# Central CA and issuance authority

Use a dedicated AWS Private CA issuing hierarchy in the identity account. An enterprise root may sign the subordinate, or a dedicated AWS Private CA root may establish the hierarchy. The enterprise PKI authority chooses this during rollout. Keep root signing authority outside everyday enrollment operations.

Use separate issuing CAs for production runners, nonproduction runners and privileged cluster issuance controllers. Anchor the intended subordinate rather than a broad enterprise root that would admit unrelated certificates. Keep general TLS issuance separate from AWS workload authentication. A centralized CA does not require a single issuer for every trust domain.

AWS provides a reference implementation for certificate issuance used with Roles Anywhere; this design adds asset registry checks, local key generation and job authorization rather than treating the sample as a complete enterprise service.[^pca]

## Separation of duties

| Identity | May do | Must not do |
|---|---|---|
| PKI administrator | Establish hierarchy, approve profiles, rotate CA | Approve product entitlements alone |
| Registration service role | Issue/retrieve leaf certificates from named CA and approved template | Issue subordinate CAs, modify target roles or broker registry |
| Revocation updater | Retrieve authoritative CRL and import/update it for named anchors | Issue certificates or change job entitlements |
| Broker execution role | Assume exact product job roles | Issue certificates or edit its own allowlist |
| Node runner role | Invoke node-bound broker method | Call Private CA issuance or target STS roles |
| Entitlement publisher | Publish reviewed registry snapshots and target policy changes | Sign scheduler runtime attestations |

Restrict `acm-pca:IssueCertificate` by exact CA ARN and approved `acm-pca:TemplateArn`; grant only necessary retrieval operations. Template restrictions alone do not validate who may request a CN, SAN or product claim. The registration service constructs or validates every identity-bearing field against asset registry and rejects unexpected extensions and CA capabilities.

CA mode and certificate lifetimes are procurement/deployment decisions. Compare general-purpose and short-lived CA modes against the selected lifetimes, regions, revocation requirements and current pricing. Do not assume changing mode later is operationally free.

## Revocation design

Configure CA revocation publication and an automated importer. Roles Anywhere checks imported CRLs; it does not fetch CDP or OCSP URLs to discover revocation.[^crl] On publication, the importer validates issuer/signature and CRL freshness, converts representation if necessary, then updates the enabled CRL associated with every active anchor/region. Poll as a reconciliation path in addition to event triggers.

Track CA generation lag, import lag, CRL `thisUpdate`/`nextUpdate`, import result and oldest unprocessed revocation. Proposed freshness target: five minutes after a new authoritative CRL becomes available; measure CA publication separately. Never claim a five-minute end-to-end guarantee without testing it.

Use the broker's node denylist for prompt containment while revocation propagates. Certificate revocation and anchor disabling stop future Roles Anywhere sessions; they do not invalidate all existing credentials. See [incident response](../operations/incident-response.md).

[^pca]: [AWS certificate issuance reference](https://aws.amazon.com/blogs/security/set-up-aws-private-certificate-authority-to-issue-certificates-for-use-with-iam-roles-anywhere/).
[^crl]: [Roles Anywhere revocation behavior](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html).
