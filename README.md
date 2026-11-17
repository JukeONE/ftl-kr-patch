# FTL: Faster Than Light 한글패치

Steam판 **FTL: Faster Than Light 1.6.x**(확인한 버전: 1.6.14)용 한글패치입니다.

## 설치
1. [Releases](../../releases)에서 `FTL_KR_v1.0.zip`을 받아 압축을 풉니다.
2. 게임을 끈 상태에서 `FTL_KR_v1.0.exe`를 실행합니다. Steam 게임 폴더를 자동으로 찾습니다 (못 찾으면 **[폴더]**로 직접 고르세요).
3. **[설치]**를 누르고, 끝나면 **[실행]**으로 게임을 시작합니다.
   - 영어로 나오면: OPTIONS → Change Language → **한국어**

- **[복원]**을 누르면 게임 파일이 설치 전과 똑같이 돌아갑니다.
- 게임이 업데이트되거나 스팀에서 파일 무결성 확인을 하면 패치가 풀립니다. 그때는 **[설치]**를 다시 누르면 됩니다.
- 예전 1.5.x 버전(`resources/data.dat`이 있는 판)에는 쓸 수 없습니다.
- 설치 파일에는 게임 원본 데이터가 들어 있지 않습니다.
- 서명 없는 프로그램이라 Windows 경고가 뜨면 [추가 정보] → [실행]을 누르세요.
- 필요 환경: Windows 10/11 (.NET Framework 4.x 기본 포함)

## 원리
- 게임에 한국어 칸이 없어서 **중국어(간체, zh-Hans) 칸을 한국어로** 씁니다. 실행 파일은 건드리지 않습니다.
  - 글: `data/text-zh-Hans.xml`
  - 폰트: `fonts/zh-Hans/black.ttf` (나눔고딕 Bold의 세로 치수를 원래 폰트에 맞춘 것)
  - 그림: `img/loc-zh-Hans/*` 40장 (메인 메뉴·일시정지 등 그림으로 된 글씨)
  - 승무원 이름: 설치할 때 게임의 `data/names.xml`에서 중국어 칸 목록을 기본 이름으로 바꿔 넣음
- 위 자료를 `ftl.dat` **끝에 덧붙이고 목차만 고칩니다.** 복원은 목차를 되돌리고 파일을 원래 길이로 잘라 원본과 완전히 같게 만듭니다.
- `settings.ini`의 `language`를 `zh-Hans`로 맞춥니다 (복원 때 되돌림).
- 패치를 적용한 동안에는 중국어를 고를 수 없습니다.

## 번역
- 기존 한글패치 **FTL Advanced Edition 한글패치 0.9.0**(1.5.13용)의 번역문을 현재 버전의 글 번호에 맞춰 옮겼습니다. 원 번역에 참여하신 분들께 감사드립니다.
- 1.6에서 추가·변경된 메뉴, 단축키, 경고 문구, 도움말, 무기·드론 짧은 이름, 함급 등 약 750줄은 새로 번역했습니다 (`ftl-tools/ko_manual.py`).
- 전체 5,176줄 중 5,028줄이 한글이고, 나머지(키 이름, 제작진 이름, 터치 전용 문구)는 영어 그대로입니다.
- 오역이나 칸을 넘치는 글씨를 발견하면 [Issues](../../issues)에 알려 주세요.

## 저장소 구성
- `patch/` 게임에 들어가는 한글 자료 (글·폰트·그림)
- `installer/` 설치기 소스 (C# WinForms, 주크박스 창·패치 로직)
- `ftl-tools/` 구 한글패치 번역을 옮기고 폰트·그림을 만드는 스크립트
- `skin/`, `music/`, `lib/`, `tools/` 설치기 스킨·배경음 박자 자료·빌드 도구 (배경음 곡 파일은 포함하지 않음)
- `licenses/` 폰트 라이선스
- 빌드: `sh tools/getbgm.sh` → `NAME=FTL_KR_v1.0 sh tools/build.sh`

## 감사
- 원 번역: FTL Advanced Edition 한글패치 0.9.0 제작진
- 본문 폰트: 나눔고딕 (NAVER) — SIL Open Font License 1.1, 이름을 바꾼 수정본으로 포함
- 메뉴 그림 글씨: [갈무리](https://github.com/quiple/galmuri) — SIL Open Font License 1.1
- 배경음: "Psychedelic Blues Rock Instrumental" by nickpanek ([Pixabay](https://pixabay.com/)) — Pixabay Content License, 설치기 안에만 포함
- 원작: Subset Games
