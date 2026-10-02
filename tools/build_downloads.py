"""Build two minimal distributions, without reconstructed game files."""
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
    'CopyPaste': ('CockspurCopyFiles.exe', '''복사·붙여넣기용 (Windows 64비트)
1. 최초 1회 원본 게임을 바탕으로 복사용 파일을 생성해야 합니다. 이 ZIP에는 전체 수정 게임 파일이 없습니다.
2. 게임을 종료하고 ZIP을 별도 폴더에 전부 압축 해제한 뒤 CockspurCopyFiles.exe를 실행합니다.
3. 원본 게임 폴더 선택 → 복사용 파일 만들기 → 게임 폴더 밖의 저장 위치를 선택합니다. Python이나 명령줄은 필요 없습니다.
4. 생성된 Cockspur-copy-files\\files 안의 The Dream Of A Cockspur_Data 폴더를 게임 실행 파일이 있는 폴더에 붙여넣고 덮어씁니다.
5. 게임에서 English를 선택합니다.
복원: original-files 안의 폴더를 같은 위치에 덮어쓰고 added-files.txt에 적힌 추가 파일 8개만 삭제합니다.
original-files 백업은 보관하십시오. 복사 설치에는 자동 설치의 복원 버튼을 사용하지 않습니다.
생성된 파일에는 게임 자산이 포함되므로 재배포하지 마십시오.
'''),
}

def main():
    output = ROOT / 'downloads'
    output.mkdir(exist_ok=True)
    common = [ROOT/'manifest.json']
    for directory in ('patches', 'runtime', 'licenses'):
        common += sorted(p for p in (ROOT/directory).rglob('*') if p.is_file())
    report = {}
    for mode, (executable, guide) in GUIDES.items():
        target = output / ('Cockspur-Korean-' + mode + '.zip')
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
    (output/'SHA256.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
