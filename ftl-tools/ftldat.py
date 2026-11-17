import struct, zlib, os, sys

def read_old(path):
    d = open(path, 'rb').read()
    n = struct.unpack_from('<I', d, 0)[0]
    out = {}
    for i in range(n):
        off = struct.unpack_from('<I', d, 4 + 4*i)[0]
        if off == 0: continue
        size, nl = struct.unpack_from('<II', d, off)
        name = d[off+8:off+8+nl].decode('utf-8', 'replace')
        out[name] = d[off+8+nl:off+8+nl+size]
    return out

def read_pkg(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'PKG\n'
    hs, es, cnt, psz = struct.unpack_from('>HHII', d, 4)
    ents = []
    pbase = hs + es*cnt
    for i in range(cnt):
        h, po, do, ds, us = struct.unpack_from('>IIIII', d, hs + es*i)
        flags = po >> 24; po &= 0xFFFFFF
        end = d.index(b'\0', pbase+po)
        name = d[pbase+po:end].decode('utf-8')
        ents.append(dict(hash=h, flags=flags, name=name, off=do, size=ds, usize=us))
    return d, ents, (hs, es, cnt, psz)

def pkg_get(d, e):
    raw = d[e['off']:e['off']+e['size']]
    if e['flags'] & 1:
        raw = zlib.decompress(raw, -15) if raw[:1] != b'\x78' else zlib.decompress(raw)
    return raw

def dump(files, outdir):
    for name, data in files.items():
        p = os.path.join(outdir, name)
        os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
        open(p, 'wb').write(data)
