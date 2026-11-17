# FTL: Faster Than Light 한글패치 (1.6.x) — 만드는 도구

`ftl` 브랜치는 김쥬크 설치기 틀에 FTL 한글패치를 얹은 것입니다. 빌드: `NAME=FTL_KR_v1.0 sh tools/build.sh`

## 방식
- 게임(1.6.14)에는 한국어 칸이 없어서 **중국어(zh-Hans) 칸을 한국어로** 씁니다. 실행 파일은 건드리지 않습니다.
  - 글: `patch/data/text-zh-Hans.xml` (5,176줄 중 5,028줄 한글, 나머지는 키 이름·제작진 이름 등 영어 유지)
  - 폰트: `patch/fonts/zh-Hans/black.ttf` = 나눔고딕 Bold를 원래 폰트 세로 치수에 맞추고 이름을 바꾼 것 (OFL)
  - 그림: `patch/img/loc-zh-Hans/*` 40장 = 갈무리 폰트(OFL)로 새로 그린 메뉴·일시정지 글씨
  - 승무원 이름: 설치할 때 게임의 `data/names.xml`에서 중국어 칸 목록을 기본 이름으로 바꿔 넣음
- 설치기(`installer/Patcher.cs`)는 위 파일을 `ftl.dat` 끝에 덧붙이고 목차만 고칩니다.
  복원은 목차를 되돌리고 파일을 원래 길이로 잘라서 원본과 완전히 같게 만듭니다.
- `settings.ini`의 `language`를 `zh-Hans`로 맞춥니다(복원 때 되돌림). 영어로 뜨면 OPTIONS → Change Language → 한국어.

## 번역 출처
- 바탕: 게임 폴더에 있던 구 한글패치 `FTL_Adv_Korean_Patch_0.9.0`(1.5.13용, 조합형 자체 인코딩)의 번역문을
  유니코드로 풀어(`jamo.py`) 1.6.14의 글 번호에 자동 대응(`align.py`). 배포할 때는 원 번역팀을 밝혀 주세요.
- 새로 번역: 1.6에서 추가·변경된 메뉴/단축키/경고/도움말, 무기·드론 짧은 이름, 함급 등 약 750줄 (`ko_manual.py`)

## 다시 만드는 순서 (경로는 스크립트 안의 /home/claude/work 기준)
1. `unpack.py` : ftl.dat과 구 패치 dat 풀기 → 2. `dec.py` : 구 패치 글을 유니코드로
3. `align.py` → `missing2.py` → `build_text.py` → `write_data.py` : 한글 글 파일 생성
4. `build_font.py`, `build_img.py` : 폰트·그림 생성 → 결과를 `patch/`에 복사

게임 원본 파일과 구 패치 파일은 이 저장소에 넣지 않습니다.
