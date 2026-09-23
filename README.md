# Enterprise AWS workload identity

Start with the [single architecture decision record](bundles/architecture/adr-001.md), then use the four linked Open Knowledge Format bundles below.

| Bundle | Contents |
|---|---|
| [Architecture](bundles/architecture/index.md) | Decision, diagrams, requirements, trust boundaries, account topology and network design |
| [Identity and PKI](bundles/identity-pki/index.md) | Server identity, centralized CA, enrollment, Configuration automation and Kubernetes |
| [Job authorization](bundles/job-authorization/index.md) | Scheduler integration, broker contract, policy examples and credential delivery |
| [Operations](bundles/operations/index.md) | Ownership, onboarding, incident response, recovery, capacity and acceptance tests |

The proposed design uses unique server certificates and a common runner role. A separate credential broker validates each scheduled run and assumes its approved product/job role. Jobs receive only the resulting credentials. Product identity is never inferred from a caller-selected session name.

These are reviewable architecture documents, not deployed infrastructure. Account IDs, regions, hostnames, lifetimes and service objectives are illustrative. Custom enrollment, scheduler attestation and broker components are explicitly identified. No cloud deployment or live AWS test has been performed.

The bundles follow the user-supplied [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). That repository now points to the [canonical specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Distribute the complete `bundles` directory to preserve links between bundles. Each bundle has its own root index, concept metadata and update log. Documents use standard relative links for repository browsing; diagrams use Mermaid.

All five diagrams are embedded in Markdown. The three topology diagrams use Mermaid `architecture-beta` with AWS icons; the ADR also includes a sequence diagram and a state diagram. The [diagram guide](bundles/architecture/diagrams.md) explains the required icon-pack registration and validation commands.

The [documentation workflow](.github/workflows/validate-docs.yml) runs on pushes, pull requests and manual dispatch. It tests the validator, checks the chosen OKF conventions, local links and heading anchors, JSON/YAML examples, embedded Mermaid syntax and icon references. It does not certify AWS policy behavior or production readiness.

To run the same checks locally, use Python 3.13+ and Node.js 24.15+ (24.x): install with `python -m pip install -r scripts/requirements.txt` and `npm ci --ignore-scripts`, then run `python -m unittest discover -s scripts -p 'test_*.py'`, `python scripts/validate_docs.py` and `npm run validate:diagrams`. npm dependencies are pinned in the committed lockfile.
