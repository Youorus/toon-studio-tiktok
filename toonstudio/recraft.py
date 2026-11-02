"""Client Recraft avec garde-fou de budget.

Chaque appel payant :
  1. est d'abord cherché dans le cache (même requête = même résultat, jamais payé deux fois) ;
  2. est refusé si la dépense cumulée dépasserait le budget (RECRAFT_BUDGET_USD, 21 $ par défaut, soit ~20 €) ;
  3. est inscrit dans data/recraft-depenses.jsonl (date, action, prix, fichier produit).

Tarifs : https://www.recraft.ai/docs/api-reference/pricing (relevés le 2/11/2026, 1 $ = 1 000 unités API).
"""
import base64, hashlib, json, time
from datetime import datetime
from pathlib import Path

import requests

from .config import CACHE, DATA, key

BASE = 'https://external.api.recraft.ai/v1'
LEDGER = DATA / 'recraft-depenses.jsonl'

# Prix par image (USD)
PRICES = {
    ('generate', 'recraftv4_1'): .035, ('generate', 'recraftv4_1_vector'): .08,
    ('generate', 'recraftv4_styles'): .035, ('generate', 'recraftv4_styles_vector'): .05,
    ('generate', 'recraftv4_1_flash'): .007,
    ('generate', 'recraftv3'): .04, ('generate', 'recraftv3_vector'): .08,
    ('image_to_image', 'recraftv3'): .04, ('image_to_image', 'recraftv3_vector'): .08,
    ('create_style', None): .005, ('remove_background', None): .01, ('vectorize', None): .01,
}
STYLE_REF_EXTRA = .005


def spent() -> float:
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(line)['usd'] for line in LEDGER.read_text().splitlines() if line.strip())


def budget() -> float:
    return float(key('RECRAFT_BUDGET_USD', required=False) or 21)


def _guard(cost: float, what: str):
    if spent() + cost > budget() + 1e-9:
        raise SystemExit(f'Budget Recraft atteint : {spent():.3f} $ dépensés sur {budget():.2f} $ ; « {what} » ({cost:.3f} $) refusé.')


def _log(action: str, usd: float, detail: dict):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open('a') as f:
        f.write(json.dumps({'date': datetime.now().isoformat(timespec='seconds'), 'action': action, 'usd': round(usd, 4), **detail},
                           ensure_ascii=False) + '\n')


def _headers():
    return {'Authorization': f'Bearer {key("RECRAFT_API_TOKEN")}'}


def _cache_path(payload: dict, files: list[Path]) -> Path:
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode())
    for f in files:
        h.update(Path(f).read_bytes())
    return CACHE / 'recraft' / h.hexdigest()[:24]


def _post(path: str, data: dict, files: list[tuple[str, Path]] | None = None) -> dict:
    for attempt in range(3):
        if files:
            parts = [(name, (Path(p).name, Path(p).read_bytes())) for name, p in files]
            form = {k: (json.dumps(v) if isinstance(v, (dict, list)) else str(v)) for k, v in data.items()}
            r = requests.post(BASE + path, headers=_headers(), data=form, files=parts, timeout=420)
        else:
            r = requests.post(BASE + path, headers=_headers(), json=data, timeout=420)
        if r.status_code < 500:
            break
        time.sleep(3 * (attempt + 1))
    if r.status_code >= 400:
        raise RuntimeError(f'Recraft {path} {r.status_code} : {r.text[:400]}')
    return r.json()


def _save_images(resp: dict, out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, item in enumerate(resp.get('data', [resp.get('image', {})])):
        if item.get('b64_json'):
            raw = base64.b64decode(item['b64_json'])
        else:
            raw = requests.get(item['url'], timeout=120).content
        ext = '.svg' if raw.lstrip().startswith(b'<') else '.png'
        p = out_dir / f'{stem}{"" if i == 0 else f"-{i + 1}"}{ext}'
        p.write_bytes(raw)
        paths.append(p)
    return paths


def generate(prompt: str, out: Path, model: str = 'recraftv4_1', n: int = 1, size: str = '1024x1024',
             style_id: str | None = None, style_refs: list[Path] | None = None, colors: list[tuple] | None = None,
             background: tuple | None = None, seed: int | None = None) -> list[Path]:
    """Génère n images ; renvoie les fichiers écrits (out = chemin sans extension)."""
    payload = {'prompt': prompt, 'model': model, 'n': n, 'size': size, 'response_format': 'b64_json'}
    if model.endswith('_vector') is False:
        payload['image_format'] = 'png'
    if style_id:
        payload['style_id'] = style_id
    if seed is not None:
        payload['random_seed'] = seed
    controls = {}
    if colors:
        controls['colors'] = [{'rgb': list(c)} for c in colors]
    if background:
        controls['background_color'] = {'rgb': list(background)}
    if controls:
        payload['controls'] = controls
    refs = [Path(p) for p in (style_refs or [])]
    cached = _cache_path(payload, refs)
    if cached.exists():
        return _restore(cached, Path(out))
    cost = PRICES.get(('generate', model), .08) * n + (STYLE_REF_EXTRA if refs else 0)
    _guard(cost, f'génération {Path(out).name}')
    try:
        resp = _post('/images/generations', payload, [('style_references', p) for p in refs] if refs else None)
    except requests.exceptions.Timeout:
        # Recraft facture souvent une génération même si la réponse n'arrive pas : on la note pour garder le budget juste
        _log('generate (délai dépassé, image perdue)', cost, {'model': model, 'n': n, 'prompt': prompt[:160], 'fichier': str(out)})
        raise
    files = _save_images(resp, cached, 'image')
    _log('generate', cost, {'model': model, 'n': n, 'prompt': prompt[:160], 'fichier': str(out), 'style_id': resp.get('style_id')})
    if resp.get('style_id'):
        (cached / 'style_id.txt').write_text(resp['style_id'])
    return _restore(cached, Path(out))


def create_style(images: list[Path], style: str = 'any', model: str = 'recraftv4_styles') -> str:
    """Enregistre un style maison à partir de 1 à 10 images de référence ; renvoie son identifiant."""
    payload = {'style': style, 'model': model}
    cached = _cache_path(payload, images)
    if (cached / 'style_id.txt').exists():
        return (cached / 'style_id.txt').read_text().strip()
    _guard(PRICES[('create_style', None)], 'création de style')
    resp = _post('/styles', payload, [('files', p) for p in images])
    cached.mkdir(parents=True, exist_ok=True)
    (cached / 'style_id.txt').write_text(resp['id'])
    _log('create_style', PRICES[('create_style', None)], {'style_id': resp['id'], 'images': [str(p) for p in images]})
    return resp['id']


def _tool(action: str, path: str, image: Path, out: Path, extra: dict | None = None, model: str | None = None) -> Path:
    payload = {'action': action, **(extra or {})}
    cached = _cache_path(payload, [image])
    if not cached.exists():
        cost = PRICES[(action, model)]
        _guard(cost, f'{action} {Path(image).name}')
        resp = _post(path, {**(extra or {}), 'response_format': 'b64_json'}, [('file' if action != 'image_to_image' else 'image', image)])
        _save_images(resp, cached, 'image')
        _log(action, cost, {'source': str(image), 'fichier': str(out)})
    return _restore(cached, Path(out))[0]


def remove_background(image: Path, out: Path) -> Path:
    return _tool('remove_background', '/images/removeBackground', image, out)


def vectorize(image: Path, out: Path) -> Path:
    return _tool('vectorize', '/images/vectorize', image, out)


def image_to_image(image: Path, prompt: str, out: Path, strength: float = .5, model: str = 'recraftv3', style_id: str | None = None) -> Path:
    """Variante d'une image existante (même personnage, autre pose ou autre bras). strength : 0 = identique, 1 = libre."""
    extra = {'prompt': prompt, 'strength': strength, 'model': model}
    if style_id:
        extra['style_id'] = style_id
    return _tool('image_to_image', '/images/imageToImage', image, out, extra, model)


def _restore(cached: Path, out: Path) -> list[Path]:
    out.parent.mkdir(parents=True, exist_ok=True)
    res = []
    for i, src in enumerate(sorted(p for p in cached.iterdir() if p.name.startswith('image'))):
        dst = out.with_name(out.stem + ('' if i == 0 else f'-{i + 1}') + src.suffix)
        dst.write_bytes(src.read_bytes())
        res.append(dst)
    return res


def account() -> dict:
    r = requests.get(BASE + '/users/me', headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()
