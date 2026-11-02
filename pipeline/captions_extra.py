# captions_extra_vlm.jsonl + dataset_extra/zonas.json -> dataset_extra/<img>.txt con el nombre de la zona tras el prefijo,
# para poder invocar cada zona desde el prompt ("Rock Tunnel", "Team Rocket Hideout"...).
import os, json, re
RUIDO = re.compile(r'\btext\b|\btexts\b|\breads?\b|caption|message|dialog|subtitle|pok[eé]mon go|gotta|labeled|legible|lettering|"', re.I)
here = os.path.dirname(os.path.abspath(__file__))
PREFIJO = "lgpestyle, Pokémon Let's Go Pikachu Eevee overworld, high-angle 3/4 view, "
ZONA = {
 'tunel_roca': 'Rock Tunnel, a dim rocky cave with a sandy floor',
 'mt_moon': 'Mt. Moon, a rocky cave with a sandy floor',
 'calle_victoria': 'Victory Road, a rocky cave with stone pillars, boulders and torches',
 'torre_pokemon': 'Pokémon Tower of Lavender Town, a haunted tower with gravestones and purple mist',
 'casino': 'Celadon Game Corner, a casino with slot machines',
 'cueva_diglett': "Diglett's Cave, an earthy tunnel",
 'ss_anne': 'S.S. Anne, a luxury cruise ship',
 'guarida_rocket': 'Team Rocket Hideout, a secret underground base with arrow spinner tiles',
 'silph': 'Silph Co., a modern office building',
 'gym_azafran': 'Saffron City Gym, a neon psychic gym at night above the city skyline',
 'central_energia': 'Power Plant, an abandoned industrial facility with generators and pipes',
 'islas_espuma': 'Seafoam Islands, an icy cave with frozen water and fog',
 'mansion_canela': 'Pokémon Mansion on Cinnabar Island, a burned ruined mansion',
 'gym_verde': 'Viridian City Gym, a dark gym with arrow spinner tiles',
}
EXTERIORES = {1822, 2069, 2070, 2071, 2072, 6863, 6866, 6257, 6258, 6720}  # fuera del edificio: sin etiqueta de zona
zonas = json.load(open(os.path.join(here, 'dataset_extra', 'zonas.json')))
n = 0
for e in map(json.loads, open(os.path.join(here, 'captions_extra_vlm.jsonl'), encoding='utf-8')):
    img = os.path.basename(e['image_path'].replace(chr(92), '/'))
    c = ' '.join(e['caption'].split()).rstrip('.')
    # fuera frases sobre texto en pantalla (dialogos o letras inventadas); 'textures' no cuenta
    c = ' '.join(f for f in re.split(r'(?<=[.!?"])\s+', c) if not RUIDO.search(f)).rstrip('.')
    assert c, img
    z = '' if int(img[-10:-4]) in EXTERIORES else ZONA[zonas[img]] + ', '
    open(os.path.join(here, 'dataset_extra', img[:-4] + '.txt'), 'w', encoding='utf-8').write(PREFIJO + z + c[0].lower() + c[1:] + '.')
    n += 1
assert n == len(zonas), (n, len(zonas))
print(n, 'captions')
