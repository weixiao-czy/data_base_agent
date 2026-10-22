"""Package only active promo source. No media generation or dependency install.

Run from any directory: python promo/scripts/package_source.py
Python 3.9+ is needed only to rebuild this ZIP, never to render the film.
"""
from pathlib import Path
import hashlib
import zipfile

root = Path(__file__).resolve().parents[1]
files = [
    '.gitignore', 'README.md', 'STORYBOARD.md', 'RENDER_HANDOFF.md',
    'package.json', 'package-lock.json', 'remotion.config.ts', 'tsconfig.json',
    'src/index.ts', 'src/Root.tsx', 'src/Promo.tsx', 'src/global.css',
    'src/types.d.ts', 'src/film.json', 'src/components/Logo.tsx',
    'src/commercial/Commercial.tsx', 'src/commercial/design.tsx',
    'src/commercial/TreeScenes.tsx', 'src/commercial/tree-demo.json',
    'scripts/audio-plan.mjs', 'scripts/gen_audio.mjs',
    'scripts/check-project.mjs', 'scripts/preview.mjs', 'scripts/package_source.py',
]
# An allowlist prevents accidental delivery of credentials, old videos or caches.
manifest = '\n'.join(f'{hashlib.sha256((root / file).read_bytes()).hexdigest()}  {file}' for file in files) + '\n'
out = root / 'out' / 'delivery' / 'promo-litmap-84s-source.zip'
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for file in files:
        archive.write(root / file, f'promo/{file}')
    archive.writestr('promo/MANIFEST.sha256', manifest)
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(files) + 1
    for line in manifest.splitlines():
        digest, file = line.split('  ', 1)
        assert hashlib.sha256(archive.read(f'promo/{file}')).hexdigest() == digest
print(f'Packaged and verified {len(files)} source files: {out} ({out.stat().st_size:,} bytes)')
