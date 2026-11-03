"""Allège vosk-model-small-fr-0.22 pour une grammaire de quelques mots : retire le grand modèle
de langue (Gr.fst) et ne garde que les mots utiles. Usage : build_model.py <dossier_modele> <sortie.tar.gz>"""
import os, shutil, struct, sys, tarfile, tempfile

KEEP = {'<eps>', '!SIL', '[unk]', '#0', '<s>', '</s>',
        'do', 'ré', 'mi', 'fa', 'sol', 'la', 'si', 'suivant'}


def symbols(path):
    b = open(path, 'rb').read()
    i = b.find(struct.pack('<i', 2125658996)) + 4
    n = struct.unpack_from('<i', b, i)[0]; i += 4 + n
    i += 8
    size = struct.unpack_from('<q', b, i)[0]; i += 8
    out = []
    for _ in range(size):
        n = struct.unpack_from('<i', b, i)[0]; i += 4
        s = b[i:i + n].decode('utf-8'); i += n
        out.append((s, struct.unpack_from('<q', b, i)[0])); i += 8
    return out


src, dst = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
slim = os.path.join(tmp, 'model')
shutil.copytree(src, slim)
syms = symbols(os.path.join(slim, 'graph', 'Gr.fst'))
kept = [(s, k) for s, k in syms if s in KEEP]
assert {'suivant', 'ré', 'sol'} <= {s for s, _ in kept}, kept
with open(os.path.join(slim, 'graph', 'words.txt'), 'w', encoding='utf-8', newline='\n') as f:
    for s, k in kept:
        f.write(f'{s} {k}\n')
os.remove(os.path.join(slim, 'graph', 'Gr.fst'))
if os.path.exists(os.path.join(slim, 'README')):
    os.remove(os.path.join(slim, 'README'))
with tarfile.open(dst, 'w:gz', compresslevel=9) as t:
    t.add(slim, arcname='model')
shutil.rmtree(tmp)
print(dst, round(os.path.getsize(dst) / 1e6, 1), 'Mo', len(kept), 'mots')
