"""Verify Alp extension metadata, local files and public download links."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git', '.venv', '__pycache__', 'build'}
GITHUB_HOSTS = {'github.com', 'raw.githubusercontent.com'}
MD_LINK_RE = re.compile(r'!?\[[^\]\r\n]*\]\((<[^>\r\n]+>|[^)\s]+)(?:[ \t]+"[^"\r\n]*")?\)')
MD_REFERENCE_RE = re.compile(r'^[ \t]{0,3}\[[^\]\r\n]+\]:[ \t]+(<[^>\r\n]+>|\S+)', re.MULTILINE)


def _repo_files(pattern: str):
    for path in sorted(REPO_ROOT.rglob(pattern)):
        if path.is_file() and not IGNORED_DIRS.intersection(path.relative_to(REPO_ROOT).parts):
            yield path


def _validate_manifest(manifest: dict, schema: dict, *, label: str) -> None:
    if not isinstance(manifest, dict):
        raise ValueError(f'{label}: expected an object')
    for key in schema['required']:
        if key not in manifest:
            raise ValueError(f'{label}: missing required field {key!r}')
    for field, rule in schema['properties'].items():
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
        if 'const' in rule and val != rule['const']:
            raise ValueError(f'{label}.{field}: expected {rule["const"]!r}')
        if 'minLength' in rule and len(val) < rule['minLength']:
            raise ValueError(f'{label}.{field}: shorter than minLength')
        if 'minimum' in rule and val < rule['minimum']:
            raise ValueError(f'{label}.{field}: below minimum')
        if 'enum' in rule and val not in rule['enum']:
            raise ValueError(f'{label}.{field}: {val!r} not in {rule["enum"]}')
        if 'pattern' in rule and not re.search(rule['pattern'], val):
            raise ValueError(f'{label}.{field}: {val!r} does not match {rule["pattern"]}')


def _check_privacy_and_hygiene(public_owner: str) -> None:
    banned = [
        re.compile(r'\b[a-z]:[\\/]', re.IGNORECASE),
        re.compile(r'(?:file):/{2}|/(?:Users|home)/', re.IGNORECASE),
        re.compile(r'\b192\.168\.'),
        re.compile(r'\b[0-9a-f]{2}(?:[:-][0-9a-f]{2}){5}\b', re.IGNORECASE),
    ]
    local_user = Path.home().name
    account = re.compile(r'(?<![\w-])' + re.escape(local_user) + r'(?![\w-])', re.IGNORECASE)
    check_account = bool(local_user) and local_user.casefold() != public_owner.casefold()
    checked = 0
    for path in _repo_files('*'):
        if path.suffix.lower() not in ('.md', '.json', '.nsi', '.txt', '.py') and path.name != 'LICENSE':
            continue
        checked += 1
        text = path.read_text(encoding='utf-8')
        # The MIT notice retains the public copyright attribution.
        if path != REPO_ROOT / 'LICENSE' and check_account and account.search(text):
            raise ValueError(f'Private account name in {path.relative_to(REPO_ROOT)}')
        for pattern in banned:
            if pattern.search(text):
                raise ValueError(f'Local path or device address in {path.relative_to(REPO_ROOT)}')
    print(f'[PASS] Privacy & hygiene scan ({checked} text files)')


def _check_markdown_links(catalog: dict, raw_base: str) -> set[str]:
    repo = catalog['repository']
    branch = catalog['branch']
    links = set()
    resolved_count = 0
    routes = (
        (f'{repo}/tree/{branch}/', True),
        (f'{repo}/blob/{branch}/', False),
        (f'{repo}/raw/{branch}/', False),
        (raw_base, False),
    )
    for md in _repo_files('*.md'):
        text = md.read_text(encoding='utf-8')
        targets = MD_LINK_RE.findall(text) + MD_REFERENCE_RE.findall(text)
        for target in targets:
            url = urlsplit(target.strip('<>'))
            if url.scheme or url.netloc:
                if url.scheme == 'https' and url.hostname in GITHUB_HOSTS:
                    links.add(url._replace(fragment='').geturl())
                absolute = url._replace(query='', fragment='').geturl()
                for prefix, is_dir in routes:
                    if absolute.startswith(prefix):
                        path = (REPO_ROOT / unquote(absolute.removeprefix(prefix))).resolve()
                        exists = path.is_dir() if is_dir else path.is_file()
                        if not path.is_relative_to(REPO_ROOT) or not exists:
                            raise ValueError(f'Broken GitHub path in {md.relative_to(REPO_ROOT)}: {target}')
                        resolved_count += 1
                        break
                continue

            if not url.path:
                continue
            path = (md.parent / unquote(url.path)).resolve()
            if not path.is_relative_to(REPO_ROOT) or not path.exists():
                raise ValueError(f'Broken relative link in {md.relative_to(REPO_ROOT)}: {target}')
            route = 'tree' if path.is_dir() else 'blob'
            links.add(f'{repo}/{route}/{branch}/{quote(path.relative_to(REPO_ROOT).as_posix())}')
            resolved_count += 1
    print(f'[PASS] Markdown relative and repository links ({resolved_count} paths resolved)')
    return links


def _check_python_syntax() -> None:
    count = 0
    for py_file in _repo_files('*.py'):
        ast.parse(py_file.read_text(encoding='utf-8'), filename=str(py_file))
        count += 1
    print(f'[PASS] Python AST syntax check ({count} files)')


def _check_catalog_and_plugins() -> tuple[dict, dict[str, Path]]:
    catalog_schema = json.loads((REPO_ROOT / 'schemas' / 'catalog.schema.json').read_text(encoding='utf-8'))
    plugin_schema = json.loads((REPO_ROOT / 'schemas' / 'plugin.schema.json').read_text(encoding='utf-8'))

    catalog = json.loads((REPO_ROOT / 'catalog.json').read_text(encoding='utf-8'))
    _validate_manifest(catalog, catalog_schema, label='catalog.json')
    sample = json.loads((REPO_ROOT / 'examples' / 'catalog.sample.json').read_text(encoding='utf-8'))
    _validate_manifest(sample, catalog_schema, label='examples/catalog.sample.json')
    for idx, entry in enumerate(sample['plugins']):
        _validate_manifest(entry, plugin_schema, label=f'examples/catalog.sample.json[{idx}]')

    by_id = {}
    for idx, entry in enumerate(catalog['plugins']):
        _validate_manifest(entry, plugin_schema, label=f'catalog.json[{idx}]')
        ext_id = entry['id']
        if ext_id in by_id:
            raise ValueError(f'catalog.json: duplicate extension ID {ext_id}')
        by_id[ext_id] = entry

    plugin_manifests = sorted((REPO_ROOT / 'plugins').glob('*/plugin.json'))
    if not plugin_manifests:
        raise ValueError('No official plugins found under plugins/*/plugin.json')

    downloads = {}
    seen_ids = set()
    for mf_path in plugin_manifests:
        mf = json.loads(mf_path.read_text(encoding='utf-8'))
        _validate_manifest(mf, plugin_schema, label=str(mf_path.relative_to(REPO_ROOT)))
        ext_id = mf['id']
        if ext_id in seen_ids or by_id.get(ext_id) != mf:
            raise ValueError(f'{ext_id}: duplicate or differs from catalog.json entry')
        seen_ids.add(ext_id)

        dist_dir = mf_path.parent / 'dist'
        installer = dist_dir / mf['installerName']
        if installer.parent != dist_dir or not installer.is_file():
            raise ValueError(f'{ext_id}: missing installer under dist/')
        raw = installer.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha != mf['sha256']:
            raise ValueError(f'{ext_id}: SHA-256 mismatch ({sha} != {mf["sha256"]})')
        if len(raw) != mf['size']:
            raise ValueError(f'{ext_id}: size mismatch ({len(raw)} != {mf["size"]})')

        sums = (dist_dir / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
        expected_line = f'{sha}  {mf["installerName"]}'
        if expected_line not in sums:
            raise ValueError(f'{ext_id}: SHA256SUMS.txt missing {expected_line!r}')
        downloads[mf['downloadUrl']] = installer

    if seen_ids != by_id.keys():
        raise ValueError(f'catalog.json: entries without extension manifests {sorted(by_id.keys() - seen_ids)}')
    tmpl = json.loads((REPO_ROOT / 'templates' / 'extension-template' / 'plugin.json').read_text(encoding='utf-8'))
    _validate_manifest(tmpl, plugin_schema, label='templates/extension-template/plugin.json')
    print(f'[PASS] Schemas, catalog and {len(plugin_manifests)} official extension installer(s)')
    return catalog, downloads


def _check_online(links: set[str], downloads: dict[str, Path]) -> None:
    for url in sorted(links | downloads.keys()):
        request = Request(url, headers={'User-Agent': 'Alp-Extension-Repository-Check'})
        with urlopen(request, timeout=20) as response:
            if local := downloads.get(url):
                if local.suffix == '.json':
                    matches = json.load(response) == json.loads(local.read_text(encoding='utf-8'))
                else:
                    expected = local.read_bytes()
                    matches = response.read(len(expected) + 1) == expected
                if not matches:
                    raise ValueError(f'Published download differs from the local file: {url}')
    print(f'[PASS] Published GitHub pages and links ({len(links | downloads.keys())} URLs)')
    print(f'[PASS] Published catalog values and installer bytes ({len(downloads)} files)')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--online', action='store_true', help='Also verify the published GitHub pages and downloads')
    options = parser.parse_args()

    catalog, downloads = _check_catalog_and_plugins()
    repository_path = urlsplit(catalog['repository']).path.strip('/')
    raw_base = f'https://raw.githubusercontent.com/{repository_path}/{catalog["branch"]}/'
    links = _check_markdown_links(catalog, raw_base)
    _check_python_syntax()
    _check_privacy_and_hygiene(repository_path.split('/', 1)[0])
    if options.online:
        links.update(entry['homepage'] for entry in catalog['plugins'] if 'homepage' in entry)
        downloads[f'{raw_base}catalog.json'] = REPO_ROOT / 'catalog.json'
        _check_online(links, downloads)
    print('ALL REPOSITORY CHECKS PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
