"""Transactional patch installation shared by the desktop app and tests."""
import json
import os
from pathlib import Path
import shutil
import tempfile
from prepare import contained, patch, sha


class Patcher:
    def __init__(self, package, game, progress=lambda message: None):
        self.package, self.game = Path(package).resolve(), Path(game).resolve()
        self.rows = json.loads((self.package / 'manifest.json').read_text(encoding='utf-8'))
        self.backup = self.game / '_cockspur_ko_backup'
        if self.backup.is_symlink():
            raise ValueError('백업 폴더가 심볼릭 링크입니다.')
        self.state = self.backup / 'state.json'
        self.progress = progress

    def target(self, row):
        return contained(self.game, row['path'])

    def original(self, row):
        return contained(self.backup / 'originals', row['path'])

    def digest(self, path):
        return sha(path.read_bytes()) if path.is_file() else None

    def validate_payloads(self):
        for row in self.rows:
            if self.digest(contained(self.package, row['payload'])) != row['payload_sha256']:
                raise ValueError('패치 파일이 손상되었습니다: ' + row['payload'])

    def verify(self):
        self.validate_payloads()
        original = patched = 0
        for row in self.rows:
            digest = self.digest(self.target(row))
            if digest == row['patched_sha256']:
                patched += 1
            elif digest == row.get('original_sha256'):
                original += 1
            else:
                raise ValueError('지원하지 않는 버전 또는 다른 수정 파일입니다: ' + row['path'])
        if patched == len(self.rows):
            return 'installed'
        if original == len(self.rows):
            return 'original'
        return 'mixed'

    def save_state(self, status):
        self.backup.mkdir(parents=True, exist_ok=True)
        doc = {'game': str(self.game), 'status': status, 'manifest': self.rows}
        temp = self.backup / 'state.tmp'
        temp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(str(temp), str(self.state))

    @staticmethod
    def replace(source, target, expected):
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix='.cockspur-', dir=str(target.parent))
        os.close(fd)
        temporary = Path(name)
        try:
            shutil.copyfile(source, temporary)
            if sha(temporary.read_bytes()) != expected:
                raise ValueError('임시 파일 검증에 실패했습니다.')
            os.replace(str(temporary), str(target))
        finally:
            if temporary.exists():
                temporary.unlink()

    def install(self):
        status = self.verify()
        if status == 'installed':
            return '이미 한국어 패치가 설치되어 있습니다.'
        if status != 'original':
            raise ValueError('파일 상태가 섞여 있습니다. 기존 패치를 먼저 복원하십시오.')
        # Preflight existing backups before modifying any backup or game file.
        if self.backup.exists():
            if not self.state.is_file():
                raise ValueError('기존 백업 폴더가 있습니다. 내용을 보존하고 다른 설치 상태를 확인하십시오.')
            saved = json.loads(self.state.read_text(encoding='utf-8'))
            if saved.get('game') != str(self.game) or saved.get('manifest') != self.rows:
                raise ValueError('다른 설치의 백업입니다.')
            for row in self.rows:
                if not row.get('new_file') and self.digest(self.original(row)) != row['original_sha256']:
                    raise ValueError('기존 원본 백업이 손상되었습니다.')
        with tempfile.TemporaryDirectory(prefix='cockspur-ko-') as temporary:
            stage = Path(temporary)
            for i, row in enumerate(self.rows):
                self.progress('파일 준비 중 (%d/%d)' % (i+1, len(self.rows)))
                payload = contained(self.package, row['payload']).read_bytes()
                result = payload if row.get('new_file') else patch(self.target(row).read_bytes(), payload)
                if sha(result) != row['patched_sha256']:
                    raise ValueError('차분 복원 결과가 일치하지 않습니다: ' + row['path'])
                (stage / str(i)).write_bytes(result)
            if not self.backup.exists():
                for row in self.rows:
                    if row.get('new_file'):
                        continue
                    target = self.original(row)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open('xb') as stream:
                        stream.write(self.target(row).read_bytes())
                    if self.digest(target) != row['original_sha256']:
                        raise ValueError('원본 백업 검증에 실패했습니다. 게임 파일은 변경하지 않았습니다.')
            self.save_state('prepared')
            touched = []
            try:
                for i, row in enumerate(self.rows):
                    touched.append(row)
                    self.replace(stage / str(i), self.target(row), row['patched_sha256'])
                self.save_state('installed')
            except Exception:
                for row in reversed(touched):
                    target = self.target(row)
                    if row.get('new_file'):
                        if target.exists():
                            target.unlink()
                    else:
                        self.replace(self.original(row), target, row['original_sha256'])
                self.save_state('rolled_back')
                raise
        if self.verify() != 'installed':
            raise ValueError('설치 후 검증에 실패했습니다.')
        return '설치 완료! 게임에서 English를 선택하십시오.'

    def restore(self):
        self.verify()
        if not self.state.is_file():
            raise ValueError('이 프로그램의 원본 백업이 없습니다. 수동 설치는 수동 백업으로 복원하십시오.')
        saved = json.loads(self.state.read_text(encoding='utf-8'))
        if saved.get('game') != str(self.game) or saved.get('manifest') != self.rows:
            raise ValueError('다른 설치의 백업입니다.')
        for row in self.rows:
            if not row.get('new_file') and self.digest(self.original(row)) != row['original_sha256']:
                raise ValueError('원본 백업이 손상되어 복원을 중단했습니다.')
        for row in self.rows:
            target = self.target(row)
            if row.get('new_file'):
                if target.exists():
                    target.unlink()
            else:
                self.replace(self.original(row), target, row['original_sha256'])
        self.save_state('restored')
        if self.verify() != 'original':
            raise ValueError('복원 후 검증에 실패했습니다.')
        return '원본으로 복원했습니다. 백업은 보관되며 세이브는 변경하지 않았습니다.'

    def export_copy(self, output):
        """Create local copy/paste files and verified original backups; never install."""
        output = Path(output).resolve()
        try:
            output.relative_to(self.game)
        except ValueError:
            pass
        else:
            raise ValueError('게임 폴더 밖의 저장 위치를 선택하십시오.')
        if output.exists():
            raise ValueError('복사용 폴더가 이미 있습니다. 기존 파일을 보존하려면 다른 저장 위치를 선택하십시오.')
        if self.verify() != 'original':
            raise ValueError('원본 상태에서만 복사용 파일을 만들 수 있습니다. 기존 패치를 먼저 복원하십시오.')
        # Stage beside the destination so the final rename exposes only a complete package.
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.cockspur-copy-', dir=str(output.parent)) as temporary:
            stage = Path(temporary) / 'package'
            stage.mkdir()
            for i, row in enumerate(self.rows):
                self.progress('복사용 파일 준비 중 (%d/%d)' % (i+1, len(self.rows)))
                payload = contained(self.package, row['payload']).read_bytes()
                original = b'' if row.get('new_file') else self.target(row).read_bytes()
                result = payload if row.get('new_file') else patch(original, payload)
                if sha(result) != row['patched_sha256']:
                    raise ValueError('복사용 파일 검증에 실패했습니다: ' + row['path'])
                target = contained(stage / 'files', row['path'])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(result)
                if self.digest(target) != row['patched_sha256']:
                    raise ValueError('저장된 복사용 파일 검증에 실패했습니다.')
                if not row.get('new_file'):
                    if sha(original) != row['original_sha256']:
                        raise ValueError('작업 중 원본 파일이 변경되었습니다.')
                    backup = contained(stage / 'original-files', row['path'])
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    backup.write_bytes(original)
                    if self.digest(backup) != row['original_sha256']:
                        raise ValueError('저장된 원본 백업 검증에 실패했습니다.')
            (stage / 'manifest.json').write_text(json.dumps(self.rows, indent=2), encoding='utf-8')
            additions = [r['path'] for r in self.rows if r.get('new_file')]
            (stage / 'added-files.txt').write_text('\n'.join(additions) + '\n', encoding='utf-8')
            instructions = ('복사 설치: files 안의 The Dream Of A Cockspur_Data 폴더만 게임 실행 파일이 있는 폴더에 붙여넣으십시오.\n'
                            '게임 폴더는 아직 변경하지 않았습니다. 설치 후 게임 언어를 English로 선택하십시오.\n'
                            '복원: original-files 안의 같은 폴더를 게임 폴더에 덮어쓴 뒤 added-files.txt의 추가 파일 8개를 삭제하십시오.\n'
                            '수동 설치는 패처의 원본으로 복원 버튼으로 복원할 수 없습니다. 상태 확인 버튼은 사용할 수 있습니다.\n'
                            '이 폴더는 사용자의 원본 게임 파일을 포함하는 로컬 백업입니다. 공개 업로드하거나 공유하지 마십시오.\n')
            (stage / '복사설치안내.txt').write_text(instructions, encoding='utf-8-sig')
            stage.rename(output)
        return '복사용 파일과 원본 백업을 만들었습니다. 게임 폴더는 변경하지 않았습니다.\n' + str(output)
