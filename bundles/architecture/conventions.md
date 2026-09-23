---
type: Reference
title: Documentation conventions
description: Format, provenance and review rules for the architecture bundle set.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-23T22:59:48+02:00"}
sources:
  - id: okf
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
  - id: canonical
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
---
# Documentation conventions

This set uses OKF v0.2: concept documents have YAML frontmatter and a nonempty `type`; root indexes declare `okf_version`; other indexes and update logs have no concept metadata. Sources use stable identifiers and corresponding footnotes. Relative Markdown links connect concepts. These choices follow the supplied specification.[^okf]

The original repository redirects maintainers to the canonical OKF repository. Both inspected specifications identify version 0.2.[^canonical]

All concepts remain `draft`. This means the deliverable is complete for architecture review, while the enterprise design has not been approved or tested in AWS. No `verified` entry is asserted. Document timestamps record authorship, not source publication dates. Proposed owners are organizational functions, not assertions about actual staff assignments.

“Required” and “must” express this proposed architecture's controls. “AWS behavior” identifies a sourced platform constraint. Other implementation choices, service objectives and parameter values are design proposals. Examples are illustrative and must be rendered with enterprise identifiers before deployment.

Maintain a single ADR. Update it when decisions change; keep operational detail in linked concepts. Review sources and implementation assumptions before adoption and after relevant AWS, scheduler or PKI changes. Publish the whole bundle set together; cross-bundle links make an isolated directory incomplete as a deployment guide.

[^okf]: [User-supplied OKF specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).
[^canonical]: [Canonical OKF specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).
