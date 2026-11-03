"""Sous-titres sur les prises réelles et planches de contrôle Toon Studio."""
from bisect import bisect_right
import json
import re

from PIL import Image, ImageDraw

from toonstudio import cards, rig
from toonstudio.config import H, W
from toonstudio.drawing import clamp, cover, font
from toonstudio.episode import Episode

def caption_groups(words):
    group = []
    for word in words:
        if group and (len(group) >= 5 or re.search(r'[.!?]$', group[-1][0])):
            yield group
            group = []
        group.append(word)
    if group:
        yield group


def tokens(text):
    words = []
    for token in text.split():
        if words and not any(c.isalnum() for c in token):
            words[-1] += ' ' + token
        else:
            words.append(token)
    return words


def groups_for_line(line):
    actual = line.get('mots', [])
    groups = [tokens(text) for text in line.get('sous_titres', line['dit']).split('|')]
    def normalize(word):
        return ''.join(c for c in word.casefold() if c.isalnum())
    expected = [normalize(word) for group in groups for word in group]
    if expected != [normalize(word[0]) for word in actual]:
        return list(caption_groups(actual))
    aligned = iter(actual)
    return [[(word, start, end) for word, (_, start, end) in zip(group, aligned)] for group in groups]


def make_cues(lines):
    cues = []
    for line in lines:
        groups = groups_for_line(line)
        for i, group in enumerate(groups):
            start = line['t0'] + group[0][1]
            stop = line['t0'] + group[-1][2]
            limit = line['t0'] + groups[i + 1][0][1] if i + 1 < len(groups) else line['t1']
            stop = min(limit, max(start + 0.72, stop + 0.15))
            phrase = ' '.join(word[0] for word in group)
            cues.append({'debut': round(start, 3), 'fin': round(stop, 3), 'texte': phrase, 'voix': line['qui']})
    return cues


def srt_time(t):
    millis = round(t * 1000)
    secs, ms = divmod(millis, 1000)
    mins, sec = divmod(secs, 60)
    hr, minute = divmod(mins, 60)
    return f'{hr:02}:{minute:02}:{sec:02},{ms:03}'


class CaptionedEpisode(Episode):
    def __init__(self, folder):
        super().__init__(folder)
        style = self.niche.get('direction_artistique', {})
        if 'legendes_y' in style:
            self.cfg.setdefault('legendes_y', style['legendes_y'])
        self.mot_capitales = self.cfg.get('legendes_mode', style.get('legendes_mode')) == 'mot_capitales'
        if self.mot_capitales:
            self.words = [(line['t0']+a, line['t0']+b, text.strip('….,!?;:«»'))
                          for line in self.lines for text,a,b in line.get('mots', ())]
            self.word_starts = [start for start,_,_ in self.words]
        self.badge_xy = tuple(style.get('badge_organe_xy', (132, 305)))
        self.cues = make_cues(self.lines)
        self.cue_starts = [cue['debut'] for cue in self.cues]
        organs = {shot['organe'] for shot in self.shots if 'organe' in shot}
        badges = {organ: cards.organ_badge(organ) for organ in organs}
        self.organ_badges = {shot['id']: badges[shot['organe']] for shot in self.shots if 'organe' in shot}
        self.mini_badges = {}
        for shot in self.shots:
            if not shot.get('mini_badges'):
                continue
            lines = [line for line in self.lines if line['shot'] == shot['id']]
            labels = []
            for spec in shot['mini_badges']:
                index = spec.get('replique', 0)
                if spec['acteur'] not in shot['acteurs'] or not 0 <= index < len(lines):
                    raise ValueError(f"{shot['id']} : acteur ou réplique inconnus pour le mini-badge")
                start = lines[index]['t0'] + spec.get('delai', 0)
                end = min(start + spec.get('duree', 1.8), shot['t1'])
                badge = cards.actor_badge(spec['texte'], spec.get('fond', '#503467'), spec.get('point', '#D4A5ED'))
                if end <= start or badge.width > 768:
                    raise ValueError(f"{shot['id']} : durée ou largeur du mini-badge hors cadre")
                labels.append((spec, start, end, badge))
            self.mini_badges[shot['id']] = labels

    def _actor_labels(self, frame, shot, t, placed, view):
        labels = self.mini_badges.get(shot['id'])
        if not labels:
            return
        faces = {actor['name']: actor for actor in placed}
        left, top, right, bottom = view
        sx, sy = W / (right - left), H / (bottom - top)
        occupied = []
        for spec, start, end, badge in labels:
            actor = faces.get(spec['acteur'])
            if not actor or not start < t < end:
                continue
            fx, fy = actor['face']
            tx = round((fx - left) * sx)
            ty = round((fy - actor['face_r'] * .82 - top) * sy)
            if not (0 <= tx < W and 0 <= ty < H):
                continue
            dx, dy = spec.get('decalage', (0, -132))
            w, h = badge.size
            x = round(clamp(tx + dx - w / 2, 132, 900 - w))
            y = round(clamp(ty + dy, 395, self.cfg['legendes_y'] - 105 - h))
            if any(x < r and l < x + w and y < b and u < y + h for l, u, r, b in occupied):
                continue
            occupied.append((x, y, x + w, y + h))
            layer = Image.new('RGBA', frame.size)
            d = ImageDraw.Draw(layer)
            if tx < x or tx > x + w:
                pin = (x if tx < x else x + w, round(clamp(ty, y + 17, y + h - 17)))
            else:
                pin = (round(clamp(tx, x + 22, x + w - 22)), y if ty < y else y + h)
            d.line((pin, (tx, ty)), fill='#241D22', width=8)
            d.line((pin, (tx, ty)), fill='#FFF9ED', width=4)
            d.ellipse((tx-7, ty-7, tx+7, ty+7), fill=spec.get('point', '#D4A5ED'), outline='#FFF9ED', width=2)
            layer.alpha_composite(badge, (x, y))
            visibility = min(1, (t - start) / .13, (end - t) / .18)
            if visibility < 1:
                layer.putalpha(layer.getchannel('A').point(lambda a: round(a * visibility)))
            frame.alpha_composite(layer)
            if len(occupied) == 2:
                break

    def _caption(self, frame, line, t):
        if line['shot'] in self.organ_badges:
            frame.alpha_composite(self.organ_badges[line['shot']], self.badge_xy)
        if self.mot_capitales:
            self._caption_word(frame, line, t)
            return
        index = bisect_right(self.cue_starts, t) - 1
        if index < 0 or t >= self.cues[index]['fin']:
            return
        text = self.cues[index]['texte']
        d = ImageDraw.Draw(frame)
        f = font('Fredoka', 62)
        try:
            f.set_variation_by_name('SemiBold')
        except (OSError, ValueError):
            pass
        if d.textlength(text, font=f) > 620 and ' ' in text:
            words = text.split()
            options = [(' '.join(words[:i]), ' '.join(words[i:])) for i in range(1, len(words))]
            first, second = min(options, key=lambda pair: max(d.textlength(w, font=f) for w in pair))
            text = first + '\n' + second
        d.multiline_text((W / 2, self.cfg['legendes_y']), text, font=f, fill='#FFF9ED',
                         stroke_width=5, stroke_fill='#181313', anchor='mm', align='center', spacing=1)

    def _caption_word(self, frame, line, t):
        index = bisect_right(self.word_starts, t) - 1
        if index < 0:
            return
        _, end, word = self.words[index]
        if not word or t > end + .095:
            return
        text = word.upper()
        size = 91 if line['shot'] == 'cabinet' else 81
        width = font('LuckiestGuy', size).getlength(text)
        if width > 650:
            size = max(50, int(size * 650 / width))
        f = font('LuckiestGuy', size)
        d = ImageDraw.Draw(frame)
        x, y = W // 2, self.cfg['legendes_y']
        d.text((x+2,y+5), text, font=f, fill='#191517', anchor='mm',
               stroke_width=2, stroke_fill='#191517')
        d.text((x,y), text, font=f, fill='#FFFDF8', anchor='mm',
               stroke_width=1, stroke_fill='#272026')

    def save_subtitles(self, out):
        assert all(c['fin'] > c['debut'] for c in self.cues)
        assert all(a['fin'] <= b['debut'] for a, b in zip(self.cues, self.cues[1:]))
        text = '\n\n'.join(
            f"{i}\n{srt_time(c['debut'])} --> {srt_time(c['fin'])}\n{c['texte']}"
            for i, c in enumerate(self.cues, 1)
        )
        (out / 'sous-titres.srt').write_text(text + '\n')
        (out / 'sous-titres.json').write_text(json.dumps(self.cues, ensure_ascii=False, indent=2) + '\n')

    def preview(self, out, times):
        chars = {(s['id'], n): rig.load(self.path(a['perso'])) for s in self.shots for n, a in s['acteurs'].items()}
        self._chars = {n: c for (_, n), c in chars.items()}
        sheet = Image.new('RGB', (4 * 270, ((len(times) + 3) // 4) * 512), '#17232A')
        labels = ImageDraw.Draw(sheet)
        for i, t in enumerate(times):
            shot = next(s for s in self.shots if s['t0'] <= t < s['t1'])
            lines = [l for l in self.lines if l['shot'] == shot['id']]
            li = next(j for j, l in enumerate(lines) if l['t0'] <= t < l['t1'])
            line = lines[li]
            frame = cover(Image.open(self.path(shot['decor'])).convert('RGBA'))
            placed = self._place_actors(shot, lines, li, line, t, chars)
            for actor in placed:
                frame.alpha_composite(actor['img'], actor['pos'])
            frame, view = self._camera_frame(frame, shot, t)
            self._actor_labels(frame, shot, t, placed, view)
            if line.get('carte'):
                card = cards.draw(line['carte'], t - line['t0'], line['t1'] - line['t0'], self.palette)
                frame.alpha_composite(card, ((W - card.width) // 2, 430 - card.height // 2))
            self._caption(frame, line, t)
            self._watermark(frame, t)
            x, y = i % 4 * 270, i // 4 * 512
            sheet.paste(frame.convert('RGB').resize((270, 480), Image.Resampling.LANCZOS), (x, y))
            labels.text((x + 7, y + 486), f"{t:05.2f} s   {shot['id']}", fill='white', font=font('Fredoka', 17))
        sheet.save(out / 'planche-travail.jpg', quality=88)
