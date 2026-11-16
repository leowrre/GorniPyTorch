## ==============================================================================
## ОБЩИЕ ПОМОЩНИКИ ДЛЯ НОВЫХ МИНИ-ИГР (ПО ПРАВКАМ ГЕЙМДИЗАЙНЕРА)
##   mg_site.rpy    — сборка сайта техникума по образцу (вместо перезагрузки ПК)
##   mg_pipes.rpy   — трубопровод станка, поворот труб (вместо шестерёнок)
##   mg_wiring.rpy  — проводка Теслы без пересечений + памятка ТБ
##   mg_mine.rpy    — шахта в стиле Bomberman: порода и крысы (вместо бурения)
##   mg_kitchen.rpy — кража ингредиентов в реальном времени + сборка бутера
## ==============================================================================

init -1 python:
    import random
    import math
    import pygame

    class MGTextCache(object):
        """Кэш текстовых displayable (атрибут класса — не попадает в сохранения)."""
        cache = {}

    def mg_text(rv, s, x, y, size=16, color="#ffffff", bold=False, width=None, align=0.0, st=0, at=0):
        """Рисует текст поверх Render. align: 0 — от x вправо, 0.5 — x по центру, 1 — x справа.
        Возвращает (ширина, высота) текста."""
        key = ("txt", s, size, color, bold, width, align)
        d = MGTextCache.cache.get(key)
        if d is None:
            if len(MGTextCache.cache) > 1800:
                MGTextCache.cache.clear()
            d = Text(s, size=size, color=color, bold=bold, text_align=align,
                    substitute=False, xmaximum=(width if width else 4000))
            MGTextCache.cache[key] = d
        tr = renpy.render(d, width or 4000, 4000, st, at)
        tw, th = tr.get_size()
        rv.blit(tr, (int(x - tw * align), int(y)))
        return tw, th

    def mg_blit_img(rv, path, x, y, w, h, align_x=0.5, align_y=0.5, rotate=0, xzoom=1.0, st=0, at=0):
        """Рисует масштабированный/повёрнутый PNG-спрайт поверх Render с кэшированием Transform."""
        if not renpy.loadable(path):
            return 0, 0
        rot_q = int(round(rotate / 3.0)) * 3 % 360 if rotate else 0
        xz = -1.0 if xzoom < 0 else 1.0
        key = ("img", path, int(w), int(h), rot_q, xz)
        d = MGTextCache.cache.get(key)
        if d is None:
            if len(MGTextCache.cache) > 1800:
                MGTextCache.cache.clear()
            if rot_q != 0:
                d = Transform(path, size=(int(w), int(h)), fit="contain", xzoom=xz, rotate=rot_q, rotate_pad=False)
            else:
                d = Transform(path, size=(int(w), int(h)), fit="contain", xzoom=xz)
            MGTextCache.cache[key] = d
        ir = renpy.render(d, int(w), int(h), st, at)
        iw, ih = ir.get_size()
        rv.blit(ir, (int(x - iw * align_x), int(y - ih * align_y)))
        return iw, ih

    def mg_pts(points):
        return [(int(px), int(py)) for (px, py) in points]

    def mg_sfx(path):
        if renpy.loadable(path):
            renpy.sound.play(path)

    # Направления: 0 — вверх, 1 — вправо, 2 — вниз, 3 — влево
    MG_DIR_SCANCODES = {82: 0, 26: 0, 79: 1, 7: 1, 81: 2, 22: 2, 80: 3, 4: 3}
    MG_DIR_KEYS = {
        pygame.K_UP: 0, pygame.K_w: 0,
        pygame.K_RIGHT: 1, pygame.K_d: 1,
        pygame.K_DOWN: 2, pygame.K_s: 2,
        pygame.K_LEFT: 3, pygame.K_a: 3,
    }
    MG_DIR_UNICODE = {"w": 0, "ц": 0, "d": 1, "в": 1, "s": 2, "ы": 2, "a": 3, "ф": 3}
    MG_DIR_VEC = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def mg_key_dir(ev):
        """Направление для клавиши (работает и в русской раскладке, по скан-коду)."""
        sc = getattr(ev, "scancode", None)
        if sc in MG_DIR_SCANCODES:
            return MG_DIR_SCANCODES[sc]
        if ev.key in MG_DIR_KEYS:
            return MG_DIR_KEYS[ev.key]
        u = (getattr(ev, "unicode", "") or "").lower()
        return MG_DIR_UNICODE.get(u)

    def mg_key_ident(ev):
        sc = getattr(ev, "scancode", None)
        if sc:
            return ("sc", sc)
        return ("k", ev.key)

    def mg_is_space(ev):
        return ev.key == pygame.K_SPACE or getattr(ev, "scancode", None) == 44

    def mg_handle_held_keys(game, ev):
        """Запоминает зажатые клавиши движения в game.held. True — событие обработано."""
        if ev.type == pygame.KEYDOWN:
            d = mg_key_dir(ev)
            if d is not None:
                ident = mg_key_ident(ev)
                if not any(h[0] == ident for h in game.held):
                    game.held.append((ident, d))
                return True
        elif ev.type == pygame.KEYUP:
            d = mg_key_dir(ev)
            ident = mg_key_ident(ev)
            before = len(game.held)
            game.held = [h for h in game.held if h[0] != ident]
            if len(game.held) == before and d is not None:
                game.held = [h for h in game.held if h[1] != d]
            return d is not None
        return False

    class MGTouchPad(renpy.Displayable):
        """Виртуальный сенсорный D-Pad (крестовина) для мобильного управления зажатием пальца."""
        def __init__(self, game, size=228, **kwargs):
            super(MGTouchPad, self).__init__(**kwargs)
            self.game = game
            self.size = size
            self.touching = False
            self.cur_dir = None

        def _set_dir(self, d):
            self.cur_dir = d
            self.game.held = [h for h in self.game.held if h[0] != "touch"]
            if d is not None:
                self.game.held.append(("touch", d))

        def _dir_from_xy(self, x, y):
            c = self.size / 2.0
            dx, dy = x - c, y - c
            if math.hypot(dx, dy) < 14:
                return None
            if abs(dx) >= abs(dy):
                return 1 if dx > 0 else 3
            return 2 if dy > 0 else 0

        def render(self, width, height, st, at):
            S = self.size
            rv = renpy.Render(S, S)
            cv = rv.canvas()
            cx = S // 2
            bsz = int(S * 0.31)
            gap = int(S * 0.04)

            # Подложка крестовины
            cv.circle("#0b0f14aa", (cx, cx), cx - 2)
            cv.circle("#354558", (cx, cx), cx - 2, 2)

            btns = [
                (0, cx - bsz // 2, gap, "▲"),
                (1, S - gap - bsz, cx - bsz // 2, "▶"),
                (2, cx - bsz // 2, S - gap - bsz, "▼"),
                (3, gap, cx - bsz // 2, "◀"),
            ]
            for d, bx, by, sym in btns:
                act = (self.cur_dir == d)
                cv.rect("#ffaa33" if act else "#1f2b38", (bx, by, bsz, bsz))
                cv.rect("#ffe699" if act else "#4a607a", (bx, by, bsz, bsz), 2)
                mg_text(rv, sym, bx + bsz // 2, by + bsz // 2 - 16, 28,
                        "#141a22" if act else "#dce8f5", True, align=0.5, st=st, at=at)
            return rv

        def event(self, ev, x, y, st):
            if getattr(self.game, "done", False):
                if self.touching:
                    self.touching = False
                    self._set_dir(None)
                return None

            inside = (0 <= x <= self.size and 0 <= y <= self.size)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and inside:
                self.touching = True
                self._set_dir(self._dir_from_xy(x, y))
                renpy.redraw(self, 0)
                raise renpy.IgnoreEvent()
            elif ev.type == pygame.MOUSEMOTION and self.touching:
                nd = self._dir_from_xy(x, y)
                if nd != self.cur_dir:
                    self._set_dir(nd)
                    renpy.redraw(self, 0)
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.touching:
                self.touching = False
                self._set_dir(None)
                renpy.redraw(self, 0)
            return None
