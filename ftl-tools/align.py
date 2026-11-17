import re,glob,os,difflib,json,html
N='/home/claude/work/new/data/'; O='/home/claude/work/oldu/'
def rd(p): return open(p,encoding='utf-8',errors='replace').read().replace('\r\n','\n')
en={}; src={}
for f in sorted(glob.glob(N+'text_*.xml')):
    for m in re.finditer(r'<text name="([^"]+)"[^>]*>(.*?)</text>',rd(f),re.S):
        en[m.group(1)]=m.group(2); src[m.group(1)]=os.path.basename(f)
TAG=re.compile(r'<([A-Za-z_][\w]*)((?:\s+[\w:]+\s*=\s*"[^"]*")*)\s*(/?)>')
def toks(s):
    s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    out=[]
    for m in TAG.finditer(s):
        tag,attrs,sc=m.groups()
        a=dict(re.findall(r'([\w:]+)\s*=\s*"([^"]*)"',attrs))
        inner=None
        if not sc:
            e=s.find('<',m.end())
            if s.startswith('</'+tag,e): inner=s[m.end():e]
        out.append((tag,a,inner))
    return out
ko={}; conflicts=[]; unmatched=[]
def addctx(ts):
    ctx=''; out=[]
    for tag,a,inner in ts:
        if 'name' in a and tag in ('event','textList','eventList','ship','weaponBlueprint','droneBlueprint','augBlueprint','crewBlueprint','systemBlueprint','shipBlueprint','achievement','sectorDescription','itemBlueprint','blueprintList'): ctx=tag+':'+a['name']
        out.append((tag,a,inner,ctx))
    return out
def key(t):
    tag,a,inner,ctx=t
    return (tag, a.get('name') or a.get('load') or a.get('req') or '', ctx)
for f in sorted(glob.glob(N+'*.xml')):
    b=os.path.basename(f)
    if b.startswith('text') or not os.path.exists(O+b): continue
    nt=addctx(toks(rd(f)))
    if not any('id' in t[1] for t in nt): continue
    ot=addctx(toks(rd(O+b)))
    sm=difflib.SequenceMatcher(None,[key(t) for t in nt],[key(t) for t in ot],autojunk=False)
    matched=set()
    for i,j,n in sm.get_matching_blocks():
        for k in range(n):
            a=nt[i+k][1]; inner=ot[j+k][2]
            if 'id' in a and a['id'] in en:
                matched.add(i+k)
                if inner is None: continue
                inner=inner.strip()
                if a['id'] in ko and ko[a['id']]!=inner: conflicts.append((a['id'],ko[a['id']],inner))
                else: ko[a['id']]=inner
    for i,t in enumerate(nt):
        if 'id' in t[1] and t[1]['id'] in en and i not in matched: unmatched.append((b,t[1]['id']))
print('en',len(en),'ko mapped',len(ko),'conflicts',len(conflicts),'unmatched tokens',len(unmatched))
# misc.xml: 이름으로 직접
om={m.group(1):m.group(2) for m in re.finditer(r'<text name="([^"]+)"[^>]*>(.*?)</text>',rd(O+'misc.xml'),re.S)}
hit=0
for k,v in om.items():
    if k in en and k not in ko: ko[k]=v.strip(); hit+=1
print('misc by name',hit,'of',len(om),'not in new:',[k for k in om if k not in en][:40])
json.dump(dict(en=en,ko=ko,src=src,conflicts=conflicts,unmatched=unmatched),open('/home/claude/work/map.json','w'),ensure_ascii=False,indent=0)
import collections
hang=re.compile('[가-힣]')
st=collections.Counter()
for k in en:
    s=src[k]
    if k not in ko: st[s,'missing']+=1
    elif hang.search(ko[k]): st[s,'korean']+=1
    else: st[s,'nohangul']+=1
for k in sorted(st): print(k,st[k])
for c in conflicts[:8]: print('CONFLICT',c)
import random; random.seed(1)
for k in random.sample(sorted(ko),12): print(k,'|',en[k][:90],'|',ko[k][:90])
