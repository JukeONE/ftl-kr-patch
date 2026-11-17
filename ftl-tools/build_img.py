# 중국어 칸 현지화 이미지(img/loc-zh-Hans/*) 40장을 한글로 새로 그림
# 색은 원래 이미지에서 뽑고, 글씨는 갈무리(OFL) 픽셀 폰트로 그린다.
import os, collections
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
SRC='/home/claude/work/new/img/loc-zh-Hans/'; OUT='/home/claude/work/out/img/loc-zh-Hans/'
FB='/home/claude/work/fontsrc/Galmuri11-Bold.ttf'; F14='/home/claude/work/fontsrc/Galmuri14.ttf'; F11='/home/claude/work/fontsrc/Galmuri11.ttf'

def palette(im):
    px=list(im.convert('RGBA').get_flattened_data()) if hasattr(im,'get_flattened_data') else list(im.convert('RGBA').getdata())
    op=collections.Counter(p[:3] for p in px if p[3]>=250).most_common(3)
    semi=[p for p in px if 40<p[3]<200]
    glow=tuple(sum(p[i] for p in semi)//len(semi) for i in range(3)) if semi else None
    return [c for c,_ in op], glow

def mask(text, font, size, scale):
    f=ImageFont.truetype(font,size)
    l,t,r,b=f.getbbox(text)
    m=Image.new('1',(r-l+2,b-t+2),0); ImageDraw.Draw(m).text((1-l,1-t),text,font=f,fill=1)
    m=m.convert('L')
    if scale>1: m=m.resize((m.width*scale,m.height*scale),Image.NEAREST)
    return m.crop(m.getbbox())

def dil(m,n): return m.filter(ImageFilter.MaxFilter(2*n+1))
def ero(m,n): return m.filter(ImageFilter.MinFilter(2*n+1))

def layer(size, m, pos, color, alpha=255):
    L=Image.new('RGBA',size,(0,0,0,0))
    a=Image.new('L',size,0); a.paste(m,pos)
    if alpha!=255: a=a.point(lambda v:v*alpha//255)
    L.paste(Image.new('RGBA',size,color+(255,)),(0,0),a); return L

def compose(parts, pad=8, glow=None, glow_r=3, glow_a=150, gap=4, align='center'):
    # parts: [(mask, style, colors)]  style: hollow / outline / soft
    w=max(m.width for m,_,_ in parts)+pad*2
    h=sum(m.height for m,_,_ in parts)+gap*(len(parts)-1)+pad*2
    im=Image.new('RGBA',(w,h),(0,0,0,0)); y=pad; allm=Image.new('L',(w,h),0); layers=[]
    for m,style,cols in parts:
        x=(w-m.width)//2 if align=='center' else pad
        if style=='hollow':      # 밝은 테두리 + 안쪽 어두운 색
            layers.append(layer((w,h),m,(x,y),cols[0]))
            inner=ero(m,1)
            layers.append(layer((w,h),inner,(x,y),cols[1]))
        elif style=='outline':   # 밝은 글씨 + 어두운 외곽선
            a=Image.new('L',(w,h),0); a.paste(m,(x,y)); o=dil(a,1 if m.height<20 else 2)
            L=Image.new('RGBA',(w,h),(0,0,0,0)); L.paste(Image.new('RGBA',(w,h),cols[1]+(255,)),(0,0),o); layers.append(L)
            layers.append(layer((w,h),m,(x,y),cols[0]))
        else:                    # soft: 글씨만
            layers.append(layer((w,h),m,(x,y),cols[0]))
        allm.paste(m,(x,y),m); y+=m.height+gap
    if glow:
        g=dil(allm,2).filter(ImageFilter.GaussianBlur(glow_r)).point(lambda v:min(255,v*glow_a//110))
        G=Image.new('RGBA',(w,h),glow+(0,)); G.putalpha(g); im=Image.alpha_composite(im,G)
    for L in layers: im=Image.alpha_composite(im,L)
    return im

def save(rel, im):
    p=OUT+rel; os.makedirs(os.path.dirname(p),exist_ok=True); im.save(p,optimize=True)

MENU={'continue':'이어하기','start':'새 게임','tutorial':'튜토리얼','stats':'기록','options':'설정','credits':'제작진','quit':'종료'}
for k,t in MENU.items():
    for st in ('on','off','select2'):
        rel='main_menus/%s_%s.png'%(k,st); cols,glow=palette(Image.open(SRC+rel))
        c=cols[0]; dark=tuple(int(v*0.30) for v in c)
        save(rel, compose([(mask(t,FB,11,3),'outline',(c,dark))], pad=8, glow=glow or c, glow_a=80))

PAUSE={'pause_crewselection':('승무원 선택','드래그해서 승무원 여러 명을 선택합니다'),
 'pause_doors':('문 조작','클릭하거나 드래그해서 문을 여닫습니다'),
 'pause_hacking':('해킹','선실을 클릭해 해킹 드론을 보냅니다'),
 'pause_mind':('정신 지배','적을 클릭해 일시적으로 전향시킵니다'),
 'pause_roomselection':('선실 선택','선실을 클릭해 목적지를 정합니다'),
 'pause_target':('조준','선실을 클릭해 목표를 정합니다'),
 'pause_target_beam':('조준','클릭 후 드래그해서 목표 지역을 정합니다'),
 'pause_teleport_arrive':('텔레포트','적 함선의 선실을 클릭해 그 안의 승무원을 데려옵니다'),
 'pause_teleport_leave':('텔레포트','적 함선의 선실을 클릭해 강습조를 보냅니다'),
 'autopause':('자동 일시정지','동작이 끝나면 게임이 재개됩니다')}
for k,(t,s) in PAUSE.items():
    rel=k+'.png'; cols,glow=palette(Image.open(SRC+rel))
    light=max(cols,key=sum); dark=min(cols,key=sum)
    save(rel, compose([(mask(t,FB,11,3),'outline',(light,dark)),(mask(s,F14,14,1),'outline',(light,dark))], pad=9, glow=glow, glow_a=170, gap=7))

for rel in ('Text_pause1.png','Text_pause2.png','ipad/pause.png'):
    cols,glow=palette(Image.open(SRC+rel)); light=max(cols,key=sum); dark=min(cols,key=sum)
    save(rel, compose([(mask('일시정지',FB,11,3),'outline',(light,dark))], pad=9, glow=glow, glow_a=170 if '2' not in rel else 110))

for rel,t in (('numbers/text_miss.png','빗나감'),('numbers/text_resist.png','저항')):
    cols,glow=palette(Image.open(SRC+rel)); light=max(cols,key=sum); dark=min(cols,key=sum)
    save(rel, compose([(mask(t,FB,11,2),'outline',(light,dark))], pad=3))

for rel,t,sc in (('map/map_fuel_text_nofuel.png','연료 없음',5),('map/map_fuel_text_waiting.png','대기 중...',3)):
    z=Image.open(SRC+rel); cols,glow=palette(z); c=cols[0] if cols else glow
    px=[p for p in z.convert('RGBA').get_flattened_data() if p[3]>200]; c=collections.Counter(p[:3] for p in px).most_common(1)[0][0]
    save(rel, compose([(mask(t,F11,11,sc),'soft',(c,))], pad=10, glow=glow, glow_r=4, glow_a=140))

rel='customizeUI/advanced_warning.png'; z=Image.open(SRC+rel); cols,glow=palette(z)
save(rel, compose([(mask('확장팩 콘텐츠를',FB,11,2),'soft',(cols[0],)),(mask('켜야 쓸 수 있습니다',FB,11,2),'soft',(cols[0],))], pad=8, glow=glow, glow_a=120, gap=8))

# 불러오는 중: 원래 이미지의 막대는 그대로 두고 글씨만 교체
rel='main_menus/Loading_main.png'; z=Image.open(SRC+rel).convert('RGBA'); cols,glow=palette(z)
a=z.getchannel('A'); rows=[sum(1 for x in range(z.width) if a.getpixel((x,y))>250) for y in range(z.height)]
bar_top=next(y for y in range(z.height) if rows[y]>z.width*0.8)
txt=compose([(mask('불러오는 중',FB,11,3),'outline',(max(cols,key=sum),min(cols,key=sum)))], pad=8, glow=glow, glow_a=150)
new=Image.new('RGBA',(max(z.width,txt.width),txt.height+(z.height-bar_top)+6),(0,0,0,0))
bar=z.crop((0,bar_top-3,z.width,z.height)); new.alpha_composite(bar,((new.width-z.width)//2,txt.height+3))
new.alpha_composite(txt,((new.width-txt.width)//2,0)); save(rel,new)

n=sum(len(fs) for _,_,fs in os.walk(OUT)); print('images',n, 'bar_top',bar_top)
# 비교 시트
names=sorted(os.path.relpath(os.path.join(r,f),OUT) for r,_,fs in os.walk(OUT) for f in fs)
show=[x for x in names if not x.endswith(('_off.png','_select2.png'))]+['main_menus/start_off.png','main_menus/start_select2.png']
sheet=Image.new('RGBA',(1150,60+sum(max(Image.open(OUT+x).height,Image.open(SRC+x).height)+8 for x in show)//2+400),(34,36,54,255)); x0=0;y=5;i=0
half=(len(show)+1)//2
for col in range(2):
    y=5
    for x in show[col*half:(col+1)*half]:
        k=Image.open(OUT+x); zz=Image.open(SRC+x).convert('RGBA')
        sheet.alpha_composite(k,(col*575+5,y)); sheet.alpha_composite(zz,(col*575+330,y)); y+=max(k.height,zz.height)+8
sheet.crop((0,0,1150,1000)).save('/home/claude/work/kosheet.png')
for x in show[:6]: print(x, Image.open(OUT+x).size, Image.open(SRC+x).size)
