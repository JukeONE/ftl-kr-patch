#!/bin/sh
# 배경음 바꾸기: sh music/make_bgm.sh 원하는곡.mp3
# → music/bgm.mp3(128kbps), bgm.env(박자 지도), bgm.beat(빠르기·첫 박) 생성
set -e
cd "$(dirname "$0")"
ffmpeg -loglevel error -y -i "$1" -b:a 128k -ar 44100 bgm.mp3
python3 envelope.py bgm.mp3 bgm.env
python3 beat.py bgm.mp3 bgm.beat
