import sys; sys.path.insert(0, '/home/claude/work/scripts')
import ftldat, py7zr, collections
U='/mnt/user-data/uploads/FTL Faster Than Light/'
d, ents, hdr = ftldat.read_pkg(U+'ftl.dat')
print(hdr, len(ents))
print(collections.Counter(e['flags'] for e in ents))
files={}
for e in ents:
    try: files[e['name']] = ftldat.pkg_get(d, e)
    except Exception as ex: print('ERR', e, ex); break
ftldat.dump(files, '/home/claude/work/new')
print(ents[:3])
# sort order check
names=[e['name'] for e in ents]; hs=[e['hash'] for e in ents]
print('hash sorted', hs==sorted(hs), 'name sorted', names==sorted(names))
offs=[e['off'] for e in ents]; print('off sorted', offs==sorted(offs))
py7zr.SevenZipFile(U+'FTL_Adv_Korean_Patch_0.9.0.7z').extractall('/home/claude/work/oldpatch')
for f in ('data.dat','resource.dat'):
    o = ftldat.read_old('/home/claude/work/oldpatch/'+f)
    print(f, len(o)); ftldat.dump(o, '/home/claude/work/old')
