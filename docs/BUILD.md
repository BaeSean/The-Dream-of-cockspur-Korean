# 설치 프로그램 빌드

제공된 Windows 64비트 실행 파일은 Python 3.8.9, PyInstaller 6.22.3으로 빌드했습니다. 일반 사용자는 빌드하거나 Python을 설치할 필요가 없습니다.

개발 환경에서 저장소 루트를 기준으로:

```powershell
python -m pip install pyinstaller==6.22.3
python -m PyInstaller --noconfirm --onefile --windowed --name CockspurKoreanPatcher --distpath . --workpath .work/build --specpath .work/build --paths tools tools/patcher_gui.py
python -m unittest discover -s tests -v
python tools/verify_package.py
```

프로그램은 같은 폴더의 manifest.json 및 patches/runtime만 읽습니다. 게임 원본, 번역 추출 자료, 계정 정보, 네트워크 기능을 실행 파일에 포함하지 않습니다. PyInstaller가 만든 실행 파일의 바이트 해시는 빌드 환경에 따라 달라질 수 있습니다.

독립 실행 파일의 `--test-fixture <격리원본폴더> <보고서경로>` 모드는 해당 격리 복사본에 설치한 뒤 복원하는 회귀 검사입니다. 실제 게임 설치나 개인 파일을 이 모드로 시험하지 마십시오. `--smoke-ui <보고서경로>`는 창을 표시하지 않고 Tk 및 화면 구성 초기화를 검사합니다.

설치 프로그램은 모든 입력 해시를 검사하고 결과를 임시 폴더에서 재구성한 뒤 원본을 백업합니다. 설치 중 오류가 나면 변경한 파일을 백업에서 복구합니다. 복원은 먼저 모든 백업 해시를 검사합니다. 강제 종료·전원 차단 시에는 백업을 유지하고 상태 확인 후 복원을 시도하십시오.
