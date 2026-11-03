"""Voix et bruitages ElevenLabs, avec cache (une réplique identique n'est jamais payée deux fois).

tts() renvoie le fichier audio et le minutage de chaque caractère : il sert aux sous-titres mot à mot et aux bouches.
Les indications de jeu entre crochets ([chuchote], [rit], [paniqué]…) sont dites par la voix mais retirées des sous-titres.
"""
import base64, hashlib, json, re, subprocess
import os
from functools import lru_cache
from pathlib import Path

import requests

from .config import CACHE, key

MODEL = 'eleven_v4'
VOICES = Path(__file__).resolve().parents[2] / 'dr-mia' / 'studio' / 'config' / 'voices.json'


def voice_ids() -> dict:
    path=Path(key('TOON_VOICES_CONFIG',required=False) or VOICES)
    return json.loads(path.read_text())['archetypes']


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def take_key(archetype, text, stability, seed):
    return _h([archetype, text, stability, seed])


@lru_cache(maxsize=4)
def _recorded_takes(index):
    return json.loads(index.read_text())


def tts(archetype: str, text: str, stability: float | None = None, seed: int = 7) -> dict:
    if manifest := os.environ.get('TOON_PRISES_INDEX'):
        index=Path(manifest).resolve()
        take=_recorded_takes(index).get(take_key(archetype,text,stability,seed))
        if take is None:
            raise ValueError(f'Prise absente de l’archive pour {archetype}.')
        return {'audio':index.parent/take['audio'],
                'alignment':json.loads((index.parent/take['alignement']).read_text())}
    v = voice_ids()[archetype]
    body = {'text': text, 'model_id': MODEL, 'language_code': 'fr', 'seed': seed,
            'voice_settings': {'stability': v['stability'] if stability is None else stability, 'similarity_boost': v['similarity']}}
    base = CACHE / 'voix' / _h({'v': v['voiceId'], 'b': body})
    if not base.with_suffix('.json').exists():
        r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{v["voiceId"]}/with-timestamps?output_format=mp3_44100_192',
                          headers={'xi-api-key': key('ELEVENLABS_API_KEY'), 'Content-Type': 'application/json'}, json=body, timeout=180)
        if r.status_code >= 400:
            raise RuntimeError(f'ElevenLabs voix {r.status_code} : {r.text[:300]}')
        j = r.json()
        base.parent.mkdir(parents=True, exist_ok=True)
        base.with_suffix('.mp3').write_bytes(base64.b64decode(j['audio_base64']))
        base.with_suffix('.json').write_text(json.dumps(j.get('alignment') or j.get('normalized_alignment')))
    al = json.loads(base.with_suffix('.json').read_text())
    return {'audio': base.with_suffix('.mp3'), 'alignment': al}


def sfx(prompt: str, seconds: float) -> Path:
    out = CACHE / 'bruitages' / (_h({'p': prompt, 's': seconds}) + '.mp3')
    if not out.exists():
        r = requests.post('https://api.elevenlabs.io/v1/sound-generation', headers={'xi-api-key': key('ELEVENLABS_API_KEY')},
                          json={'text': prompt, 'duration_seconds': seconds, 'prompt_influence': .6}, timeout=180)
        if r.status_code >= 400:
            raise RuntimeError(f'ElevenLabs bruitage {r.status_code} : {r.text[:300]}')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
    return out


def words_and_visemes(al: dict, tempo: float = 1.0):
    """Mots (texte, début, fin) et visèmes (temps, forme) à partir de l'alignement, sans les [indications]."""
    table = [('aàâ', 'A'), ('eéèêëiîïy', 'E'), ('oôuùûœ', 'O'), ('mbp', 'M'), ('fv', 'F')]
    words, vis, cur, tag = [], [], None, False
    for ch, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        s, e = s / tempo, e / tempo
        if ch == '[':
            tag = True; continue
        if ch == ']':
            tag = False; continue
        if tag:
            continue
        if ch.isspace():
            if cur:
                words.append(cur); cur = None
            continue
        cur = [cur[0] + ch, cur[1], e] if cur else [ch, s, e]
        if ch.isalpha():
            v = next((v for chars, v in table if ch.lower() in chars), 'E')
            if not vis or vis[-1][1] != v:
                vis.append((s, v))
    if cur:
        words.append(cur)
    return [tuple(w) for w in words if re.search(r'\w', w[0])], vis


def duration(path: Path) -> float:
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def strip_tags(text: str) -> str:
    return re.sub(r'\s*\[[^\]]*\]\s*', ' ', text).strip()
