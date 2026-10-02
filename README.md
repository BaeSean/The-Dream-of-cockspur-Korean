# The Dream Of A Cockspur 한국어 패치

게임 설정에서 **English**를 선택하면 한국어로 표시됩니다. 번역: **여우불**. 서초바탕 글꼴을 사용합니다.

기존 완성 번역을 원본 게임 파일이 필요하도록 차분 패치로 재구성한 저장소입니다. 게임 실행 파일, 원본 게임 데이터, 수정된 게임 자산 전체, 추출 원문 데이터베이스, 세이브와 개인 백업은 포함하지 않습니다. 게임을 별도로 소유해야 합니다.

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

## 설치 준비

Windows PowerShell과 Python 3.8 이상이 필요합니다. Python 외 추가 패키지를 설치하지 않아도 됩니다. 저장소의 **Code → Download ZIP**으로 내려받고 쓰기 가능한 폴더에 압축을 푸십시오. GitHub Releases 배포는 이번 작업에 포함하지 않습니다.

게임을 종료하십시오. 기존 한글 패치가 있다면 그 패치의 복원 기능으로 원본 상태를 복원하십시오. Steam 파일 무결성 검사만으로 이전 패치가 추가한 파일까지 제거되지는 않습니다. 다른 버전·변경된 파일은 해시 검사에서 거부됩니다. 세이브는 설치기가 변경하지 않지만 중요한 세이브는 따로 백업해 두십시오.

저장소 폴더에서 다음 명령을 실행합니다. `D:\Games\TheDreamOfACockspur`는 실제 게임 설치 경로로 바꾸십시오.

```powershell
python tools/prepare.py --game-dir "D:\Games\TheDreamOfACockspur"
```

이 단계는 게임 파일을 읽고 차분을 적용하여 `.local-package`에 설치 파일을 재구성합니다. 게임 설치 폴더는 변경하지 않습니다. 33개 결과 파일의 SHA-256이 기존 검수 패치와 모두 같아야 완료됩니다.

## 설치·확인·복원

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

`.local-package` 안의 백업과 `install-state.json`은 복원에 필요하므로 삭제하거나 다른 컴퓨터에 공유하지 마십시오. 재구성된 폴더에는 전체 게임 자산이 있으므로 GitHub에도 올리지 마십시오. 스크립트 실행이 시스템 정책으로 차단되면 조직 정책을 우회하지 말고 허용된 실행 환경에서 진행하십시오.

## 저장소 구성

- `patches/`: 기존 게임 파일 25개에 대한 BSDIFF40 차분
- `runtime/`: 패치가 추가하는 한국어 이미지 7개와 자체 런타임 DLL 1개
- `manifest.json`: 지원 원본·결과·배포 파일 해시와 경로
- `tools/prepare.py`: 외부 의존성 없는 로컬 재구성 도구
- `tools/Apply-Patch.ps1`: 원본 검증, 백업, 설치 실패 시 복구, 제거 도구
- `docs/`: 번역 및 패키지 검증 결과
- `licenses/`: 포함된 글꼴의 라이선스

게임과 기존 그림의 권리는 각 원저작권자에게 있습니다. 비공식 번역 패치입니다. 서초바탕은 [제작자 저장소](https://github.com/iwantanid/SeochoBatang-Font)의 SIL Open Font License 1.1을 따릅니다. 전문은 `licenses/SeochoBatang-OFL.txt`에 포함합니다. 사용자 작성 코드에 새로운 오픈소스 라이선스를 임의로 부여하지 않았습니다.
