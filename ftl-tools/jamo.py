# 구 한글패치(0.9.0)의 조합형 바이트 -> 유니코드
CHO = {0xA6:'ㄱ',0xA7:'ㄴ',0xA8:'ㄷ',0xA9:'ㄹ',0xAA:'ㅁ',0xAB:'ㅂ',0xAC:'ㅅ',0xAD:'ㅇ',0xAE:'ㅈ',0xAF:'ㅊ',0xB0:'ㅋ',0xB1:'ㅌ',0xB2:'ㅍ',0xB3:'ㅎ',0xDA:'ㅉ',0xDB:'ㅆ',0xDC:'ㅃ',0xDD:'ㄸ',0xDE:'ㄲ'}
JUNG = {0xB4:'ㅏ',0xB5:'ㅑ',0xB6:'ㅓ',0xB7:'ㅕ',0xB8:'ㅗ',0xB9:'ㅛ',0xBA:'ㅜ',0xBB:'ㅠ',0xBC:'ㅡ',0xBD:'ㅣ',0xBE:'ㅢ',0xBF:'ㅖ',0xC0:'ㅐ',0xC1:'ㅒ',0xC2:'ㅔ',0xC3:'ㅗ',0xC4:'ㅜ'}
JONG = {0xC5:'ㄱ',0xC6:'ㄴ',0xC7:'ㄷ',0xC8:'ㄹ',0xC9:'ㅁ',0xCA:'ㅂ',0xCB:'ㅅ',0xCC:'ㅇ',0xCD:'ㅈ',0xCE:'ㅊ',0xCF:'ㅋ',0xD0:'ㅌ',0xD1:'ㅍ',0xD2:'ㅎ',0xD3:'ㅀ',0xD4:'ㄶ',0xD5:'ㄺ',0xD6:'ㄻ',0xD7:'ㅄ',0xD8:'ㄲ',0xD9:'ㅆ',0xDF:'ㄼ',0xE0:'ㄵ'}
PUNC = {0xA0:' ',0xA1:'°',0xA2:'「',0xA3:'」',0xA4:'、',0xA5:'·'}
L='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
V='ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
T=[''] + list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')
COMB={('ㅗ','ㅏ'):'ㅘ',('ㅗ','ㅐ'):'ㅙ',('ㅗ','ㅣ'):'ㅚ',('ㅜ','ㅓ'):'ㅝ',('ㅜ','ㅔ'):'ㅞ',('ㅜ','ㅣ'):'ㅟ',('ㅡ','ㅣ'):'ㅢ'}
bad=[]
def decode(b):
    out=[]; i=0; n=len(b)
    while i<n:
        c=b[i]
        if c<0x80: out.append(chr(c)); i+=1; continue
        if c in CHO:
            cho=CHO[c]; i+=1; vs=[]
            while i<n and b[i] in JUNG and len(vs)<2: vs.append(JUNG[b[i]]); i+=1
            if not vs: out.append(cho); continue
            v=vs[0] if len(vs)==1 else COMB.get(tuple(vs))
            if v is None: bad.append(bytes(b[i-4:i+2])); v=vs[0]
            t=''
            if i<n and b[i] in JONG: t=JONG[b[i]]; i+=1
            out.append(chr(0xAC00+(L.index(cho)*21+V.index(v))*28+T.index(t)))
        elif c in PUNC: out.append(PUNC[c]); i+=1
        elif c in JUNG: out.append(JUNG[c]); i+=1
        elif c in JONG: out.append(JONG[c]); i+=1; bad.append(bytes(b[max(0,i-6):i+3]))
        elif 0x80<=c<0xA0 and c not in (0x81,0x8d,0x8f,0x90,0x9d):
            out.append(bytes([c]).decode('cp1252')); i+=1
        else: out.append('�'); bad.append(bytes(b[max(0,i-6):i+3])); i+=1
    return ''.join(out)
