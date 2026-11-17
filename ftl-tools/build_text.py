import json,re,sys
sys.path.insert(0,'/home/claude/work/scripts')
from ko_manual import KO, SKIP
m=json.load(open('/home/claude/work/map.json')); en=m['en']
ko=json.load(open('/home/claude/work/ko_auto.json'))
hang=re.compile('[가-힣]')
final={}; issues=[]
ph=lambda s: sorted(re.findall(r'\\[0-9]',s))
for k,e in en.items():
    v=None
    if k in SKIP: continue
    if k in KO: v=KO[k]
    elif k in ko and hang.search(ko[k]): v=ko[k]
    if v is None: continue
    v=v.replace('\r','')
    if '\n' in v: v=re.sub(r'\s*\n\s*',' ',v)
    v=v.replace('/n','\\n') if '/n' in v and '\\n' in e else v
    if ph(v)!=ph(e): issues.append(('PLACEHOLDER',k,e,v))
    if e.count('\\n')!=v.count('\\n') and k not in KO: issues.append(('NEWLINE',k,e,v))
    if re.search(r'<|&(?!amp;|lt;|gt;|quot;|apos;|#)',v): issues.append(('XML',k,e,v))
    final[k]=v
unk=[k for k in KO if k not in en]
print('final',len(final),'of',len(en),'unknown manual keys',unk)
import collections
print(collections.Counter(i[0] for i in issues))
for i in issues:
    if i[0]!='NEWLINE': print(i)
for i in [x for x in issues if x[0]=='NEWLINE'][:12]: print(i)
json.dump(final,open('/home/claude/work/ko_final.json','w'),ensure_ascii=False,indent=0)
left=[k for k in en if k not in final]
print('left english',len(left)); print([k for k in left if not k.startswith(('keycap','credits','tutorial_','help_','paused_','warning_','name_'))])
