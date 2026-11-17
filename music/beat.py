# 곡의 빠르기와 첫 박 위치 → bgm.beat ("BPM 첫박ms")
import sys, librosa
y, sr = librosa.load(sys.argv[1], sr=22050)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
t = float(tempo[0] if hasattr(tempo, '__len__') else tempo)
first = librosa.frames_to_time(beats[:1], sr=sr)[0] * 1000 if len(beats) else 0
open(sys.argv[2], 'w').write('%.2f %d' % (t, first))
print(sys.argv[2], '%.2f BPM, 첫 박 %d ms' % (t, first))
