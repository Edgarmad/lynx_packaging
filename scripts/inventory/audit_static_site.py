"""Audit built HTML links, assets and basic document invariants without a server."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.h1 = 0
        self.noindex = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'meta' and a.get('name') == 'robots':
            self.noindex = 'noindex' in a.get('content', '')
        for key in ('href', 'src', 'poster'):
            if a.get(key): self.links.append(a[key])

errors = []
pages = list(DIST.rglob('*.html'))
references = 0
anchor_cache = {}
for path in pages:
    page = Page()
    page.feed(path.read_text(encoding='utf-8'))
    anchor_cache[path] = set(page.ids)
    rel = path.relative_to(DIST).as_posix()
    if page.h1 != 1: errors.append([rel, 'h1', page.h1])
    if len(page.ids) != len(set(page.ids)): errors.append([rel, 'duplicate id'])
    if not page.noindex: errors.append([rel, 'missing preview noindex'])
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc: continue
        references += 1
        target = (DIST / unquote(url.path).lstrip('/')) if url.path.startswith('/') else (path.parent / unquote(url.path))
        if not url.path: target = path
        if target.is_dir(): target = target / 'index.html'
        if not target.exists(): errors.append([rel, 'missing target', link])
        elif url.fragment and target.suffix == '.html':
            if target not in anchor_cache:
                other = Page()
                other.feed(target.read_text(encoding='utf-8'))
                anchor_cache[target] = set(other.ids)
            if unquote(url.fragment) not in anchor_cache[target]: errors.append([rel, 'missing anchor', link])
report = {'pages': len(pages), 'references': references, 'errors': errors}
out = ROOT / 'tmp/catalog-review/static-audit.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(bool(errors))
