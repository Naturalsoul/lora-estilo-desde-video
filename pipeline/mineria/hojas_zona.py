# Hojas por zona para elegir frames a mano. Zonas oscuras: todas las candidatas; resto: solo YES sin usar.
import os, json
from PIL import Image, ImageDraw
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
z = json.load(open(os.path.join(here, 'mineria', 'zonas.json')))
OSCURAS = {'tunel_roca', 'mt_moon', 'torre_pokemon', 'torre_pokemon_2', 'calle_victoria', 'cueva_diglett'}
CLARAS = {'guarida_rocket', 'silph', 'ss_anne', 'mansion_canela', 'casino', 'central_energia', 'islas_espuma', 'gym_azafran', 'gym_verde'}
si = {os.path.basename(e['image_path']) for e in map(json.loads, open(os.path.join(here, 'vlm_filtro.jsonl'), encoding='utf-8')) if e['caption'].strip().upper().startswith('YES')}
ds = set(os.listdir(os.path.join(here, 'dataset')))
cs = sorted(os.listdir(os.path.join(here, 'candidatas')))
out = os.path.join(here, 'mineria', 'zonas'); os.makedirs(out, exist_ok=True)
W, H, C, R = 200, 112, 12, 10
for k in sorted(OSCURAS | CLARAS):
    a, b = z[k]
    fs = [c for c in cs if a <= int(c[-10:-4]) <= b and c not in ds and (k in OSCURAS or c in si)]
    for h in range(0, len(fs), C * R):
        sh = Image.new('RGB', (C * W, R * H), 'black'); d = ImageDraw.Draw(sh)
        for i, f in enumerate(fs[h:h + C * R]):
            x, y = (i % C) * W, (i // C) * H
            sh.paste(Image.open(os.path.join(here, 'candidatas', f)).convert('RGB').resize((W - 4, H - 4)), (x + 2, y + 2))
            d.text((x + 5, y + 4), f[-10:-4].lstrip('0'), fill='yellow', stroke_width=2, stroke_fill='black')
        sh.save(os.path.join(out, f'{k}_{h // (C * R)}.jpg'), quality=80)
    print(k, len(fs))
