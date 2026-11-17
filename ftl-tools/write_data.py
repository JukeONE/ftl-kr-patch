import json,re,unicodedata
ko=json.load(open('/home/claude/work/ko_final.json')); en=json.load(open('/home/claude/work/map.json'))['en']
zh=open('/home/claude/work/new/data/text-zh-Hans.xml',encoding='utf-8').read()
crlf='\r\n' in zh
def strip_acc(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn') if any(ord(c)>126 for c in s) else s
seen=set(); stats=dict(ko=0,en=0,kept=0)
def rep(m):
    k=m.group(1); seen.add(k)
    if k in ko: stats['ko']+=1; v=ko[k]
    elif k in en: stats['en']+=1; v=strip_acc(en[k])
    else: stats['kept']+=1; return m.group(0)
    return '<text name="%s" language="zh-Hans">%s</text>'%(k,v)
out=re.sub(r'<text name="([^"]+)" language="zh-Hans">(.*?)</text>',rep,zh,flags=re.S)
extra=[k for k in en if k not in seen]
print(stats,'en keys not in zh file:',extra)
if extra:
    add=''.join('<text name="%s" language="zh-Hans">%s</text>%s'%(k,ko.get(k,strip_acc(en[k])),'\r\n' if crlf else '\n') for k in extra)
    out=out.replace('</FTL>',add+'</FTL>')
open('/home/claude/work/out/data/text-zh-Hans.xml','w',encoding='utf-8',newline='').write(out)
# 검증: XML로 읽히는지
import xml.etree.ElementTree as ET
t=ET.fromstring(out.encode('utf-8')); print('xml ok',len(t))
left=[c for c in set(out) if '一'<=c<='鿿']; print('남은 한자',len(left), ''.join(left)[:50])

# names.xml: 중국어 칸 이름 목록을 기본(영어) 이름으로
n=open('/home/claude/work/new/data/names.xml',encoding='utf-8').read()
lists=list(re.finditer(r'<nameList race="human" sex="(male|female)"( language="([^"]+)")?>(.*?)</nameList>',n,re.S))
base={'male':[],'female':[]}
for m in lists:
    if not m.group(3): base[m.group(1)]+=re.findall(r'<name[^>]*>.*?</name>',m.group(4))
print({k:len(v) for k,v in base.items()},[(m.group(1),m.group(3),len(re.findall('<name',m.group(4)))) for m in lists if m.group(3) in (None,'zh-Hans','ja')])
nl='\r\n' if '\r\n' in n else '\n'
def rep2(m):
    if m.group(3)!='zh-Hans': return m.group(0)
    return '<nameList race="human" sex="%s" language="zh-Hans">%s\t%s%s</nameList>'%(m.group(1),nl,(nl+'\t').join(base[m.group(1)]),nl)
n2=re.sub(r'<nameList race="human" sex="(male|female)"( language="([^"]+)")?>(.*?)</nameList>',rep2,n,flags=re.S)
open('/home/claude/work/out/data/names.xml','w',encoding='utf-8',newline='').write(n2)
print(len(n),len(n2), len([c for c in n2 if '一'<=c<='鿿' ]))
sec=re.search(r'<nameList race="human" sex="female" language="zh-Hans">.*?</nameList>',n2,re.S).group(0); print(sec[:200])
