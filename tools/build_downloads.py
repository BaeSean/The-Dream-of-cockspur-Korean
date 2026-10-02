"""Preserve quick installer and assemble the ready-to-copy distribution."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GUIDES = {
    'QuickInstall': ('CockspurKoreanPatcher.exe', '''빠른 설치용 (Windows 64비트)
1. 원본 게임을 설치하고 종료한 뒤 ZIP을 별도 폴더에 전부 압축 해제합니다.
2. CockspurKoreanPatcher.exe를 실행합니다. Python이나 명령줄은 필요 없습니다.
3. 게임 폴더 선택 → 한국어 패치 설치를 누릅니다.
4. 게임에서 English를 선택합니다.
복원: 같은 프로그램에서 게임 폴더 선택 → 원본으로 복원.
게임 폴더의 _cockspur_ko_backup은 복원 전까지 보관하십시오.
'''),

}

def main():
    output = ROOT / 'downloads'
    output.mkdir(exist_ok=True)
    common = [ROOT/'manifest.json']
    for directory in ('patches', 'runtime', 'licenses'):
        common += sorted(p for p in (ROOT/directory).rglob('*') if p.is_file())
    report = {}
    previous = json.loads((output/'SHA256.json').read_text()) if (output/'SHA256.json').exists() else {}
    for mode, (executable, guide) in GUIDES.items():
        if mode == 'CopyPaste':
            continue
        target = output / ('Cockspur-Korean-' + mode + '.zip')
        if target.exists() and target.name in previous:
            assert hashlib.sha256(target.read_bytes()).hexdigest() == previous[target.name]['sha256']
            report[target.name] = previous[target.name]
            continue
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            def add(name, data):
                info = zipfile.ZipInfo(name, (2026, 10, 2, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
            add(executable, (ROOT/'CockspurKoreanPatcher.exe').read_bytes())
            add('START-HERE.txt', guide.encode('utf-8-sig'))
            for path in common:
                add(path.relative_to(ROOT).as_posix(), path.read_bytes())
        report[target.name] = {'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size, 'entry_point': executable}
    parts = ROOT/'copy-package-parts'
    index = json.loads((parts/'index.json').read_text())
    blocks = []
    for item in index['parts']:
        assert Path(item['name']).name == item['name']
        block = (parts/item['name']).read_bytes()
        assert len(block) == item['bytes'] and hashlib.sha256(block).hexdigest() == item['sha256']
        blocks.append(block)
    data = b''.join(blocks)
    assert len(data) == index['bytes'] and hashlib.sha256(data).hexdigest() == index['sha256']
    (output/index['zip_file']).write_bytes(data)
    report[index['zip_file']] = {'sha256': index['sha256'], 'bytes': len(data), 'entry_point': 'The Dream Of A Cockspur_Data', 'installation': 'copy-and-overwrite', 'game_files': 33}
    (output/'SHA256.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
