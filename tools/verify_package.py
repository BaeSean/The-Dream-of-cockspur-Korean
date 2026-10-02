"""Check distributable payload hashes without requiring the game."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    assert len(rows) == 33
    assert len({r['path'] for r in rows}) == 33
    expected = set()
    for row in rows:
        relative = Path(row['payload'])
        assert not relative.is_absolute() and '..' not in relative.parts
        data = (ROOT / relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row['payload_sha256'], row['payload']
        if row.get('new_file'):
            assert row['format'] == 'new-localization-asset'
            assert relative.parts[0] == 'runtime'
            assert '/Managed/KoreanImageAssets/' in row['path'] or row['path'].endswith('/Managed/KoreanImageSubtitles.dll')
        else:
            assert row['format'] == 'BSDIFF40' and data[:8] == b'BSDIFF40'
            assert relative.parts[0] == 'patches'
            assert hashlib.sha256(data).hexdigest() not in (row['original_sha256'], row['patched_sha256'])
        expected.add(relative.as_posix())
    actual = {p.relative_to(ROOT).as_posix() for name in ('patches', 'runtime') for p in (ROOT / name).rglob('*') if p.is_file()}
    assert actual == expected
    print('PASS: 25 BSDIFF40 deltas and 8 new localization assets; 33 payload hashes verified.')


if __name__ == '__main__':
    main()
