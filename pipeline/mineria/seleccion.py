# Copia la seleccion manual (hojas de mineria/zonas) a dataset_extra/ y anota la zona de cada frame.
# "recorte": frames con cuadro de dialogo -> se guarda solo la parte de arriba (sin el texto).
import os, json
from PIL import Image
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
z = json.load(open(os.path.join(here, 'mineria', 'zonas.json')))
MANUAL = {
 'tunel_roca': [2411,2423,2449,2458,2480,2502,2536,2566,2590,2592,2625,2651,2652,2654,2676,2692],
 'mt_moon': [710,727,739,745,747,758,767,777,778,779,790,791,792,794,795,801,816,817,846,847,848,852,853,866,885,886,896,917,949,950],
 'calle_victoria': [7604,7605,7621,7633,7634,7636,7639,7641,7643,7644,7689,7690,7691,7720,7721,7722,7723,7763,7783,7784,7787,7788,7789,7790,7794,7795,7796,7798,7841,7864,7865,7867,7868,7869,7871,7892],
 'torre_pokemon': [2792,2793,2794,2817,2838,2841,2844,3956,3957,4009,4010,4047,4057,4059,4127,4179,4180,4210],
 'casino': [3531],
}
RECORTE = {
 'tunel_roca': [2450,2451,2524,2565,2603,2653,2694,2708],
 'mt_moon': [726,728],
 'calle_victoria': [7602,7640,7780,7785,7791,7793,7799,7819,7870],
 'torre_pokemon': [2795,2797,2818,2839,2840,3958,3959,3960,3968,3972,4030,4072,4106,4107,4148,4161,4164,4211,4213,4214],
 'casino': [3526,3527,3529,3530,3540],
}
# zonas claras: YES del VLM sin usar, menos vistas de combate/UI vistas en las hojas
EXCLUIR = {3546,3577,3623,3662,3663, 5542,5589,5612,5712,5714,5746,5767,5791,5826,5827,5930,6025,6065,
           1903,1925,1928,1954,1965,1969,2036,2061, 6612,6613,6615, 6233, 7443,7456,7504,7509}
CLARAS = {'guarida_rocket': 1, 'silph': 2, 'ss_anne': 1, 'mansion_canela': 1, 'central_energia': 1,
          'islas_espuma': 2, 'gym_azafran': 1, 'gym_verde': 1, 'cueva_diglett': 1}  # valor = tomar 1 de cada N
si = {os.path.basename(e['image_path']) for e in map(json.loads, open(os.path.join(here, 'vlm_filtro.jsonl'), encoding='utf-8')) if e['caption'].strip().upper().startswith('YES')}
ds = set(os.listdir(os.path.join(here, 'dataset')))
nombre = lambda i: f'0xTJPB6WwKY_{i:06d}.png'
for k, (a, b) in z.items():
    if k in CLARAS:
        fs = [int(c[-10:-4]) for c in sorted(si) if a <= int(c[-10:-4]) <= b and c not in ds and int(c[-10:-4]) not in EXCLUIR]
        MANUAL[k] = fs[::CLARAS[k]]
MANUAL['torre_pokemon'] += []
out = os.path.join(here, 'dataset_extra'); os.makedirs(out, exist_ok=True)
zona, n = {}, 0
for k, ids in list(MANUAL.items()) + [(k + '#r', v) for k, v in RECORTE.items()]:
    for i in ids:
        f = nombre(i); assert os.path.exists(os.path.join(here, 'candidatas', f)), f
        im = Image.open(os.path.join(here, 'candidatas', f))
        if k.endswith('#r'):
            im = im.crop((0, 0, 1920, 780))  # el cuadro de dialogo empieza ~y 790
        im.save(os.path.join(out, f)); zona[f] = k.split('#')[0]; n += 1
json.dump(zona, open(os.path.join(out, 'zonas.json'), 'w'), indent=0)
import collections; print(n, dict(collections.Counter(zona.values())))
