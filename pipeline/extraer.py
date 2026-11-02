# Longplays de YouTube -> frames candidatos para la LoRA de estilo LGPE.
#   python extraer.py descargar | frames | filtrar   (sin argumento: las tres)
# descargar: video sin audio con yt-dlp (via uvx) en videos/
# frames:    solo keyframes (mejor calidad del stream), uno cada >=SEG s, bajados a 1920 de ancho, recorte de marca de agua
# filtrar:   descarta negros/blancos, borrosos y casi-duplicados -> candidatas/ ; puntajes en filtro.csv
import os, sys, glob, shutil, subprocess
import numpy as np
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
# id, formato yt-dlp, pixeles a recortar abajo (tras escalar a 1920x1080)
VIDEOS = [
    ('0xTJPB6WwKY', '315', 72),   # 4K60, marca "@Kouteshi" abajo a la derecha
    ('35UNESZJ3bE', '137', 0),    # 1080p Switch original
]
SEG = 4          # separacion minima entre frames extraidos
BLUR_MIN = 40    # varianza del laplaciano (a 960px); menos = borroso o fundido
DUP_DIST = 6     # distancia de Hamming del dHash 64-bit; <= esto = duplicado


def descargar():
    os.makedirs(os.path.join(here, 'videos'), exist_ok=True)
    for vid, fmt, _ in VIDEOS:
        if glob.glob(os.path.join(here, 'videos', vid + '.*')):
            continue
        subprocess.run(['uvx', 'yt-dlp', '--js-runtimes', 'node', '-f', fmt, '-o',
                        os.path.join(here, 'videos', '%(id)s.%(ext)s'),
                        'https://www.youtube.com/watch?v=' + vid], check=True)


def frames():
    for vid, _, crop in VIDEOS:
        src = glob.glob(os.path.join(here, 'videos', vid + '.*'))
        out = os.path.join(here, 'frames', vid)
        if not src or os.path.isdir(out):
            continue
        os.makedirs(out + '.tmp')
        vf = (f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{SEG})',"
              f"scale=1920:1080:flags=lanczos,crop=1920:{1080 - crop}:0:0")
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-stats', '-skip_frame', 'nokey', '-i', src[0],
                        '-vf', vf, '-fps_mode', 'vfr', os.path.join(out + '.tmp', '%06d.png')], check=True)
        os.rename(out + '.tmp', out)  # carpeta final solo si ffmpeg termino


def dhash(g):
    s = np.asarray(Image.fromarray(g).resize((9, 8), Image.BILINEAR), dtype=np.int16)
    return np.packbits(s[:, 1:] > s[:, :-1])


def filtrar():
    dst = os.path.join(here, 'candidatas')
    os.makedirs(dst, exist_ok=True)
    rows, kept = ['archivo,brillo,nitidez,motivo'], []
    for f in sorted(glob.glob(os.path.join(here, 'frames', '*', '*.png'))):
        im = Image.open(f).convert('L')
        g = np.asarray(im.resize((960, im.height * 960 // im.width)), dtype=np.float32)
        lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
        brillo, nitidez = g.mean(), lap.var()
        h = dhash(g.astype(np.uint8))
        if not 25 < brillo < 235:
            motivo = 'negro/blanco'
        elif nitidez < BLUR_MIN:
            motivo = 'borroso'
        elif kept and np.unpackbits(np.bitwise_xor(np.array(kept), h), axis=1).sum(1).min() <= DUP_DIST:
            motivo = 'duplicado'
        else:
            motivo = ''
            kept.append(h)
            vid = os.path.basename(os.path.dirname(f))
            shutil.copy(f, os.path.join(dst, f'{vid}_{os.path.basename(f)}'))
        rows.append(f'{os.path.relpath(f, here)},{brillo:.0f},{nitidez:.0f},{motivo}')
    open(os.path.join(here, 'filtro.csv'), 'w').write('\n'.join(rows))
    print(f'{len(kept)} candidatas de {len(rows) - 1} frames')


if __name__ == '__main__':
    pasos = sys.argv[1:] or ['descargar', 'frames', 'filtrar']
    for p in pasos:
        globals()[p]()
