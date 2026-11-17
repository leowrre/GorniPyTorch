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
        """Виртуальный сенсорный D-Pad (крестовина) из FOTOVSTAVIT2 для мобильного управления."""
        DPAD_IMGS = {
            None: "images/ui/T_X_Dpad.png",
            0: "images/ui/T_X_Dpad_Up.png",
            1: "images/ui/T_X_Dpad_Right.png",
            2: "images/ui/T_X_Dpad_Down.png",
            3: "images/ui/T_X_Dpad_Left.png",
        }

        def __init__(self, game, size=258, **kwargs):
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
            path = self.DPAD_IMGS.get(self.cur_dir, self.DPAD_IMGS[None])
            key = ("dpad_exact", path, int(S))
            d = MGTextCache.cache.get(key)
            if d is None:
                d = Transform(path, size=(int(S), int(S)))
                MGTextCache.cache[key] = d
            rv.blit(renpy.render(d, int(S), int(S), st, at), (0, 0))
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


    class MGBombButton(renpy.Displayable):
        """Кнопка B (закладка заряда) из FOTOVSTAVIT2, затемняющаяся при нажатии."""
        def __init__(self, game, size=240, **kwargs):
            super(MGBombButton, self).__init__(**kwargs)
            self.game = game
            self.size = size
            self.pressed = False
            self.press_until = 0.0

        def render(self, width, height, st, at):
            S = self.size
            rv = renpy.Render(S, S)
            is_dark = self.pressed or (st < self.press_until)
            path = "images/ui/T_X_B_Color_Dark.png" if is_dark else "images/ui/T_X_B_Color.png"
            mg_blit_img(rv, path, S // 2, S // 2, S, S, st=st, at=at)
            if st < self.press_until:
                renpy.redraw(self, 0.04)
            return rv

        def event(self, ev, x, y, st):
            if getattr(self.game, "done", False):
                self.pressed = False
                return None
            c = self.size / 2.0
            inside = (math.hypot(x - c, y - c) <= c)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and inside:
                self.pressed = True
                self.press_until = st + 0.16
                self.game.place_charge()
                renpy.redraw(self, 0)
                raise renpy.IgnoreEvent()
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.pressed:
                self.pressed = False
                renpy.redraw(self, 0)
            return None
