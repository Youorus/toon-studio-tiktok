"""Décors (et images de test) par Gemini Image. Mis en cache : une même demande ne coûte qu'une fois.

Les images Gemini portent un marquage IA invisible (SynthID) : TikTok peut afficher la mention « IA ».
Pour les personnages et organes définitifs, on passe par Recraft (style maison, voir docs/RECRAFT.md).
"""
import base64, hashlib, io, json, time
from pathlib import Path

import requests
from PIL import Image

from .config import CACHE, key
from .drawing import cover

MODEL = 'gemini-3-pro-image'
URL = 'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent'


def image(prompt: str, out: Path, aspect: str = '9:16', refs: list[Path] | None = None, fit: tuple | None = (1080, 1920)) -> Path:
    refs = [Path(r) for r in (refs or [])]
    h = hashlib.sha256(json.dumps([prompt, aspect, MODEL]).encode())
    for r in refs:
        h.update(r.read_bytes())
    cached = CACHE / 'gemini' / (h.hexdigest()[:24] + '.png')
    if not cached.exists():
        parts = [{'text': prompt}] + [{'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(r.read_bytes()).decode()}} for r in refs]
        body = {'contents': [{'role': 'user', 'parts': parts}],
                'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': aspect, 'imageSize': '2K'}}}
        for attempt in range(4):
            r = requests.post(URL.format(m=MODEL), headers={'x-goog-api-key': key('GEMINI_API_KEY')}, json=body, timeout=300)
            if r.status_code < 500:
                break
            time.sleep(5 * (attempt + 1))
        r.raise_for_status()
        part = next((p for p in r.json()['candidates'][0]['content']['parts'] if 'inlineData' in p), None)
        if not part:
            raise RuntimeError('Gemini n\'a pas rendu d\'image')
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(base64.b64decode(part['inlineData']['data']))
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(cached).convert('RGB')
    (cover(img, *fit) if fit else img).save(out)
    return out
