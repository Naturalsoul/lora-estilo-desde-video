# vlm_filtro.jsonl (YES/NO de Qwen2.5-VL sobre candidatas/) -> dataset/, sin los de descartes_manual.txt
# Ademas descarta fundidos (poco contraste) y ralea: max 1 frame cada GAP keyframes (~4 s c/u) para que
# zonas largas (Islas Espuma, rutas) no dominen el dataset.
import os, json, shutil
import numpy as np
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
GAP = 5            # ~20 s de juego entre frames elegidos
CONTRASTE_MIN = 25  # desvio de grises; fundidos a blanco dieron 15-22, niebla real 29+

si = sorted(os.path.basename(e['image_path']) for e in map(json.loads, open(os.path.join(here, 'vlm_filtro.jsonl'), encoding='utf-8'))
            if e['caption'].strip().upper().startswith('YES'))
malas = {w for l in open(os.path.join(here, 'descartes_manual.txt')) if not l.startswith('#') for w in l.split()}
dst = os.path.join(here, 'dataset')
os.makedirs(dst, exist_ok=True)
ultimo, n = {}, 0
for f in si:
    vid, idx = f[:-11], int(f[-10:-4])  # <video>_<000123>.png
    if idx - ultimo.get(vid, -GAP) < GAP:
        continue
    g = np.asarray(Image.open(os.path.join(here, 'candidatas', f)).convert('L').resize((480, 252)), dtype=np.float32)
    if g.std() < CONTRASTE_MIN:
        continue
    ultimo[vid] = idx
    if f[-10:-4] in malas:  # ocupa su lugar en el raleo: asi no entra en su reemplazo un frame sin revisar
        continue
    shutil.copy(os.path.join(here, 'candidatas', f), dst)
    n += 1
print(f'{n} imagenes en dataset/ (de {len(si)} aceptadas por el VLM)')
