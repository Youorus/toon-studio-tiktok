"""Ligne de commande du studio : python -m toonstudio <commande> …  (voir README.md)."""
import argparse, sys
from pathlib import Path

import yaml

from .config import NICHES, ROOT


def cmd_budget(a):
    from . import recraft
    print(f'Recraft : {recraft.spent():.3f} $ dépensés sur un budget de {recraft.budget():.2f} $')
    if a.compte:
        print('Compte :', recraft.account())


def cmd_decor(a):
    from . import gemini
    niche = yaml.safe_load((NICHES / a.niche / 'niche.yaml').read_text())
    out = NICHES / a.niche / 'decors' / f'{a.nom}.png'
    gemini.image(f'{a.description}. {niche["style_decor"]}', out)
    print('Décor :', out.relative_to(ROOT))


def cmd_organe(a):
    """Crée un personnage d'une seule couche (organe, objet) : image -> détourage -> personnage.yaml -> aperçu."""
    from PIL import Image
    from .drawing import remove_flat_background
    from .rig import auto_setup_organ
    niche = yaml.safe_load((NICHES / a.niche / 'niche.yaml').read_text())
    folder = NICHES / a.niche / 'personnages' / a.nom
    folder.mkdir(parents=True, exist_ok=True)
    raw = folder / 'source.png'
    prompt = f'{a.description}. {niche["style_personnage"]}'
    if a.source == 'recraft':
        from . import recraft
        r = niche.get('recraft', {})
        files = recraft.generate(prompt, folder / 'source', model=r.get('modele', 'recraftv4_1'), style_id=r.get('style_id'))
        raw = files[0]
    else:
        from . import gemini
        gemini.image(prompt + ', centered, isolated on a plain pure white background', raw, aspect='1:1', fit=None)
    img = remove_flat_background(Image.open(raw))
    img.thumbnail((900, 900), Image.LANCZOS)
    img.save(folder / 'corps.png')
    cfg = auto_setup_organ(folder / 'corps.png', a.nom.replace('-', ' ').capitalize())
    (folder / 'personnage.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    cmd_apercu(argparse.Namespace(perso=str(folder)))


def cmd_apercu(a):
    """Planche de contrôle : le personnage dans toutes ses émotions, repères visibles."""
    from PIL import Image, ImageDraw
    from . import rig
    from .face import EMOTIONS
    ch = rig.load(Path(a.perso))
    tiles = []
    for emo in EMOTIONS:
        img, anchor = ch.render(emo=emo)
        img.thumbnail((360, 420), Image.LANCZOS)
        t = Image.new('RGBA', (380, 470), (118, 196, 206, 255))
        t.alpha_composite(img, ((380 - img.width) // 2, 440 - img.height))
        ImageDraw.Draw(t).text((10, 8), emo, fill='black')
        tiles.append(t)
    sheet = Image.new('RGBA', (380 * 7, 470 * 2), 'white')
    for i, t in enumerate(tiles):
        sheet.alpha_composite(t, ((i % 7) * 380, (i // 7) * 470))
    out = Path(a.perso) / 'apercu.jpg'
    sheet.convert('RGB').save(out, quality=90)
    print('Aperçu :', out)


def _kit(niche):
    k = yaml.safe_load((NICHES / niche / 'kit.yaml').read_text())
    subs = {'{sans_visage}': k['sans_visage'], '{fond_blanc}': k['fond_blanc']}

    def prompt(item):
        p = item['prompt']
        for x, y in subs.items():
            p = p.replace(x, y)
        return f"{p}. {k['style']}"
    return k, prompt


def cmd_kit(a):
    """Génère une étape du kit Recraft. Sans --lancer : affiche seulement ce qui serait généré et le prix."""
    from . import recraft
    k, prompt = _kit(a.niche)
    niche = yaml.safe_load((NICHES / a.niche / 'niche.yaml').read_text())
    style_id = (niche.get('recraft') or {}).get('style_id')
    items = [i for i in k[a.etape] if not a.seulement or i['nom'] in a.seulement]
    if a.etape == 'elements' and not style_id:
        raise SystemExit('Pas encore de style maison : lance d\'abord l\'étape « references », puis la commande « style ».')
    model = (niche.get('recraft') or {}).get('modele', 'recraftv4_1')
    cost = sum(recraft.PRICES[('generate', model)] * i.get('n', 1) for i in items)
    print(f'{len(items)} demandes, {sum(i.get("n", 1) for i in items)} images, environ {cost:.2f} $ '
          f'(déjà dépensé {recraft.spent():.2f} $ sur {recraft.budget():.2f} $)')
    if not a.lancer:
        for i in items:
            print(f'  - {i["nom"]} x{i.get("n", 1)}')
        print('Ajoute --lancer pour générer.')
        return
    out_dir = NICHES / a.niche / 'recraft' / a.etape
    for i in items:
        # le style maison vaut pour les organes et objets ; humains et décors : sans style imposé (sinon la peau prend la couleur des organes)
        kind = i.get('style', {'organe': 'maison', 'humain': 'humains'}.get(i.get('type'), 'aucun')) if a.etape == 'elements' else 'aucun'
        sid = {'maison': style_id, 'humains': (niche.get('recraft') or {}).get('style_humains')}.get(kind)
        colors = [c for c in k.get('palettes', {}).get(i['couleurs'], [])] if i.get('couleurs') else None
        files = recraft.generate(prompt(i), out_dir / i['nom'], model=model if sid else 'recraftv4_1', n=i.get('n', 1),
                                 size=i.get('ratio', '1:1'), style_id=sid,
                                 colors=[tuple(int(c.lstrip('#')[j:j + 2], 16) for j in (0, 2, 4)) for c in colors] if colors else None)
        print(f'  {i["nom"]} : ' + ', '.join(str(f.relative_to(ROOT)) for f in files))
    print(f'Total dépensé : {recraft.spent():.3f} $')


def cmd_style(a):
    """Enregistre le style maison à partir des images de référence choisies, et l'écrit dans niche.yaml."""
    from . import recraft
    sid = recraft.create_style([Path(p) for p in a.images])
    path = NICHES / a.niche / 'niche.yaml'
    cfg = yaml.safe_load(path.read_text())
    field = 'style_humains' if a.humains else 'style_id'
    text = path.read_text()
    old = (cfg.get('recraft') or {}).get(field)
    if field in text:
        text = text.replace(f'{field}: {old if old else "null"}', f'{field}: {sid}', 1)
    else:
        text = text.replace('  style_id:', f'  {field}: {sid}   # style des personnages humains\n  style_id:', 1)
    path.write_text(text)
    print('Style maison :', sid)


def cmd_choisir(a):
    """Installe un candidat Recraft : organe/objet -> personnage animable ; decor -> decors/ ; humain -> dossier à régler."""
    from PIL import Image
    from .drawing import remove_flat_background
    from .rig import auto_setup_organ
    src = Path(a.candidat)
    base = NICHES / a.niche
    if a.type == 'decor':
        from .drawing import cover
        cover(Image.open(src).convert('RGB')).save(base / 'decors' / f'{a.nom}.png')
        print('Décor :', base / 'decors' / f'{a.nom}.png'); return
    folder = base / 'personnages' / a.nom
    folder.mkdir(parents=True, exist_ok=True)
    img = remove_flat_background(Image.open(src), tol=30)
    img.thumbnail((900, 900) if a.type == 'organe' else (1100, 1100), Image.LANCZOS)
    img.save(folder / 'corps.png')
    from .rig import auto_setup_human
    setup = auto_setup_organ if a.type == 'organe' else auto_setup_human
    cfg = setup(folder / 'corps.png', a.nom.replace('-', ' ').capitalize())
    (folder / 'personnage.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    cmd_apercu(argparse.Namespace(perso=str(folder)))


def cmd_controle(a):
    from .episode import Episode
    ep = Episode(Path(a.episode))
    probs = ep.controle()
    print('\n'.join(probs) if probs else 'Aucun problème détecté.')
    print('Planche :', ep.folder / 'out' / 'controle.jpg')
    return probs


def cmd_rendu(a):
    if a.captionne:
        from .sous_titres import CaptionedEpisode
        ep = CaptionedEpisode(Path(a.episode))
    else:
        from .episode import Episode
        ep = Episode(Path(a.episode))
    print(f'« {ep.cfg["titre"]} » : {ep.duration:.1f} s, {len(ep.lines)} répliques')
    probs = ep.controle()
    if probs and not a.forcer:
        print('Contrôle de mise en scène : ' + str(len(probs)) + ' problème(s), rendu annulé (voir out/controle.jpg, ou --forcer) :')
        print('\n'.join('  - ' + p for p in probs)); return
    if a.captionne:
        ep.save_subtitles(ep.folder / 'out')
    print('Vidéo :', ep.render(preview_every=150))


def main(argv=None):
    p = argparse.ArgumentParser(prog='toonstudio')
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('budget', help='dépenses Recraft'); b.add_argument('--compte', action='store_true'); b.set_defaults(fn=cmd_budget)
    d = sub.add_parser('decor', help='générer un décor (Gemini)'); d.add_argument('niche'); d.add_argument('nom'); d.add_argument('description'); d.set_defaults(fn=cmd_decor)
    o = sub.add_parser('organe', help='créer un organe/objet animable'); o.add_argument('niche'); o.add_argument('nom'); o.add_argument('description')
    o.add_argument('--source', choices=['recraft', 'gemini'], default='recraft'); o.set_defaults(fn=cmd_organe)
    ap = sub.add_parser('apercu', help='planche des émotions d\'un personnage'); ap.add_argument('perso'); ap.set_defaults(fn=cmd_apercu)
    k = sub.add_parser('kit', help='générer une étape du kit Recraft'); k.add_argument('niche'); k.add_argument('etape', choices=['references', 'elements'])
    k.add_argument('--seulement', nargs='*'); k.add_argument('--lancer', action='store_true'); k.set_defaults(fn=cmd_kit)
    st = sub.add_parser('style', help='créer le style maison Recraft'); st.add_argument('niche'); st.add_argument('images', nargs='+')
    st.add_argument('--humains', action='store_true', help='style des personnages humains'); st.set_defaults(fn=cmd_style)
    c = sub.add_parser('choisir', help='installer un candidat Recraft'); c.add_argument('niche'); c.add_argument('candidat'); c.add_argument('nom')
    c.add_argument('--type', choices=['organe', 'humain', 'decor'], default='organe'); c.set_defaults(fn=cmd_choisir)
    r = sub.add_parser('rendu', help='rendre un épisode'); r.add_argument('episode'); r.add_argument('--forcer', action='store_true'); r.add_argument('--captionne', action='store_true', help='sous-titres synchronisés et badges des acteurs'); r.set_defaults(fn=cmd_rendu)
    ct = sub.add_parser('controle', help='contrôle de mise en scène (planche + problèmes)'); ct.add_argument('episode'); ct.set_defaults(fn=cmd_controle)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
