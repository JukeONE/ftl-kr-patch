# 나눔고딕 Bold(OFL) -> 게임의 중국어 칸 폰트(black.ttf) 자리에 넣을 한글 폰트
# 세로 치수를 원래 폰트(SimHei) 비율에 맞추고, OFL 규정대로 이름을 바꾼다.
import json
from fontTools.ttLib import TTFont
src='/home/claude/work/fontsrc/NanumGothic-Bold.ttf'
ref=TTFont('/home/claude/work/new/fonts/zh-Hans/black.ttf')
f=TTFont(src)
upm=f['head'].unitsPerEm; r=ref['head'].unitsPerEm
print('before',upm,f['hhea'].ascent,f['hhea'].descent,f['hhea'].lineGap,f['OS/2'].sTypoAscender,f['OS/2'].sTypoDescender,f['OS/2'].usWinAscent,f['OS/2'].usWinDescent)
asc=round(ref['hhea'].ascent*upm/r); desc=round(ref['hhea'].descent*upm/r); gap=round(ref['hhea'].lineGap*upm/r)
f['hhea'].ascent=asc; f['hhea'].descent=desc; f['hhea'].lineGap=gap
o=f['OS/2']; o.sTypoAscender=asc; o.sTypoDescender=desc; o.sTypoLineGap=gap; o.usWinAscent=asc; o.usWinDescent=-desc
NEW='KJ FTL Gothic'
for n in f['name'].names:
    if n.nameID in (1,16): n.string=NEW
    elif n.nameID in (4,): n.string=NEW+' Bold'
    elif n.nameID==6: n.string='KJFTLGothic-Bold'
    elif n.nameID==3: n.string='KJFTLGothic-Bold;modified from NanumGothic Bold (SIL OFL 1.1)'
if 'DSIG' in f: del f['DSIG']
cm=f.getBestCmap()
ko=json.load(open('/home/claude/work/ko_final.json')); en=json.load(open('/home/claude/work/map.json'))['en']
need=set(c for v in list(ko.values())+list(en.values()) for c in v)|set(chr(i) for i in range(32,127))
names=open('/home/claude/work/new/data/names.xml',encoding='utf-8').read()
miss=sorted(c for c in need if ord(c) not in cm and c not in '\n\r\t')
print('missing glyphs',[(c,hex(ord(c))) for c in miss])
f.save('/home/claude/work/out/fonts/zh-Hans/black.ttf')
g=TTFont('/home/claude/work/out/fonts/zh-Hans/black.ttf'); print('after',g['hhea'].ascent,g['hhea'].descent,g['hhea'].lineGap,len(g.getBestCmap()))
gs=g.getGlyphSet(); 
from fontTools.pens.boundsPen import BoundsPen
for ch in '한글Ag':
    bp=BoundsPen(gs); gs[g.getBestCmap()[ord(ch)]].draw(bp); print(ch,bp.bounds)
rg=ref.getGlyphSet()
for ch in '继Ag':
    bp=BoundsPen(rg); rg[ref.getBestCmap()[ord(ch)]].draw(bp); print(ch,[round(x*upm/r) for x in bp.bounds], ref['hmtx'][ref.getBestCmap()[ord(ch)]][0]*upm/r)
