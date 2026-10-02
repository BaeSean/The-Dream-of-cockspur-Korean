"""Reconstruct the reviewed patch locally. Python standard library only."""
import argparse
import bz2
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def integer(data):
    if len(data) != 8:
        raise ValueError('Truncated BSDIFF integer')
    value = int.from_bytes(data, 'little')
    return -(value & ((1 << 63) - 1)) if value >> 63 else value


def patch(old, delta):
    if delta[:8] != b'BSDIFF40' or len(delta) < 32:
        raise ValueError('Invalid BSDIFF40 header')
    ctrl_len, diff_len, size = [integer(delta[i:i+8]) for i in (8, 16, 24)]
    if min(ctrl_len, diff_len, size) < 0 or 32 + ctrl_len + diff_len > len(delta) or size > 1024**3:
        raise ValueError('Invalid BSDIFF40 lengths')
    ctrl = bz2.decompress(delta[32:32+ctrl_len])
    diff = bz2.decompress(delta[32+ctrl_len:32+ctrl_len+diff_len])
    extra = bz2.decompress(delta[32+ctrl_len+diff_len:])
    result = bytearray()
    cp = dp = ep = op = 0
    while len(result) < size:
        x, y, z = [integer(ctrl[cp+i:cp+i+8]) for i in (0, 8, 16)]
        cp += 24
        if min(x, y) < 0 or len(result)+x+y > size or dp+x > len(diff) or ep+y > len(extra):
            raise ValueError('Invalid BSDIFF40 control record')
        chunk = bytearray(diff[dp:dp+x])
        for i in range(x):
            if 0 <= op+i < len(old):
                chunk[i] = (chunk[i] + old[op+i]) & 255
        result.extend(chunk)
        result.extend(extra[ep:ep+y])
        dp += x
        ep += y
        op += x+z
    return bytes(result)


def contained(root, relative):
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        raise ValueError('Path outside folder')
    return path


def prepare(game, output):
    game, output = Path(game).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('Output already exists; choose a fresh output folder')
    rows = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    # Complete all input validation before creating reconstructed files.
    for row in rows:
        payload = contained(ROOT, row['payload']).read_bytes()
        if sha(payload) != row['payload_sha256']:
            raise ValueError('Corrupt patch payload: ' + row['path'])
        source = contained(game, row['path'])
        if not row.get('new_file') and sha(source.read_bytes()) != row['original_sha256']:
            raise ValueError('Unsupported game version or already patched file: ' + row['path'])
        if row.get('new_file') and source.exists():
            raise ValueError('Existing localization file; restore the prior patch first: ' + row['path'])
    for row in rows:
        payload = contained(ROOT, row['payload']).read_bytes()
        data = payload if row.get('new_file') else patch(contained(game, row['path']).read_bytes(), payload)
        if sha(data) != row['patched_sha256']:
            raise ValueError('Reconstruction checksum mismatch: ' + row['path'])
        target = contained(output / 'files', row['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (output / 'manifest.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    shutil.copyfile(ROOT / 'tools/Apply-Patch.ps1', output / 'Apply-Patch.ps1')
    print('Verified and reconstructed %d files. Game installation unchanged.' % len(rows))
    print('Local installer: ' + str(output / 'Apply-Patch.ps1'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-dir', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-package')
    args = parser.parse_args()
    prepare(args.game_dir, args.output)
