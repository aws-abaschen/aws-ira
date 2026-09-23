---
type: Reference
title: Editable Mermaid diagrams
description: Embedded Mermaid architecture diagrams with AWS icons and renderer setup.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
sources:
  - id: architecture
    resource: https://mermaid.js.org/syntax/architecture.html
  - id: icons
    resource: https://mermaid.js.org/config/icons.html
---
# Editable Mermaid diagrams

All diagram sources live in fenced `mermaid` blocks inside the documents. Edit and commit the Markdown directly; there are no standalone diagram files or synchronization step.

| Diagram | Mermaid type | Owning document |
|---|---|---|
| Logical architecture | `architecture-beta` | [ADR](adr-001.md#logical-architecture) |
| Credential exchange | `sequenceDiagram` | [ADR](adr-001.md#credential-flow) |
| Certificate lifecycle | `stateDiagram-v2` | [ADR](adr-001.md#certificate-lifecycle) |
| Private network | `architecture-beta` | [Accounts and network](accounts-network.md#network-topology) |
| Kubernetes topology | `architecture-beta` | [Kubernetes integration](../identity-pki/kubernetes.md#selected-broker-integration) |

Architecture diagrams use groups for account/cluster boundaries, services for components, and directed edges for relationships. Mermaid introduced this diagram type in version 11.1.0. Detailed message semantics remain in the sequence diagram and surrounding text.[^architecture]

## AWS icons

The architecture blocks use the `logos` Iconify pack, pinned for validation to `@iconify-json/logos@1.2.14`. AWS components use icons such as `logos:aws-iam`, `logos:aws-api-gateway`, `logos:aws-lambda`, `logos:aws-s3`, `logos:aws-vpc` and `logos:aws-route53`. Kubernetes uses its product icon. Generic on-premises services use Mermaid's built-in `server`, `database` and `internet` symbols.

Where this pack lacks a dedicated service icon, use a related service-family symbol with an explicit label: `aws-iam` represents IAM roles, Roles Anywhere and STS; `aws-certificate-manager` supplies the certificate symbol for AWS Private CA. The label identifies the actual component. The CA remains AWS Private CA, and the on-premises cluster remains self-managed Kubernetes. The S3 symbols illustrate the worked-example resources rather than restricting all product capabilities to S3.

Mermaid requires the host renderer to register custom icon packs; a diagram fence does not register JavaScript by itself.[^icons] Configure the Markdown site's Mermaid instance before rendering:

```javascript
import mermaid from 'mermaid';
import { icons } from '@iconify-json/logos';

mermaid.registerIconPacks([{ name: 'logos', icons }]);
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
// The Markdown renderer now passes its embedded Mermaid blocks to this instance.
```

Use a viewer that supports `architecture-beta` and registers the `logos` pack. Support depends on the Markdown host; Git committability does not imply that every hosted preview loads custom AWS icons. For a managed documentation site, bundle the pinned pack locally so viewing does not require a runtime icon CDN.

## Validation

Install the local validation dependencies:

```powershell
python -m pip install -r scripts/requirements.txt
npm ci --ignore-scripts
```

Run from the repository root:

```powershell
python scripts/validate_docs.py
npm run validate:diagrams
```

Use Python 3.13+ and Node.js 24.15+ (24.x). The Python check validates document structure, examples, local links and heading anchors. The JavaScript check reads the fences directly, registers the icon pack, checks referenced icon names and parses every embedded diagram. There is no fixed diagram count. These checks do not certify layout in every viewer. Dependencies use the committed npm lockfile; `node_modules` is ignored by Git.

The [GitHub Actions workflow](../../.github/workflows/validate-docs.yml) runs these checks and validator regression tests on pushes, pull requests and manual dispatch. It needs no AWS credentials and has read-only repository permissions. Local regression tests use `python -m unittest discover -s scripts -p 'test_*.py'`.

[^architecture]: [Mermaid architecture syntax](https://mermaid.js.org/syntax/architecture.html).
[^icons]: [Mermaid icon-pack registration](https://mermaid.js.org/config/icons.html).
