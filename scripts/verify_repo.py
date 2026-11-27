"""Validate manifests, schemas, SHA-256 checksums, links, and privacy hygiene."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
HEX64_RE = re.compile(r'^[0-9a-f]{64}$')
MD_LINK_RE = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')


def _validate_manifest(manifest: dict, plugin_schema: dict, *, label: str) -> None:
    for req_key in plugin_schema['required']:
        if req_key not in manifest:
            raise ValueError(f'{label}: missing required field {req_key!r}')
    props = plugin_schema['properties']
    for field, rule in props.items():
        if field not in manifest:
            continue
        val = manifest[field]
        expected_type = rule.get('type')
        if expected_type == 'string' and not isinstance(val, str):
            raise ValueError(f'{label}.{field}: expected string')
        if expected_type == 'integer' and (isinstance(val, bool) or not isinstance(val, int)):
            raise ValueError(f'{label}.{field}: expected integer')
        if expected_type == 'boolean' and not isinstance(val, bool):
            raise ValueError(f'{label}.{field}: expected boolean')
        if expected_type == 'array' and not isinstance(val, list):
            raise ValueError(f'{label}.{field}: expected list')
        if 'minLength' in rule and len(val) < rule['minLength']:
            raise ValueError(f'{label}.{field}: shorter than minLength')
        if 'minimum' in rule and val < rule['minimum']:
            raise ValueError(f'{label}.{field}: below minimum')
        if 'enum' in rule and val not in rule['enum']:
            raise ValueError(f'{label}.{field}: {val!r} not in {rule["enum"]}')
        if 'pattern' in rule and not re.search(rule['pattern'], val):
            raise ValueError(f'{label}.{field}: {val!r} does not match {rule["pattern"]}')


def _check_privacy_and_hygiene() -> None:
    banned = [
        re.compile('auto' + 'Files', re.IGNORECASE),
        re.compile(r'C:\\\\?Users', re.IGNORECASE),
        re.compile(r'\bD:\\\\'),
        re.compile(r'192\.168\.'),
        re.compile(r'\b[0-9a-f]{2}(:[0-9a-f]{2}){5}\b', re.IGNORECASE),
    ]
    local_user = '\u82cf\u6653\u6c89'
    checked = 0
    for path in REPO_ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts:
            continue
        if path.suffix.lower() not in ('.md', '.json', '.nsi', '.txt', '.py'):
            continue
        checked += 1
        text = path.read_text(encoding='utf-8', errors='replace')
        # LICENSE legitimately carries the MIT copyright holder name; disallow in technical files elsewhere.
        if path.name != 'LICENSE' and path.name != 'verify_repo.py' and local_user in text:
            raise ValueError(f'Privacy violation: local author marker found in {path.relative_to(REPO_ROOT)}')
        if path.name != 'verify_repo.py':
            for pat in banned:
                if pat.search(text):
                    raise ValueError(f'Banned pattern {pat.pattern!r} matched in {path.relative_to(REPO_ROOT)}')
    print(f'[PASS] Privacy & hygiene scan ({checked} text files)')


def _check_markdown_links() -> None:
    count = 0
    for md in REPO_ROOT.rglob('*.md'):
        if '.git' in md.parts:
            continue
        text = md.read_text(encoding='utf-8')
        for match in MD_LINK_RE.finditer(text):
            target = match.group(1).strip().split('#', 1)[0]
            if not target or target.startswith(('http://', 'https://', 'mailto:')):
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                raise ValueError(f'Broken relative Markdown link in {md.relative_to(REPO_ROOT)}: {match.group(1)!r}')
            count += 1
    print(f'[PASS] Relative Markdown links ({count} links resolved)')


def _check_python_syntax() -> None:
    count = 0
    for py_file in REPO_ROOT.rglob('*.py'):
        if '.git' in py_file.parts:
            continue
        ast.parse(py_file.read_text(encoding='utf-8'), filename=str(py_file))
        count += 1
    print(f'[PASS] Python AST syntax check ({count} files)')


def _check_catalog_and_plugins() -> None:
    catalog_schema = json.loads((REPO_ROOT / 'schemas' / 'catalog.schema.json').read_text(encoding='utf-8'))
    plugin_schema = json.loads((REPO_ROOT / 'schemas' / 'plugin.schema.json').read_text(encoding='utf-8'))

    catalog = json.loads((REPO_ROOT / 'catalog.json').read_text(encoding='utf-8'))
    for req_key in catalog_schema['required']:
        if req_key not in catalog:
            raise ValueError(f'catalog.json: missing {req_key!r}')
    if catalog['schemaVersion'] != 1:
        raise ValueError(f'catalog.json: unsupported schemaVersion {catalog["schemaVersion"]!r}')

    sample = json.loads((REPO_ROOT / 'examples' / 'catalog.sample.json').read_text(encoding='utf-8'))
    for idx, entry in enumerate(sample['plugins']):
        _validate_manifest(entry, plugin_schema, label=f'examples/catalog.sample.json[{idx}]')

    by_id = {}
    for idx, entry in enumerate(catalog['plugins']):
        _validate_manifest(entry, plugin_schema, label=f'catalog.json[{idx}]')
        by_id[entry['id']] = entry

    plugin_manifests = sorted((REPO_ROOT / 'plugins').glob('*/plugin.json'))
    if not plugin_manifests:
        raise ValueError('No official plugins found under plugins/*/plugin.json')

    for mf_path in plugin_manifests:
        mf = json.loads(mf_path.read_text(encoding='utf-8'))
        _validate_manifest(mf, plugin_schema, label=str(mf_path.relative_to(REPO_ROOT)))
        ext_id = mf['id']
        if ext_id not in by_id:
            raise ValueError(f'{mf_path.relative_to(REPO_ROOT)}: missing from catalog.json')
        if by_id[ext_id] != mf:
            raise ValueError(f'{ext_id}: plugin.json differs from catalog.json entry')

        dist_dir = mf_path.parent / 'dist'
        installer = dist_dir / mf['installerName']
        if not installer.is_file():
            raise ValueError(f'{ext_id}: missing installer {installer.relative_to(REPO_ROOT)}')
        raw = installer.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha != mf['sha256'] or not HEX64_RE.match(sha):
            raise ValueError(f'{ext_id}: SHA-256 mismatch ({sha} != {mf["sha256"]})')
        if len(raw) != mf['size']:
            raise ValueError(f'{ext_id}: size mismatch ({len(raw)} != {mf["size"]})')

        sums = (dist_dir / 'SHA256SUMS.txt').read_text(encoding='utf-8').strip()
        expected_line = f'{sha}  {mf["installerName"]}'
        if expected_line not in sums.splitlines():
            raise ValueError(f'{ext_id}: SHA256SUMS.txt missing {expected_line!r}')

    tmpl = json.loads((REPO_ROOT / 'templates' / 'extension-template' / 'plugin.json').read_text(encoding='utf-8'))
    _validate_manifest(tmpl, plugin_schema, label='templates/extension-template/plugin.json')
    print(f'[PASS] Schemas, catalog.json, and {len(plugin_manifests)} official plugin(s) + installers')


def main() -> int:
    _check_catalog_and_plugins()
    _check_markdown_links()
    _check_python_syntax()
    _check_privacy_and_hygiene()
    print('ALL REPOSITORY CHECKS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
