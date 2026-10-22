"""Fit independently supplied PCM WAV cues to exact lesson slots. Does not synthesize.
Requires ffmpeg on PATH (or FFMPEG env). Never runs on import or during npm check.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import wave

ROOT = Path(__file__).resolve().parent.parent
RATE = 48000
MAX_SPEED = 1.20


def main():
    ffmpeg = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if not ffmpeg:
        raise SystemExit('ffmpeg missing. Install it and add it to PATH, or set FFMPEG to its full executable path.')
    cues = json.loads((ROOT / 'narration-cues.json').read_text(encoding='utf-8-sig'))
    folder = ROOT / 'public' / 'voice-cues'
    fitted = folder / 'fitted'
    jobs, errors = [], []
    for cue in cues:
        source = folder / f'{cue["id"]:03}.wav'
        try:
            with wave.open(str(source), 'rb') as wav:
                seconds = wav.getnframes() / wav.getframerate()
            if seconds <= 0:
                raise ValueError('empty audio')
            speed = max(1.0, seconds / (cue['seconds'] - .30))
            if speed > MAX_SPEED:
                raise ValueError(f'{seconds:.2f}s speech exceeds {cue["seconds"]}s slot; rerecord this cue or extend lesson.json and regenerate docs')
            jobs.append((cue, source, speed))
        except (OSError, EOFError, wave.Error, ValueError) as exc:
            errors.append(f'Cue {cue["id"]:03}: {exc}')
    if errors:
        raise SystemExit('\n'.join(errors))
    fitted.mkdir(parents=True, exist_ok=True)
    paths = []
    for cue, source, speed in jobs:
        target = fitted / source.name
        length = round(cue['seconds'] * RATE)
        # Speech ends before the slot boundary. atrim removes padded silence only.
        filters = f'atempo={speed:.8f},aresample={RATE},adelay=150:all=1,apad,atrim=end_sample={length}'
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source),
                        '-af', filters, '-ar', str(RATE), '-ac', '1', '-c:a', 'pcm_s16le', str(target)], check=True)
        paths.append(target)
    # PCM concatenation avoids concat-demuxer quoting issues in arbitrary Windows paths.
    output = ROOT / 'public' / 'narration.wav'
    with wave.open(str(output), 'wb') as joined:
        joined.setnchannels(1)
        joined.setsampwidth(2)
        joined.setframerate(RATE)
        for target in paths:
            with wave.open(str(target), 'rb') as part:
                joined.writeframes(part.readframes(part.getnframes()))
    expected = round(sum(cue['seconds'] for cue in cues) * RATE)
    with wave.open(str(output), 'rb') as wav:
        assert wav.getnframes() == expected, 'Narration duration mismatch'
    print(f'Created {output}; exact length {expected / RATE:.3f}s. Listen and balance levels before final rendering.')


if __name__ == '__main__':
    main()
