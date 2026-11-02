# Hojas de miniaturas de candidatas/ cada PASO frames, para ubicar zonas del longplay.
# Borde verde = YES del VLM, azul = ya en dataset/, sin borde = rechazada.
import os, sys, json
from PIL import Image, ImageDraw
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
paso = int(sys.argv[1]) if len(sys.argv) > 1 else 6
desde, hasta = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 10**9)
out = sys.argv[4] if len(sys.argv) > 4 else os.path.join(here, 'mineria', 'hojas')
os.makedirs(out, exist_ok=True)
si = {os.path.basename(e['image_path']) for e in map(json.loads, open(os.path.join(here, 'vlm_filtro.jsonl'), encoding='utf-8')) if e['caption'].strip().upper().startswith('YES')}
ds = set(os.listdir(os.path.join(here, 'dataset')))
fs = [f for f in sorted(os.listdir(os.path.join(here, 'candidatas'))) if desde <= int(f[-10:-4]) <= hasta][::paso]
W, H, C, R = 240, 135, 10, 8
for h in range(0, len(fs), C * R):
    sh = Image.new('RGB', (C * W, R * H), 'black')
    for i, f in enumerate(fs[h:h + C * R]):
        im = Image.open(os.path.join(here, 'candidatas', f)).convert('RGB').resize((W - 6, H - 6))
        x, y = (i % C) * W, (i // C) * H
        col = (40, 120, 255) if f in ds else (0, 200, 0) if f in si else (0, 0, 0)
        ImageDraw.Draw(sh).rectangle((x, y, x + W - 1, y + H - 1), fill=col)
        sh.paste(im, (x + 3, y + 3))
        ImageDraw.Draw(sh).text((x + 6, y + 5), f[-10:-4], fill='yellow', stroke_width=2, stroke_fill='black')
    sh.save(os.path.join(out, f'hoja_{fs[h][-10:-4]}.jpg'), quality=80)
print(len(fs), 'miniaturas')
