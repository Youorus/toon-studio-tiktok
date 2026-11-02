"""Chemins du studio et lecture des clés (fichier .env du studio, puis .env de Postly)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NICHES = ROOT / 'niches'
SHARED = ROOT / 'shared'
DATA = ROOT / 'data'
CACHE = DATA / 'cache'
FONTS = SHARED / 'fonts'
SFX = SHARED / 'sfx'
POSTLY_ENV = Path(os.environ.get('TOON_KEYS_ENV', ROOT.parent / 'postly_tiktok' / '.env'))

W, H, FPS = 1080, 1920, 30          # format vertical TikTok


def _read_env(path: Path) -> dict:
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def key(name: str, required: bool = True) -> str | None:
    """Clé d'API : environnement, .env du studio, puis .env de Postly (avec ou sans préfixe POSTLY_)."""
    local, postly = _read_env(ROOT / '.env'), _read_env(POSTLY_ENV)
    for source in (os.environ, local, postly):
        for n in (name, 'POSTLY_' + name):
            if source.get(n):
                return source[n]
    if required:
        raise SystemExit(f'Clé {name} introuvable : ajoute-la dans {ROOT / ".env"}')
    return None
