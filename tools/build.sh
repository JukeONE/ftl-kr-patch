#!/bin/sh
# 설치기 빌드 (mono의 mcs, .NET Framework 4.x 대상)
#   sh tools/build.sh            → patch/ 폴더 파일을 덮어쓰는 기본 방식
#   CECIL=1 sh tools/build.sh    → 코드 패치(Mono.Cecil 사용)일 때
#
# 중요: Windows의 .NET Framework 4.8 "참조 어셈블리"로 컴파일하고, 빌드 후 API 검사를
#       통과해야만 성공으로 끝난다. (mono 실제 라이브러리로 컴파일하면 Windows에 없는
#       mono 전용 API에 연결되어, 설치기가 Windows에서 아무 반응 없이 바로 꺼진다.
#       2026-11 다크 메시아 설치기에서 string.Split(char, StringSplitOptions) 때문에 실제로 발생.)
set -e
cd "$(dirname "$0")/.."

# ---- 1. .NET Framework 4.8 참조 어셈블리 찾기 (없으면 빌드 중단) -----------------
REF=""
for d in "$REFDIR" /usr/lib/mono/4.8-api "$CONDA_PREFIX/lib/mono/4.8-api" /opt/conda/lib/mono/4.8-api \
         /usr/lib/mono/4.7.2-api; do
  if [ -n "$d" ] && [ -f "$d/mscorlib.dll" ] && [ -f "$d/System.Windows.Forms.dll" ]; then REF="$d"; break; fi
done
if [ -z "$REF" ]; then
  echo "!! .NET Framework 4.8 참조 어셈블리(4.8-api)를 찾지 못했습니다. 빌드를 멈춥니다." >&2
  echo "   우분투: sudo apt-get install -y mono-devel   (mono-mcs만으로는 안 됨)" >&2
  echo "   conda : conda install -c conda-forge mono     (또는 REFDIR=경로 지정)" >&2
  exit 1
fi
echo "참조 어셈블리: $REF"

# ---- 2. patch.zip 만들기 -----------------------------------------------------------
mkdir -p build
rm -f build/patch.zip
if [ -z "$(cd patch && find . -type f ! -name '_*')" ]; then
  echo "!! patch/ 폴더에 넣을 파일이 없습니다. (밑줄로 시작하는 파일은 제외됨)" >&2; exit 1
fi
(cd patch && find . -type f ! -name '_*' | sed 's#^\./##' | zip -q -X ../build/patch.zip -@)

# ---- 2-1. 배경음 고르기 ---------------------------------------------------------------
# 기본: Pixabay 곡 "Psychedelic Blues Rock Instrumental"(nickpanek) = music/bgm_psych.*
#   음원(mp3)은 저장소에 넣지 않으므로 없으면 먼저  sh tools/getbgm.sh  로 받아 온다.
# 직접 만든 칩튠(music/bgm.*)으로 빌드하려면  BGM=chiptune
if [ "$BGM" = "chiptune" ]; then
  B=music/bgm
else
  B=music/bgm_psych
  if [ ! -f "$B.mp3" ]; then
    echo "!! 배경음 $B.mp3 가 없습니다. 먼저  sh tools/getbgm.sh  를 실행하세요." >&2
    echo "   (직접 만든 칩튠으로 빌드하려면 BGM=chiptune 을 붙이세요)" >&2
    exit 1
  fi
fi
echo "배경음: $B.mp3"

# ---- 3. 컴파일 (참조 어셈블리만 사용) ------------------------------------------------
NAME=${NAME:-KimJuke_Patch_Installer}
EXTRA=""
if [ "$CECIL" = "1" ]; then
  cp lib/Mono.Cecil.dll build/Mono.Cecil.dll
  EXTRA="-r:build/Mono.Cecil.dll -resource:build/Mono.Cecil.dll,Mono.Cecil.dll"
fi
mcs -nostdlib -noconfig -lib:"$REF" -lib:"$REF/Facades" \
  -r:mscorlib.dll -r:System.dll -r:System.Core.dll \
  -codepage:utf8 -target:winexe -optimize+ -win32icon:installer/juke.ico \
  -r:System.Windows.Forms.dll -r:System.Drawing.dll -r:System.IO.Compression.dll $EXTRA \
  -resource:installer/skin.png,skin.png -resource:build/patch.zip,patch.zip \
  -resource:$B.mp3,bgm.mp3 -resource:$B.env,bgm.env -resource:$B.beat,bgm.beat \
  installer/*.cs -out:build/$NAME.exe

# ---- 4. API 검사: Windows .NET Framework 4.8에 없는 함수를 쓰면 실패 ----------------
mkdir -p build/check
if [ ! -f build/check/check.exe ] || [ tools/check.cs -nt build/check/check.exe ]; then
  mcs -r:lib/Mono.Cecil.dll tools/check.cs -out:build/check/check.exe >/dev/null
  cp lib/Mono.Cecil.dll build/check/Mono.Cecil.dll
fi
if ! mono build/check/check.exe build/$NAME.exe "$REF"; then
  echo "!! .NET Framework 4.8에 없는 API를 쓰고 있습니다 (위 MISSING 목록). 이 exe는 Windows에서 바로 꺼집니다." >&2
  rm -f build/$NAME.exe
  exit 1
fi
echo "build/$NAME.exe  (API 검사 통과)"
