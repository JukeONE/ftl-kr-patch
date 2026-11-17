import sys,glob,os,re,collections
sys.path.insert(0,'/home/claude/work/scripts'); import jamo
os.makedirs('/home/claude/work/oldu',exist_ok=True)
for f in sorted(glob.glob('/home/claude/work/old/data/*.xml'))+['/home/claude/work/old/data/credits.txt']:
    b=open(f,'rb').read()
    if b[:3]==b'\xef\xbb\xbf': b=b[3:]
    try: s=b.decode('utf-8')
    except: s=jamo.decode(b)
    open('/home/claude/work/oldu/'+os.path.basename(f),'w',encoding='utf-8',newline='').write(s)
print(len(jamo.bad), collections.Counter(jamo.bad).most_common(15))
s=open('/home/claude/work/oldu/events.xml',encoding='utf-8').read()
i=s.find('<event name="START_BEACON"'); print(s[i:i+900])
for w in ['앉','얹','끊','몫']: print(w, len(re.findall(w,''.join(open(g,encoding='utf-8').read() for g in glob.glob('/home/claude/work/oldu/*.xml')))))
