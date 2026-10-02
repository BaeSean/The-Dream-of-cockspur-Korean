from pathlib import Path
import hashlib,json,zipfile,argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--files',required=True,type=Path);FILES=parser.parse_args().files
rows=json.loads((ROOT/'manifest.json').read_text())
guide='''The Dream Of A Cockspur 한국어 패치 — 복사·붙여넣기

1. CopyPaste ZIP을 다운로드하고 게임 밖의 폴더에 압축을 전부 풉니다.
2. 게임을 종료하고 Steam 라이브러리 → 게임 우클릭 → 관리 → 로컬 파일 보기를 누릅니다.
3. 덮어쓰기 전에 원본 The Dream Of A Cockspur_Data 폴더 전체를 게임 밖에 복사해 백업합니다. 그다음 ZIP에서 푼 The Dream Of A Cockspur_Data 폴더를 게임 실행 파일이 있는 폴더에 붙여넣고 같은 이름의 파일을 덮어씁니다.
4. 게임을 실행하고 언어를 English로 선택합니다.

패처 실행, Python 설치, 복사용 파일 생성은 필요 없습니다.
빠른설치용 ZIP과 함께 설치할 필요가 없습니다. 다른 패치가 있다면 먼저 해당 패치 방법으로 원본을 복원하십시오.

원본으로 복원:
게임을 종료합니다. 게임 안의 현재 The Dream Of A Cockspur_Data 폴더 이름을 The Dream Of A Cockspur_Data-Korean-old로 바꿉니다. 게임 밖에 보관한 원본 The Dream Of A Cockspur_Data 폴더를 게임 실행 파일이 있는 위치에 복사합니다. 정상 복원을 확인할 때까지 이름을 바꾼 폴더를 보관합니다.
백업을 기존 패치 폴더에 단순 덮어쓰기만 하면 추가 파일이 남으므로 위 순서를 따르십시오. 이 수동 설치는 자동 패처의 Restore 기능으로 복원되지 않습니다.

수정 25파일과 추가 8파일만 포함합니다. 게임 실행 파일, 미수정 게임 파일, 세이브, 원본 백업은 포함하지 않습니다. 포함된 수정 Unity 컨테이너에는 번역 외 원래 게임 데이터도 남아 있습니다. 소유한 지원 버전 게임에 사용하십시오.
'''
target=ROOT/'downloads/Cockspur-Korean-CopyPaste.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    def add(name,data):
        info=zipfile.ZipInfo(name,(2026,10,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,data)
    for row in rows:
        data=(FILES/row['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['patched_sha256']
        if not row.get('new_file'):assert hashlib.sha256(data).hexdigest()!=row['original_sha256']
        add(row['path'],data)
    add('START-HERE.txt',guide.encode('utf-8-sig'))
    add('PATCH-FILES-SHA256.json',json.dumps([{'path':r['path'],'sha256':r['patched_sha256'],'new_file':bool(r.get('new_file'))} for r in rows],indent=2).encode())
    add('licenses/SeochoBatang-OFL.txt',(ROOT/'licenses/SeochoBatang-OFL.txt').read_bytes())
data=target.read_bytes();parts=ROOT/'copy-package-parts';parts.mkdir(exist_ok=True)
index={'zip_file':target.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'parts':[],'patched_files':33,'payload_bytes':sum((FILES/r['path']).stat().st_size for r in rows)}
for i,start in enumerate(range(0,len(data),6*1024*1024)):
    block=data[start:start+6*1024*1024];name='%03d.part'%i;(parts/name).write_bytes(block)
    index['parts'].append({'name':name,'bytes':len(block),'sha256':hashlib.sha256(block).hexdigest()})
(parts/'index.json').write_text(json.dumps(index,indent=2)+'\n')
(ROOT/'docs/direct-copy-contents.json').write_text(json.dumps({'game_files': [{'path':r['path'],'bytes':(FILES/r['path']).stat().st_size,'sha256':r['patched_sha256'],'new_file':bool(r.get('new_file'))} for r in rows],'payload_bytes':index['payload_bytes'],'game_executable_included':False,'original_backups_included':False,'game_save_files_included':False},indent=2))
print(json.dumps(index,indent=2))
