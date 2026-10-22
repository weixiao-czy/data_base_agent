"""Create a self-contained SOURCE archive, not a video. No media generation."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
FILES = ['.gitattributes', '.gitignore', 'package.json', 'package-lock.json', 'remotion.config.ts',
         'tsconfig.json', 'props-voice.json', 'README.md', 'RENDER_HANDOFF.md',
         'STORYBOARD.md', 'NARRATION.md', 'QUICKSTART.md', 'FACT_CHECK.md',
         'subtitles.srt', 'CHAPTERS.txt', 'narration-cues.json', 'LICENSE']


def main():
    files = [ROOT / name for name in FILES]
    files += sorted((ROOT / 'src').glob('*'))
    files += sorted(p for p in (ROOT / 'scripts').glob('*') if p.suffix in {'.py', '.mjs', '.ps1'})
    assert all(p.is_file() for p in files)
    manifest = '\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}' for p in files) + '\n'
    output = ROOT / 'out' / 'delivery'
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'databaseagent-tutorial-source.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, 'databaseagent-tutorial/' + file.relative_to(ROOT).as_posix())
        archive.writestr('databaseagent-tutorial/SHA256SUMS.txt', manifest)
        archive.writestr('databaseagent-tutorial/public/', '')
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for file in files:
            assert archive.read('databaseagent-tutorial/' + file.relative_to(ROOT).as_posix()) == file.read_bytes()
        assert not any('/node_modules/' in n or n.endswith(('.wav','.mp4','.env')) for n in archive.namelist())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (output / (target.name + '.sha256')).write_text(f'{digest}  {target.name}\n', encoding='utf-8')
    print(f'{target}\n{len(files)} source files; verified CRC and byte-for-byte content. SHA256 {digest}')


if __name__ == '__main__':
    main()
