"""Check OKF conventions, local links, example syntax and embedded diagrams.

Install scripts/requirements.txt first. This does not test IAM or deployments.
"""
from pathlib import Path
import json
import os
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
import yaml


def local_target(path, target):
    """Resolve normal Markdown and OKF bundle-relative paths."""
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    if not parsed.path:
        return path
    if parsed.path.startswith('/') and path.is_relative_to(ROOT / 'bundles'):
        bundle = ROOT / 'bundles' / path.relative_to(ROOT / 'bundles').parts[0]
        return (bundle / unquote(parsed.path).lstrip('/')).resolve()
    return (path.parent / unquote(parsed.path)).resolve()


def heading_ids(text):
    """GitHub-style IDs for the ordinary ATX headings used in this repository."""
    text = re.sub(r'```[^\n]*\n.*?\n```', '', text, flags=re.S)
    result, seen = set(), {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        occurrence = seen.get(slug, 0)
        seen[slug] = occurrence + 1
        result.add(f'{slug}-{occurrence}' if occurrence else slug)
    return result


def main():
    errors = []
    counts = dict(bundles=0, concepts=0, links=0, json_examples=0, yaml_examples=0, diagrams=0)
    for bundle in sorted((ROOT / "bundles").iterdir()):
        if not bundle.is_dir():
            continue
        counts["bundles"] += 1
        index = bundle / "index.md"
        index_text = index.read_text(encoding="utf-8") if index.exists() else ""
        try:
            match = re.match(r'\A---\n(.*?)\n---\n', index_text, re.S)
            metadata = yaml.safe_load(match[1]) if match else None
            if not isinstance(metadata, dict) or set(metadata) != {'okf_version'} or str(metadata['okf_version']) != '0.2':
                raise ValueError('root index must declare only okf_version 0.2')
        except (yaml.YAMLError, ValueError) as exc:
            errors.append(f"{index}: {exc}")
        for path in sorted(bundle.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            label = str(path.relative_to(ROOT))
            if path.name in {"index.md", "log.md"}:
                if path.name == "log.md" and (text.startswith("---") or not re.search(r"^## \d{4}-\d{2}-\d{2}$", text, re.M)):
                    errors.append(f"{label}: invalid log structure")
                if path.name == "index.md" and path != index and text.startswith("---"):
                    errors.append(f"{label}: nested index frontmatter")
                continue
            counts["concepts"] += 1
            match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
            if not match:
                errors.append(f"{label}: missing frontmatter")
                continue
            try:
                meta = yaml.safe_load(match[1])
                if not isinstance(meta, dict) or not isinstance(meta.get("type"), str) or not meta["type"].strip():
                    raise ValueError("missing nonempty type")
                if meta.get("status", "stable") not in {"draft", "stable", "deprecated"}:
                    raise ValueError("invalid lifecycle status")
                source_ids = {s.get("id") for s in meta.get("sources", [])}
                for source in meta.get("sources", []):
                    if not source.get("resource"):
                        raise ValueError("source missing resource")
                    resource = source['resource']
                    if isinstance(resource, str) and resource.endswith('.md'):
                        target = local_target(path, resource)
                        if target is not None and not target.exists():
                            raise ValueError(f'broken local source {resource}')
                body = text[match.end():]
                for note in set(re.findall(r"\[\^([^\]]+)\]", body)):
                    if note not in source_ids or not re.search(rf"^\[\^{re.escape(note)}\]:", body, re.M):
                        raise ValueError(f"unresolved source footnote {note}")
            except (yaml.YAMLError, ValueError, TypeError, AttributeError) as exc:
                errors.append(f"{label}: {exc}")
            directory_index = path.parent / 'index.md'
            listing = directory_index.read_text(encoding='utf-8') if directory_index.exists() else ''
            listed = {local_target(directory_index, target) for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', listing)}
            if path.resolve() not in listed:
                errors.append(f"{label}: not in bundle index")
    for path in list((ROOT / "bundles").rglob("*.md")) + [ROOT / "README.md"]:
        text = path.read_text(encoding="utf-8")
        label = str(path.relative_to(ROOT))
        for language, block in re.findall(r"```([^\n]*)\n(.*?)\n```", text, re.S):
            try:
                if language == "mermaid":
                    counts["diagrams"] += 1
                    if not block.strip():
                        errors.append(f"{label}: empty diagram")
                elif language == "json":
                    json.loads(block)
                    counts["json_examples"] += 1
                elif language == "yaml":
                    yaml.safe_load(block)
                    counts["yaml_examples"] += 1
            except (json.JSONDecodeError, yaml.YAMLError) as exc:
                errors.append(f"{label}: invalid {language}: {exc}")
        prose = re.sub(r"```[^\n]*\n.*?\n```", "", text, flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose):
            counts["links"] += 1
            parsed = urlsplit(target)
            resolved = local_target(path, target)
            if resolved is None:
                continue
            if not resolved.exists():
                errors.append(f"{label}: broken link {target}")
            elif parsed.fragment and resolved.suffix == '.md':
                if unquote(parsed.fragment) not in heading_ids(resolved.read_text(encoding='utf-8')):
                    errors.append(f"{label}: missing heading in {target}")
        if text.count("```") % 2:
            errors.append(f"{label}: unbalanced fences")
    for directory, folders, files in os.walk(ROOT):
        folders[:] = [name for name in folders if name not in {'.git', '.tools', 'node_modules', '__pycache__', '.venv'}]
        for filename in files:
            if filename.endswith('.mmd'):
                path = Path(directory) / filename
                errors.append(f"{path.relative_to(ROOT)}: diagrams must be embedded in Markdown")
    print(json.dumps({"checks": counts, "errors": errors}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
