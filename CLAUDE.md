# 김쥬크 설치기 — 작업 규칙 (Claude가 먼저 읽을 것)

사용자(김쥬크)의 한글패치용 주크박스 설치기 기본틀. 답변과 안내는 모두 한국어로.

## 빌드 — 반드시 지킬 것
- 빌드는 **`NAME=게임이름_KR_v1.0 sh tools/build.sh`** 한 가지로만 한다. mcs를 직접 부르지 말 것.
- 빌드 스크립트가 하는 일:
  1. .NET Framework 4.8 **참조 어셈블리**(`/usr/lib/mono/4.8-api`)를 찾아서 그것만으로 컴파일 (`-nostdlib`)
  2. 빌드 후 `tools/check.cs`로 Windows .NET Framework 4.8에 없는 API를 쓰는지 검사
  3. 검사에 걸리면 exe를 지우고 실패로 끝남
- 참조 어셈블리가 없다고 멈추면 설치부터: 우분투 `sudo apt-get install -y mono-devel` (mono-mcs만으로는 부족), conda는 `conda install -c conda-forge mono`
- 끝에 **"API 검사 통과"**가 찍힌 exe만 사용자에게 보낸다.

### 왜 이렇게 하나 (실제로 겪은 오류)
- 2026-11 다크 메시아 설치기: 우분투 apt의 mono(참조 어셈블리 없음)로 빌드했더니 `"...".Split(' ')`가
  mono 전용 `string.Split(char, StringSplitOptions)`에 연결됨 → **Windows에서 실행해도 창도 오류도 없이 바로 꺼짐.**
- 증상이 "실행했는데 무반응"이면 가장 먼저 이 검사를 돌려 볼 것:
  `mono build/check/check.exe build/이름.exe /usr/lib/mono/4.8-api`
- 코드에서도 오버로드가 갈리는 호출은 피한다. 예: `Split(' ')` 대신 `Split(new[] { ' ' })`

## 리눅스에서 미리 띄워 보기 (선택)
- `apt-get install -y xvfb libgdiplus` 후 `Xvfb :99 &` → `DISPLAY=:99 mono build/이름.exe`
- 창 그리기는 Windows 전용 user32 함수라 `GetDC` EntryPointNotFound가 나면 정상(그 전 단계까지 통과했다는 뜻).

## 저장소 구조와 규칙
- 게임별로 고칠 곳은 `installer/GameConfig.cs`와 `patch/` 폴더뿐. 게임별 작업은 브랜치(예: `dark-messiah`)로 하고 `main`은 기본틀로 유지.
- 공개 저장소에는 게임 원본 파일을 올리지 않는다.
- 화면 안에 제작자 표기는 넣지 않는다 (간판에 KIM JUKE / 김쥬크가 있음). 배포 zip 이름에도 닉네임은 넣지 않아도 됨.
- 배경음은 **항상 Pixabay 곡 "Psychedelic Blues Rock Instrumental"(nickpanek)** 으로 한다 (`music/bgm_psych.*`).
  - 음원 mp3는 저장소에 넣지 않는다(설치기 exe 안에만 포함). 빌드 전에 `sh tools/getbgm.sh`로 받아 온다.
  - 직접 만든 칩튠(`music/bgm.*`)은 사용자가 따로 말할 때만: `BGM=chiptune`
- 화면 제목(`GameConfig.ScreenTitle`)이 스피커 아이콘에 닿으면 **글씨를 줄인다**. `MainForm.DrawScreen`이 자동으로 줄이므로 제목을 줄여 쓰거나 스피커를 옮기지 말 것.
