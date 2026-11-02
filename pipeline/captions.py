# captions_vlm.jsonl (descripciones de Qwen2.5-VL) -> dataset/<imagen>.txt con la palabra clave adelante
import os, json

here = os.path.dirname(os.path.abspath(__file__))
PREFIJO = "lgpestyle, Pokémon Let's Go Pikachu Eevee overworld, high-angle 3/4 view, "

n = 0
for e in map(json.loads, open(os.path.join(here, 'captions_vlm.jsonl'), encoding='utf-8')):
    img = os.path.basename(e['image_path'].replace('\\', '/'))  # rutas relativas al cwd de musubi
    c = ' '.join(e['caption'].split()).rstrip('.')
    assert c, img
    open(os.path.join(here, 'dataset', img[:-4] + '.txt'), 'w', encoding='utf-8').write(PREFIJO + c[0].lower() + c[1:] + '.')
    n += 1
print(n, 'captions')
