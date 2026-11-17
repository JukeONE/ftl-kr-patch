#!/bin/sh
# 기본 배경음(Pixabay "Psychedelic Blues Rock Instrumental" - nickpanek) 받아 오기
#   음원은 저장소에 넣지 않고, 이미 배포한 Oxenfree 한글패치 설치기(v1.0) 안에 든 것을 꺼내 쓴다.
#   결과: music/bgm_psych.mp3  (박자 자료 bgm_psych.env / bgm_psych.beat 는 저장소에 있음)
# 필요: gh(저장소 JukeONE/oxenfree-kr-patch 접근), mono + mcs
#   곡 파일을 직접 갖고 있으면:  cp 곡.mp3 music/bgm_psych.mp3  (128kbps 변환본)
set -e
cd "$(dirname "$0")/.."
[ -f music/bgm_psych.mp3 ] && { echo "이미 있음: music/bgm_psych.mp3"; exit 0; }
mkdir -p build/getbgm
ID=$(gh api repos/JukeONE/oxenfree-kr-patch/releases/tags/v1.0 --jq '.assets[] | select(.name=="Oxenfree_KR_v1.0.exe") | .id')
gh api "repos/JukeONE/oxenfree-kr-patch/releases/assets/$ID" -H "Accept: application/octet-stream" > build/getbgm/ox.exe
cp lib/Mono.Cecil.dll build/getbgm/Mono.Cecil.dll
mcs -r:lib/Mono.Cecil.dll tools/getbgm.cs -out:build/getbgm/getbgm.exe >/dev/null
mono build/getbgm/getbgm.exe build/getbgm/ox.exe music/bgm_psych.mp3
if ! cmp -s build/getbgm/bgm.env music/bgm_psych.env; then echo "!! 꺼낸 곡의 박자 자료가 저장소 것과 다릅니다." >&2; rm -f music/bgm_psych.mp3; exit 1; fi
echo "music/bgm_psych.mp3 준비 완료"
