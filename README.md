# The Dream of a Cockspur 한국어 패치 / 한글패치

게임 설정에서 **English**를 선택하면 한국어로 표시됩니다. 서초바탕 글꼴을 사용합니다.

## 빠른 설치

1. [패치 ZIP 받기](https://github.com/BaeSean/The-Dream-of-cockspur-Korean/raw/refs/heads/main/downloads/Cockspur-Korean-QuickInstall.zip)를 누르고, 받은 `Cockspur-Korean-QuickInstall.zip`을 원하는 폴더에 전부 압축 해제합니다.
2. 게임을 종료하고, 압축 푼 폴더의 **`CockspurKoreanPatcher.exe`**를 실행합니다.
3. **게임 폴더 선택 → 한국어 패치 설치**를 누릅니다. 게임 폴더는 **스팀 라이브러리에서 게임 오른쪽 클릭 → 관리 → 로컬 파일 보기**로 찾을 수 있습니다. `The Dream Of A Cockspur.exe`가 있는 폴더를 선택하면 됩니다.
4. 설치 완료 후 게임을 실행하고 언어를 **English**로 선택합니다.

**Python 설치나 명령어 입력이 필요 없습니다.** Windows 64비트용입니다. 위 링크는 실행 프로그램과 패치 자료가 함께 들어 있는 빠른 설치 전용 ZIP이며, 별도 Releases 다운로드가 아닙니다. 실행 프로그램만 따로 옮기지 말고 압축 푼 폴더의 파일들을 함께 보관하십시오.

원본은 게임 폴더의 `_cockspur_ko_backup`에 자동 백업합니다. 원래 상태로 되돌리려면 같은 프로그램에서 같은 게임 폴더를 선택하고 **원본으로 복원**을 누르십시오. **상태 확인** 버튼으로 설치 상태도 확인할 수 있습니다. 백업 폴더는 복원이 필요할 동안 보관하십시오. 세이브 파일은 수정하지 않습니다.

이전에 다른 방식으로 설치한 패치가 있다면 해당 방식으로 먼저 복원하십시오. 새 프로그램은 원본 해시가 맞는 파일만 설치하며 기존 수동 설치의 백업을 임의로 대신하지 않습니다. 게임 업데이트로 지원 파일이 바뀌었으면 설치를 중단합니다.

## 복사·붙여넣기로 설치하기

**프로그램 실행이나 파일 생성 없이, 완성된 패치 파일을 붙여넣는 방식입니다.** 빠른설치 ZIP과 둘 다 설치할 필요는 없습니다.

1. [복사·붙여넣기 ZIP 다운로드](https://github.com/BaeSean/The-Dream-of-cockspur-Korean/raw/refs/heads/main/downloads/Cockspur-Korean-CopyPaste.zip) → 게임 밖의 폴더에 압축을 전부 풉니다.
2. 게임을 종료하고 **Steam 라이브러리 → 게임 우클릭 → 관리 → 로컬 파일 보기**를 누릅니다.
3. **덮어쓰기 전**, 원본 `The Dream Of A Cockspur_Data` 폴더 전체를 게임 밖에 복사해 백업합니다. ZIP에서 푼 **`The Dream Of A Cockspur_Data` 폴더 하나를 게임 실행 파일이 있는 폴더에 붙여넣고 덮어씁니다.** 기존 폴더에 병합해야 하며, 기존 폴더를 먼저 삭제하면 안 됩니다.
4. 게임을 실행하고 언어를 **English**로 선택합니다.

패처 실행·Python 설치·복사용 파일 생성은 필요 없습니다. ZIP에는 수정 25파일과 추가 8파일만 들어 있습니다. 게임 실행 파일, 미수정 게임 파일, 세이브, 원본 백업은 포함하지 않습니다. 수정된 Unity 컨테이너에는 번역 외 원래 게임 데이터도 함께 남아 있습니다. 다른 패치가 있다면 먼저 그 패치의 방법으로 원본을 복원하십시오. 게임 업데이트로 파일 구성이 달라진 버전에서는 사용하지 마십시오.

### 복사 설치를 원본으로 복원하기

1. 게임을 종료합니다.
2. 게임 안의 현재 `The Dream Of A Cockspur_Data` 폴더 이름을 `The Dream Of A Cockspur_Data-Korean-old`로 바꿉니다.
3. 게임 밖에 백업했던 **원본 `The Dream Of A Cockspur_Data` 폴더 전체**를 게임 실행 파일이 있는 위치로 복사합니다. 정상 복원을 확인할 때까지 이름을 바꾼 폴더를 보관합니다.

백업을 기존 패치 폴더에 덮어쓰기만 하면 추가 파일이 남으므로 위 순서를 따르십시오. **이 수동 설치는 자동 패처의 Restore 버튼으로 복원되지 않습니다.** 원본 백업이 없는 경우 기존 파일을 보존한 뒤 Steam에서 원본을 다시 받는 방식이 필요합니다.

## 번역 범위

| 구분 | 검증 항목 |
|---|---:|
| 대사·메뉴·인물명 | 1,484 |
| 공통 UI | 225 |
| 이미지 UI 참조 | 9 |
| 일기 | 30 |
| 장면 지역명 | 98 |
| 아이템 이름 | 72 |
| 합계 | **1,918** |

프롤로그 쪽지, 튜토리얼·조작 안내와 공용 책 이미지 번역도 기존 패치에 포함됩니다. 일본어·중국어 선택 시 원래 언어를 사용합니다.

2026-10-02 현재 번역 파일을 기존 검사기로 다시 검사한 결과 오류 0개, 경고 0개입니다. 이 검사는 전체 플레이·엔딩 재검증을 의미하지 않습니다. 장면 지역명 98곳은 기존 빌드 보고서의 수치를 확인하며, 번역 항목 1,918개가 모두 독립적인 신규 실기 테스트를 뜻하지 않습니다.

<details>
<summary>고급 대안: Python·PowerShell 명령으로 직접 관리하기</summary>

## Python으로 재구성

이하 절차는 실행 프로그램 대신 재구성 파일을 직접 관리하려는 경우에만 사용합니다. Windows PowerShell과 Python 3.8 이상이 필요합니다. Python 외 추가 패키지를 설치하지 않아도 됩니다. GitHub Releases 배포는 이번 작업에 포함하지 않습니다.

게임을 종료하십시오. 기존 한글 패치가 있다면 그 패치의 복원 기능으로 원본 상태를 복원하십시오. Steam 파일 무결성 검사만으로 이전 패치가 추가한 파일까지 제거되지는 않습니다. 다른 버전·변경된 파일은 해시 검사에서 거부됩니다. 세이브는 설치기가 변경하지 않지만 중요한 세이브는 따로 백업해 두십시오.

저장소 폴더에서 다음 명령을 실행합니다. `D:\Games\TheDreamOfACockspur`는 실제 게임 설치 경로로 바꾸십시오.

```powershell
python tools/prepare.py --game-dir "D:\Games\TheDreamOfACockspur"
```

이 개발용 Python 대안은 `.local-package\files`에 설치 파일을 만듭니다. 일반 사용자의 복사 설치에는 위 CopyPaste ZIP을 사용하면 되며, 이 재구성 절차는 필요 없습니다. 게임 파일을 읽고 차분을 적용하여 로컬 파일을 재구성합니다. 게임 설치 폴더는 변경하지 않습니다. 33개 결과 파일의 SHA-256이 기존 검수 패치와 모두 같아야 완료됩니다.

## 고급 대안: PowerShell 설치·확인·복원

```powershell
& .\.local-package\Apply-Patch.ps1 -Mode Verify -GameRoot "D:\Games\TheDreamOfACockspur"
& .\.local-package\Apply-Patch.ps1 -Mode Install -GameRoot "D:\Games\TheDreamOfACockspur"
& .\.local-package\Apply-Patch.ps1 -Mode Verify -GameRoot "D:\Games\TheDreamOfACockspur"
```

게임을 실행하고 언어를 **English**로 선택하십시오.

원래 상태로 복원하려면 게임을 종료하고 다음 명령을 실행합니다.

```powershell
& .\.local-package\Apply-Patch.ps1 -Mode Restore -GameRoot "D:\Games\TheDreamOfACockspur"
```

`.local-package` 안의 백업과 `install-state.json`은 복원에 필요하므로 보관하고 공유하지 마십시오. 공개 CopyPaste ZIP은 검증된 수정·추가 33파일만 선별하며, 이 로컬 작업 폴더나 원본 백업을 통째로 포함하지 않습니다. 스크립트 실행이 시스템 정책으로 차단되면 조직 정책을 우회하지 말고 허용된 실행 환경에서 진행하십시오.

</details>

## 저장소 구성

- `downloads/Cockspur-Korean-CopyPaste.zip`: 완성된 수정·추가 33파일을 바로 붙여넣는 패키지
- `copy-package-parts/`: CI에서 위 단일 ZIP을 조립하기 위한 저장소 내부 자료; 사용자는 받을 필요 없음

- `patches/`: 기존 게임 파일 25개에 대한 BSDIFF40 차분
- `CockspurKoreanPatcher.exe`: Python 설치 없이 사용하는 설치·확인·복원 프로그램
- `runtime/`: 패치가 추가하는 한국어 이미지 7개와 자체 런타임 DLL 1개
- `manifest.json`: 지원 원본·결과·배포 파일 해시와 경로
- `tools/prepare.py`: 외부 의존성 없는 로컬 재구성 도구
- `tools/Apply-Patch.ps1`: 원본 검증, 백업, 설치 실패 시 복구, 제거 도구
- `docs/`: 번역 및 패키지 검증 결과
- `licenses/`: 포함된 글꼴의 라이선스
- `tools/patcher_gui.py`, `tools/patcher_engine.py`: 프로그램 소스와 설치 엔진

실행 프로그램에는 Python·Tcl/Tk 런타임과 PyInstaller 부트로더가 포함됩니다. 해당 고지는 `licenses`에 있으며 빌드 방법은 `docs/BUILD.md`에 있습니다. 실행 프로그램의 설치·복원은 격리 복사본으로 검사했으며, 게임 전체 플레이를 이번에 다시 검증한 것은 아닙니다.

게임과 기존 그림의 권리는 각 원저작권자에게 있습니다. 비공식 번역 패치입니다. 서초바탕은 [제작자 저장소](https://github.com/iwantanid/SeochoBatang-Font)의 SIL Open Font License 1.1을 따릅니다. 전문은 `licenses/SeochoBatang-OFL.txt`에 포함합니다. 사용자 작성 코드에 새로운 오픈소스 라이선스를 임의로 부여하지 않았습니다.
