"""Build Cloud 3.2 demo from the reviewed 3.1 public snapshot; never touch backend."""
from pathlib import Path
import hashlib
import sys

BASE_SHA256 = 'd18f43f7e493e4bf07fc69e9ddbbc2735484c242f686007fc8e2b848e3f713f0'
ROOT = Path(__file__).resolve().parent

def build(base: Path, destination: Path) -> None:
    raw = base.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise ValueError('Unexpected published baseline: reconcile rather than overwrite.')
    html = raw.decode('utf-8')
    marker = 'const initial=location.hash.slice(1);'
    if html.count(marker) != 1 or html.count('</style>') != 1:
        raise ValueError('Ambiguous integration markers')
    code = '\n'.join((ROOT/name).read_text('utf-8') for name in ['core.js','tutor.js','studio.js'])
    html = html.replace(marker, '\n'+code+'\n'+marker, 1)
    html = html.replace('</style>', '\n'+(ROOT/'styles.css').read_text('utf-8')+'\n</style>', 1)
    html = html.replace('cloud-v3.1-nav-tutor-2026-09-18','cloud-v3.2-studio-tutor-2026-09-18')
    html = html.replace('Cloud v3.1','Cloud v3.2').replace('ДЕМО · V3.1','ДЕМО · V3.2')
    html = html.replace("<title>Cloud v3.1", "<title>Cloud v3.2")
    if 'href="styles.css"' in html or 'src="app.js"' in html:
        raise ValueError('Demo must remain standalone')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')
    print('Built Cloud 3.2:', destination.stat().st_size, 'bytes; SHA256', hashlib.sha256(destination.read_bytes()).hexdigest())

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: apply.py BASELINE_HTML OUTPUT_HTML')
    build(Path(sys.argv[1]), Path(sys.argv[2]))
