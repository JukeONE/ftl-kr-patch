import json,re
m=json.load(open('/home/claude/work/map.json')); en,ko,src=m['en'],m['ko'],m['src']
O='/home/claude/work/oldu/'
tt=open(O+'tooltips.xml',encoding='utf-8').read()
n=0
for mm in re.finditer(r'<(\w+)>(.*?)</\1>',tt,re.S):
    k='tooltip_'+mm.group(1)
    if k in en: ko[k]=mm.group(2).strip(); n+=1
print('tooltips',n)
json.dump(ko,open('/home/claude/work/ko_auto.json','w'),ensure_ascii=False,indent=0)
hang=re.compile('[가-힣]')
om={x.group(1):x.group(2) for x in re.finditer(r'<text name="([^"]+)"[^>]*>(.*?)</text>',open(O+'misc.xml',encoding='utf-8').read(),re.S)}
print('--- old misc leftovers')
for k,v in om.items():
    if k not in en: print(k,'=',v.replace('\n','\\n'))
print('--- missing')
for k in en:
    if src[k]=='text_blueprints.xml': continue
    if k not in ko or not hang.search(ko[k]):
        print(src[k][5:9],k,'=',en[k].replace('\n','\\n'), ('' if k not in ko else ' ## '+ko[k].replace('\n','\\n')))
