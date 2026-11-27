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
    from collections import OrderedDict
    from renpy.display.matrix import Matrix2D

    _MG_LOADABLE_CACHE = {}

    def mg_loadable(path):
        res = _MG_LOADABLE_CACHE.get(path)
        if res is None:
            res = bool(renpy.loadable(path))
            _MG_LOADABLE_CACHE[path] = res
        return res

    class MGTextCache(object):
        """LRU-кэш текстовых и графических displayable без резких сбросов всего словаря."""
        cache = OrderedDict()
        MAX_SIZE = 700

        @classmethod
        def get(cls, key):
            val = cls.cache.get(key)
            if val is not None:
                cls.cache.move_to_end(key)
            return val

        @classmethod
        def put(cls, key, val):
            cls.cache[key] = val
            cls.cache.move_to_end(key)
            while len(cls.cache) > cls.MAX_SIZE:
                cls.cache.popitem(last=False)

    class MGGpuCanvas(renpy.display.im.ImageBase):
        """Аппаратная текстура в renpy.display.im.cache: рисуется на CPU ровно 1 раз при первом обращении,
        после чего постоянно живёт в видеопамяти WebGL (0 вызовов canvas() и 0 glTexImage2D на кадрах)."""
        obsolete = False
        const_size = True
        _seq = 0

        def __init__(self, key, width, height, draw_fn):
            if key is None:
                MGGpuCanvas._seq += 1
                key = ("auto_gpu_cv", MGGpuCanvas._seq)
            super(MGGpuCanvas, self).__init__(key, int(width), int(height), optimize_bounds=False)
            self.w = int(width)
            self.h = int(height)
            self.draw_fn = draw_fn

        def load(self):
            surf = renpy.display.pgrender.surface((self.w, self.h), True)
            cv = renpy.display.render.Canvas(surf)
            self.draw_fn(surf, cv)
            return surf

    class _MGCanvasRecorder(object):
        def __init__(self, ctx):
            self._ctx = ctx

        def rect(self, *args):
            self._ctx.record_cv("rect", args)

        def circle(self, *args):
            self._ctx.record_cv("circle", args)

        def line(self, *args):
            self._ctx.record_cv("line", args)

        def lines(self, *args):
            self._ctx.record_cv("lines", args)

        def polygon(self, *args):
            self._ctx.record_cv("polygon", args)

    class _MGBakeContext(object):
        def __init__(self, key, w, h):
            self.key = key
            self.w = int(w)
            self.h = int(h)
            self.items = []
            self._cur_cv_ops = None
            self.raw_blit = False

        def record_cv(self, op_name, args):
            if self._cur_cv_ops is None:
                self._cur_cv_ops = []
            self._cur_cv_ops.append((op_name, args))

        def _flush_cv(self):
            if self._cur_cv_ops:
                ops = tuple(self._cur_cv_ops)
                sub_key = (self.key, "cv", len(self.items))
                def _replay(_surf, cv, _ops=ops):
                    for mname, margs in _ops:
                        getattr(cv, mname)(*margs)
                self.items.append(("disp", MGGpuCanvas(sub_key, self.w, self.h, _replay), 0, 0, self.w, self.h))
                self._cur_cv_ops = None

        def canvas(self):
            return _MGCanvasRecorder(self)

        def add_disp(self, disp, x, y, w, h):
            self._flush_cv()
            self.items.append(("disp", disp, x, y, w, h))

        def add_xform(self, disp, x, y, w, h, align_x, align_y, rotate, xzoom):
            self._flush_cv()
            self.items.append(("xform", disp, x, y, w, h, align_x, align_y, rotate, xzoom))

        def add_text(self, disp, x, y, width, align):
            self._flush_cv()
            self.items.append(("text", disp, x, y, width, align))

        def blit(self, sub, pos):
            self.raw_blit = True

    class MGStaticLayer(renpy.Displayable):
        """Кэшируемый на GPU статичный слой: компилирует canvas()-примитивы в постоянную текстуру MGGpuCanvas (im.cache)."""
        _pool = OrderedDict()
        MAX_POOL = 96
        _anon_seq = 0

        def __init__(self, width, height, builder, key=None, clip=False, **kwargs):
            super(MGStaticLayer, self).__init__(**kwargs)
            self.w = int(width)
            self.h = int(height)
            self.builder = builder
            if key is None:
                MGStaticLayer._anon_seq += 1
                key = ("anon_static_layer", MGStaticLayer._anon_seq)
            self.key = key
            self.clip = bool(clip)
            self._compiled = None
            self._fallback = False

        def _compile_once(self):
            ctx = _MGBakeContext(self.key, self.w, self.h)
            try:
                self.builder(ctx, 0.0, 0.0)
                ctx._flush_cv()
                if ctx.raw_blit:
                    self._fallback = True
                else:
                    self._compiled = ctx.items
            except Exception:
                self._fallback = True

        def render(self, width, height, st, at):
            if self._compiled is None and not self._fallback:
                self._compile_once()
            if self._fallback:
                rv = renpy.Render(self.w, self.h)
                if self.clip:
                    rv.xclipping = True
                    rv.yclipping = True
                self.builder(rv, st, at)
                return rv
            rv = renpy.Render(self.w, self.h)
            if self.clip:
                rv.xclipping = True
                rv.yclipping = True
            for item in self._compiled:
                kind = item[0]
                if kind == "disp":
                    _k, d, x, y, dw, dh = item
                    rv.blit(renpy.render(d, dw, dh, st, at), (int(x), int(y)))
                elif kind == "text":
                    _k, td, x, y, tw_max, align = item
                    tr = renpy.render(td, tw_max or 4000, 4000, st, at)
                    tw, _th = tr.get_size()
                    rv.blit(tr, (int(x - tw * align), int(y)))
                elif kind == "xform":
                    _k, im_d, x, y, dw, dh, ax, ay, rot, xz = item
                    mg_blit_im_direct(rv, im_d, x, y, dw, dh, ax, ay, rot, xz, st, at)
            return rv

        @classmethod
        def get(cls, key, width, height, builder, clip=False):
            inst = cls._pool.get(key)
            if inst is not None:
                cls._pool.move_to_end(key)
                return inst
            inst = cls(width, height, builder, key=key, clip=clip)
            cls._pool[key] = inst
            while len(cls._pool) > cls.MAX_POOL:
                cls._pool.popitem(last=False)
            return inst

        @classmethod
        def drop_prefix(cls, prefix):
            dead = [k for k in cls._pool if isinstance(k, tuple) and len(k) > 0 and k[0] == prefix]
            for k in dead:
                cls._pool.pop(k, None)

    def mg_solid(rv, color, x, y, w, h, st=0, at=0):
        """Аппаратная заливка прямоугольника через GPU Solid без выделения программного canvas()."""
        iw, ih = int(w), int(h)
        if iw <= 0 or ih <= 0:
            return
        key = ("solid", color)
        d = MGTextCache.get(key)
        if d is None:
            d = Solid(color)
            MGTextCache.put(key, d)
        if isinstance(rv, _MGBakeContext):
            rv.add_disp(d, x, y, iw, ih)
            return
        rv.blit(renpy.render(d, iw, ih, st, at), (int(x), int(y)))

    def mg_text(rv, s, x, y, size=16, color="#ffffff", bold=False, width=None, align=0.0, st=0, at=0):
        """Рисует текст поверх Render. align: 0 — от x вправо, 0.5 — x по центру, 1 — x справа."""
        key = ("txt", s, size, color, bold, width, align)
        d = MGTextCache.get(key)
        if d is None:
            d = Text(s, size=size, color=color, bold=bold, text_align=align,
                    substitute=False, xmaximum=(width if width else 4000))
            MGTextCache.put(key, d)
        tr = renpy.render(d, width or 4000, 4000, st, at)
        tw, th = tr.get_size()
        if isinstance(rv, _MGBakeContext):
            rv.add_text(d, x, y, width, align)
            return tw, th
        rv.blit(tr, (int(x - tw * align), int(y)))
        return tw, th

    def mg_blit_im_direct(rv, im_d, x, y, w, h, align_x=0.5, align_y=0.5, rotate=0.0, xzoom=1.0, st=0, at=0):
        """Аппаратный рендер Image через Matrix2D в вершинном шейдере WebGL без создания объектов Transform."""
        cr = renpy.render(im_d, int(w), int(h), st, at)
        iw, ih = cr.get_size()
        if iw <= 0 or ih <= 0:
            return 0, 0
        scale = min(float(w) / float(iw), float(h) / float(ih))
        dw, dh = iw * scale, ih * scale
        if rotate == 0 and xzoom >= 0 and abs(scale - 1.0) < 0.008:
            rv.blit(cr, (int(x - iw * align_x), int(y - ih * align_y)))
            return dw, dh
        sx = -scale if xzoom < 0 else scale
        sy = scale
        if rotate:
            rad = math.radians(rotate)
            ca, sa = math.cos(rad), math.sin(rad)
        else:
            ca, sa = 1.0, 0.0
        inv_sx = 1.0 / sx
        inv_sy = 1.0 / sy
        rev = Matrix2D(ca * sx, -sa * sy, sa * sx, ca * sy)
        fwd = Matrix2D(ca * inv_sx, sa * inv_sx, -sa * inv_sy, ca * inv_sy)
        wr = renpy.Render(0, 0)
        wr.forward = fwd
        wr.reverse = rev
        wr.subpixel_blit(cr, rev.transform(-iw * align_x, -ih * align_y))
        rv.subpixel_blit(wr, (float(x), float(y)))
        return dw, dh

    def mg_blit_img(rv, path, x, y, w, h, align_x=0.5, align_y=0.5, rotate=0, xzoom=1.0, st=0, at=0):
        """Быстрая отрисовка спрайта напрямую из im.cache через Matrix2D (0 Transform и 0 проверок ФС на кадре)."""
        if not mg_loadable(path):
            return 0, 0
        im_key = ("raw_im", path)
        im_d = MGTextCache.get(im_key)
        if im_d is None:
            im_d = Image(path)
            MGTextCache.put(im_key, im_d)
        if isinstance(rv, _MGBakeContext):
            rv.add_xform(im_d, x, y, int(w), int(h), align_x, align_y, rotate, xzoom)
            return int(w), int(h)
        return mg_blit_im_direct(rv, im_d, x, y, w, h, align_x, align_y, rotate, xzoom, st, at)

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


init 999 python:
    # При старте игры заранее индексируем доступность всех картинок и аудио из game.zip
    # и прогреваем мелкие UI/мини-игровые спрайты в кэше (без загрузки всех 1920x1080 фонов в VRAM).
    def _preload_game_assets_index():
        for fn in renpy.list_files():
            if fn.startswith("images/") or fn.startswith("audio/"):
                _MG_LOADABLE_CACHE[fn] = True
            if fn.startswith("images/ui/") and fn.lower().endswith((".png", ".webp")):
                renpy.start_predict(fn)
            elif fn.startswith("images/mg/") and fn.lower().endswith((".png", ".webp")):
                renpy.start_predict(fn)

    config.start_callbacks.append(_preload_game_assets_index)
