# Hojas de contacto para revisar a ojo: python hoja.py <carpeta> [salida_prefijo]  (40 miniaturas por hoja, con nombre)
import os, sys, glob
from PIL import Image, ImageDraw

src = sys.argv[1]
pref = sys.argv[2] if len(sys.argv) > 2 else os.path.join(src, 'hoja')
fs = sorted(glob.glob(os.path.join(src, '**', '*.png'), recursive=True))
fs = [f for f in fs if not os.path.basename(f).startswith('hoja')]
W, H, COLS, N = 384, 216, 5, 40
for n in range(0, len(fs), N):
    lote = fs[n:n + N]
    s = Image.new('RGB', (W * COLS, H * ((len(lote) + COLS - 1) // COLS)))
    for i, f in enumerate(lote):
        x, y = (i % COLS) * W, (i // COLS) * H
        s.paste(Image.open(f).convert('RGB').resize((W, H)), (x, y))
        d = ImageDraw.Draw(s)
        d.rectangle((x, y, x + 200, y + 14), fill='black')
        d.text((x + 3, y + 2), os.path.relpath(f, src)[-32:], fill='yellow')
    s.save(f'{pref}_{n // N:03d}.png')
print((len(fs) + N - 1) // N, 'hojas')
