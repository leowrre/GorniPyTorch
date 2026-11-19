## ==============================================================================
## МИНИ-ИГРЫ КАБИНЕТА ПОВАРОВ (ПОЛНОЭКРАННЫЕ 1920x1080, ФОТО ЦЕХА + СПРАЙТЫ + ПЕНАЛЬТИ)
##   1) Стелс в реальном времени: фото поварского цеха, спрайты оборудования/поваров и система штрафов
##   2) Сборка бутера: фото кухни, PNG-спрайты и штрафы за промахи/нарушение рецептуры
## ==============================================================================

init python:

    class KitchenStealGame(object):
        W, H = 1460, 960
        START = (84.0, 480.0)
        SPEED = 320.0
        COOK_SPEED = 144.0
        MAX_CATCHES = 3
        PR = 24
        PICKUP_DIST = 78
        HALF_FOV = 0.53

        # Просторная расстановка оборудования с широкими проходами (сдвинуто вправо от крестовины)
        OBST = [
            (250, 120, 190, 220, "СТОЛ", "images/mg/equip_table.png"),
            (350, 610, 190, 220, "СТОЛ", "images/mg/equip_table.png"),
            (700, 350, 210, 250, "ПЛИТА", "images/mg/equip_stove.png"),
            (1030, 105, 230, 125, "МОЙКА", "images/mg/equip_sink.png"),
            (1030, 725, 230, 125, "РАЗДЕЛКА", "images/mg/equip_prep.png"),
            (1335, 340, 105, 280, "ХОЛОД.", "images/mg/equip_fridge.png"),
        ]

        # Все продукты разложены на столах/плите/холодильнике (есть нужные и ловушки!)
        INGR = [
            {"id": "bun", "name": "Булочки", "x": 415, "y": 230, "col": "#e0a95f", "need": True},
            {"id": "lettuce", "name": "Салат", "x": 515, "y": 720, "col": "#5fcf4a", "need": True},
            {"id": "patty", "name": "Котлета", "x": 805, "y": 378, "col": "#7a4424", "need": True},
            {"id": "bacon", "name": "Бекон", "x": 728, "y": 475, "col": "#c8553d", "need": False},
            {"id": "tomato", "name": "Помидор", "x": 1145, "y": 205, "col": "#e8412c", "need": True},
            {"id": "cheese", "name": "Сыр", "x": 1090, "y": 752, "col": "#ffd23f", "need": True},
            {"id": "cucumber", "name": "Огурцы", "x": 1205, "y": 752, "col": "#3f9c35", "need": False},
            {"id": "sauce", "name": "Соус", "x": 1360, "y": 480, "col": "#ff7a1a", "need": True},
        ]

        COOKS = [
            {"name": "Повар-кондитер", "wps": [(620, 105), (620, 855)], "range": 300},
            {"name": "Шеф-повар", "wps": [(970, 285), (970, 675), (1255, 675), (1255, 285)], "range": 305},
            {"name": "Су-шеф", "wps": [(1385, 165)], "sweep": True, "base": 2.45, "range": 335},
        ]

        def __init__(self):
            self.total_catches = 0
            self.penalties = 0
            self.reset(full=True)

        def reset(self, full=False):
            if full:
                self.total_catches = 0
                self.penalties = 0
            self.px, self.py = self.START
            self.p_ang = 0.0
            self.collected = []
            self.cooks = []
            for meta in self.COOKS:
                x, y = meta["wps"][0]
                wi = 1 % len(meta["wps"])
                tx, ty = meta["wps"][wi]
                ang = meta.get("base", math.atan2(ty - y, tx - x))
                self.cooks.append({"x": float(x), "y": float(y), "ang": ang, "wi": wi, "pause": 0.0, "look": ang, "alert": 0.0})
            self.held = []
            self.mouse_target = None
            self.invuln = 1.0
            self.time = 0.0
            self.caught_count = 0
            self.penalty_popup = False
            self.banner_text = ""
            self.banner_col = "#ff6655"
            self.banner_timer = 0.0
            self.done = False
            self.need_refresh = False
            self.message = ""

        def dismiss_penalty(self):
            self.penalty_popup = False
            self.reset(full=False)

        def ingr(self, iid):
            for it in self.INGR:
                if it["id"] == iid:
                    return it
            return None

        def extra_count(self):
            return sum(1 for iid in self.collected if not self.ingr(iid)["need"])

        def need_left(self):
            return [it for it in self.INGR if it["need"] and it["id"] not in self.collected]

        def has_all(self):
            return len(self.need_left()) == 0

        def point_blocked(self, x, y):
            for (ox, oy, ow, oh, _n, _sp) in self.OBST:
                if ox <= x <= ox + ow and oy <= y <= oy + oh:
                    return True
            return False

        def collide(self, x, y):
            if x < self.PR or x > self.W - self.PR or y < self.PR or y > self.H - self.PR:
                return True
            for (ox, oy, ow, oh, _n, _sp) in self.OBST:
                cx = max(ox, min(x, ox + ow))
                cy = max(oy, min(y, oy + oh))
                if (x - cx) ** 2 + (y - cy) ** 2 < self.PR * self.PR:
                    return True
            return False

        def los(self, x0, y0, x1, y1):
            d = math.hypot(x1 - x0, y1 - y0)
            n = int(d / 12) + 1
            for k in range(1, n):
                t = k / float(n)
                if self.point_blocked(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t):
                    return False
            return True

        def sees(self, i, px, py):
            ck = self.cooks[i]
            rng = self.COOKS[i].get("range", 300)
            dx, dy = px - ck["x"], py - ck["y"]
            d = math.hypot(dx, dy)
            if d > rng + self.PR:
                return False
            if d < 38:
                return True
            a = math.atan2(dy, dx)
            diff = abs((a - ck["ang"] + math.pi) % (2 * math.pi) - math.pi)
            if diff > self.HALF_FOV + self.PR / d:
                return False
            return self.los(ck["x"], ck["y"], px, py)

        def vision_poly(self, i):
            """Конус обзора, обрезанный столами и плитой."""
            ck = self.cooks[i]
            rng = self.COOKS[i].get("range", 300)
            pts = [(ck["x"], ck["y"])]
            rays = 18
            for k in range(rays + 1):
                a = ck["ang"] - self.HALF_FOV + 2 * self.HALF_FOV * k / float(rays)
                ca, sa = math.cos(a), math.sin(a)
                dist = 0.0
                while dist < rng:
                    nd = dist + 14.0
                    x, y = ck["x"] + ca * nd, ck["y"] + sa * nd
                    if self.point_blocked(x, y) or not (0 <= x <= self.W and 0 <= y <= self.H):
                        break
                    dist = nd
                pts.append((ck["x"] + ca * dist, ck["y"] + sa * dist))
            return pts

        def caught(self, i):
            self.cooks[i]["alert"] = 1.5
            self.caught_count += 1
            self.total_catches += 1
            self.invuln = 1.7
            self.px, self.py = self.START
            self.p_ang = 0.0
            self.held = []
            self.mouse_target = None
            mg_sfx("audio/stealth_spotted.wav")

            # Пенальти: изымается до 2 собранных продуктов, а на 3-й поимке — изгнание из цеха!
            removed = 0
            while self.collected and removed < 2:
                iid = random.choice(self.collected)
                self.collected.remove(iid)
                removed += 1

            if self.caught_count >= self.MAX_CATCHES:
                self.penalties += 1
                self.collected = []
                self.penalty_popup = True
                self.banner_text = "Вас выдвинули с кухни"
                self.banner_col = "#ff4444"
                self.banner_timer = 0.0
            else:
                left = self.MAX_CATCHES - self.caught_count
                self.banner_text = "Повар отобрал продукты (-%d шт.)! Попыток до изгнания: %d" % (removed, left)
                self.banner_col = "#ff6655"
                self.banner_timer = 2.6
            self.need_refresh = True

        @staticmethod
        def turn_towards(a, target, max_step):
            diff = (target - a + math.pi) % (2 * math.pi) - math.pi
            diff = max(-max_step, min(max_step, diff))
            return a + diff

        def update(self, dt):
            if self.done or self.penalty_popup:
                return
            self.time += dt
            if self.invuln > 0:
                self.invuln = max(0.0, self.invuln - dt)
            if self.banner_timer > 0:
                self.banner_timer = max(0.0, self.banner_timer - dt)

            # Скорость игрока снижается при подборе лишних (не из рецепта) продуктов!
            eff_speed = self.SPEED * max(0.68, 1.0 - 0.14 * self.extra_count())

            mx, my = 0.0, 0.0
            for (_ident, d) in self.held:
                vx, vy = MG_DIR_VEC[d]
                mx += vx
                my += vy
            if mx == 0 and my == 0 and self.mouse_target is not None:
                tx, ty = self.mouse_target
                ddx, ddy = tx - self.px, ty - self.py
                dd = math.hypot(ddx, ddy)
                if dd > 10:
                    mx, my = ddx / dd, ddy / dd
            ln = math.hypot(mx, my)
            if ln > 0:
                mx, my = mx / ln, my / ln
                self.p_ang = math.atan2(my, mx)
                nx = self.px + mx * eff_speed * dt
                if not self.collide(nx, self.py):
                    self.px = nx
                ny = self.py + my * eff_speed * dt
                if not self.collide(self.px, ny):
                    self.py = ny

            # Патрулирование поваров (ускоряются при каждой тревоге!)
            cook_spd = self.COOK_SPEED * (1.0 + 0.12 * self.caught_count)
            for i, ck in enumerate(self.cooks):
                meta = self.COOKS[i]
                if ck["alert"] > 0:
                    ck["alert"] = max(0.0, ck["alert"] - dt)
                if meta.get("sweep"):
                    ck["ang"] = meta["base"] + math.sin(self.time * (0.9 + 0.1 * self.caught_count)) * 0.84
                    continue
                if ck["pause"] > 0:
                    ck["pause"] = max(0.0, ck["pause"] - dt)
                    ck["ang"] = ck["look"] + math.sin((0.9 - ck["pause"]) * 7.0) * 0.55
                    continue
                tx, ty = meta["wps"][ck["wi"]]
                ddx, ddy = tx - ck["x"], ty - ck["y"]
                dd = math.hypot(ddx, ddy)
                if dd < 3.0:
                    ck["wi"] = (ck["wi"] + 1) % len(meta["wps"])
                    ck["pause"] = 0.85
                    ck["look"] = ck["ang"]
                    continue
                step = min(dd, cook_spd * dt)
                ck["x"] += ddx / dd * step
                ck["y"] += ddy / dd * step
                ck["ang"] = self.turn_towards(ck["ang"], math.atan2(ddy, ddx), 5.2 * dt)

            # Подбор продуктов со столов (с предупреждением-штрафом за лишний продукт!)
            for it in self.INGR:
                if it["id"] not in self.collected and math.hypot(self.px - it["x"], self.py - it["y"]) <= self.PICKUP_DIST:
                    self.collected.append(it["id"])
                    if it["need"]:
                        mg_sfx("audio/ingredient_pickup.wav")
                    else:
                        mg_sfx("audio/turnstile_fail.wav")
                        self.banner_text = "ШТРАФ: «%s» нет в заказе Семёна! Карманы тяжелеют (-скорость)!" % it["name"]
                        self.banner_col = "#ffcc44"
                        self.banner_timer = 2.4
                    self.need_refresh = True

            # Обнаружение поварами
            if self.invuln <= 0:
                for i in range(len(self.cooks)):
                    if self.sees(i, self.px, self.py):
                        self.caught(i)
                        break

            # Побег через дверь после сбора всех нужных продуктов
            if self.has_all() and self.px < 96 and 380 <= self.py <= 580:
                self.done = True
                self.held = []
                self.mouse_target = None
                mg_sfx("audio/bun_win.wav")
                self.need_refresh = True


    class KitchenStealDisplayable(renpy.Displayable):
        TOP = 58
        _bg_cache = None

        def __init__(self, game, **kwargs):
            super(KitchenStealDisplayable, self).__init__(**kwargs)
            self.game = game
            self.W = game.W
            self.H = game.H + self.TOP
            self.last_st = None

        def render(self, width, height, st, at):
            g = self.game
            dt = 0.0 if self.last_st is None else max(0.0, min(0.05, st - self.last_st))
            self.last_st = st
            g.update(dt)
            T = self.TOP

            rv = renpy.Render(self.W, self.H)
            floor = renpy.Render(self.W, self.H)
            fc = floor.canvas()
            fc.rect("#181f26", (0, 0, self.W, T))

            # Светлая кафельная плитка учебного кулинарного цеха ПГТ + фото-подложка
            tile = 80
            for yy in range(0, g.H, tile):
                for xx in range(0, g.W, tile):
                    w = min(tile, g.W - xx)
                    h = min(tile, g.H - yy)
                    fc.rect("#3b444c" if ((xx // tile + yy // tile) % 2 == 0) else "#333b42", (xx, T + yy, w, h))
            if renpy.loadable("images/bg/pgt_culinary_hall.png"):
                if KitchenStealDisplayable._bg_cache is None:
                    KitchenStealDisplayable._bg_cache = Transform(
                        "images/bg/pgt_culinary_hall.png",
                        size=(self.W, g.H),
                        fit="cover",
                        alpha=0.22
                    )
                floor.blit(renpy.render(KitchenStealDisplayable._bg_cache, self.W, g.H, st, at), (0, T))

            # Дверь слева
            door_col = "#2fbf71" if g.has_all() else "#b87a44"
            fc.rect(door_col, (0, T + 390, 26, 180))
            if g.has_all() and int(g.time * 5) % 2 == 0:
                fc.rect("#99ffcc", (0, T + 390, 26, 180), 4)
            rv.blit(floor, (0, 0))

            # Конусы обзора поваров
            cones = renpy.Render(self.W, self.H)
            cc = cones.canvas()
            for i, ck in enumerate(g.cooks):
                poly = [(x, y + T) for (x, y) in g.vision_poly(i)]
                cc.polygon("#ff181888" if ck["alert"] > 0 else "#ff3b3b52", mg_pts(poly))
            rv.blit(cones, (0, 0))

            # Спрайты кухонного оборудования (или детализированная нержавейка)
            objs = renpy.Render(self.W, self.H)
            oc = objs.canvas()
            for (ox, oy, ow, oh, name, sp_path) in g.OBST:
                oc.rect("#0f1419aa", (ox + 7, T + oy + 9, ow, oh))
                if renpy.loadable(sp_path):
                    mg_blit_img(objs, sp_path, ox + ow // 2, T + oy + oh // 2, ow, oh, st=st, at=at)
                else:
                    if name == "ПЛИТА":
                        oc.rect("#2f353d", (ox, T + oy, ow, oh))
                        oc.rect("#656e7a", (ox + 6, T + oy + 6, ow - 12, oh - 12))
                        for (bx, by) in [(ox + 58, oy + 65), (ox + ow - 58, oy + 65),
                                         (ox + 58, oy + oh - 65), (ox + ow - 58, oy + oh - 65)]:
                            oc.circle("#181b20", (bx, T + by), 32)
                            oc.circle("#ff5522", (bx, T + by), 22, 4)
                    elif name == "ХОЛОД.":
                        oc.rect("#7b90a2", (ox, T + oy, ow, oh))
                        oc.rect("#dce7f0", (ox + 6, T + oy + 6, ow - 12, oh - 12))
                    elif name == "МОЙКА":
                        oc.rect("#6c7d8c", (ox, T + oy, ow, oh))
                        oc.rect("#b8cad8", (ox + 6, T + oy + 6, ow - 12, oh - 12))
                        oc.rect("#4a6880", (ox + 26, T + oy + 22, 92, 82))
                        oc.rect("#4a6880", (ox + 132, T + oy + 22, 92, 82))
                    else:
                        oc.rect("#788694", (ox, T + oy, ow, oh))
                        oc.rect("#cfd8e0", (ox + 6, T + oy + 6, ow - 12, oh - 12))
                mg_text(objs, name, ox + ow // 2, T + oy + oh // 2 - 12, 19, "#16202a", True, align=0.5, st=st, at=at)

            mg_text(objs, "ВЫХОД", 36, T + 466, 22, "#88ffbb" if g.has_all() else "#ffe0b2", True, st=st, at=at)

            # PNG-спрайты продуктов на столах
            for it in g.INGR:
                if it["id"] in g.collected:
                    continue
                bob = int(3 * math.sin(g.time * 4.0 + it["x"] * 0.05))
                ix, iy = int(it["x"]), int(T + it["y"] + bob)
                if it["need"]:
                    oc.circle("#ffdd55", (ix, iy), 40, 3)
                else:
                    oc.circle("#ff554488", (ix, iy), 36, 2)
                mg_blit_img(objs, "images/mg/ingr_%s.png" % it["id"], ix, iy, 74, 74, st=st, at=at)

            # PNG-спрайты поваров (повёрнуты по взгляду)
            for ck in g.cooks:
                cx, cy = int(ck["x"]), int(T + ck["y"])
                mg_blit_img(objs, "images/mg/cook_sprite.png", cx, cy, 102, 102,
                            rotate=math.degrees(ck["ang"]), st=st, at=at)
                if ck["alert"] > 0:
                    mg_text(objs, "!", cx, cy - 68, 44, "#ff3333", True, align=0.5, st=st, at=at)

            # PNG-спрайт школьника
            if not (g.invuln > 0 and int(g.time * 12) % 2 == 0):
                px, py = int(g.px), int(T + g.py)
                mg_blit_img(objs, "images/mg/player_stealth.png", px, py, 86, 86,
                            rotate=math.degrees(g.p_ang), st=st, at=at)

            rv.blit(objs, (0, 0))

            # Лаконичный верхний HUD в стиле Persona 3 Reload
            need_total = sum(1 for it in g.INGR if it["need"])
            got = need_total - len(g.need_left())
            lives_left = max(0, g.MAX_CATCHES - g.caught_count)
            if g.has_all() and not g.done:
                hud = "%d / %d  —  К ВЫХОДУ" % (got, need_total)
                hcol = "#00e5ff"
            else:
                hud = "Продукты: %d / %d      Попытки: %d / %d" % (got, need_total, lives_left, g.MAX_CATCHES)
                hcol = "#ffffff"
            mg_text(rv, hud, self.W // 2, 13, 25, hcol, True, align=0.5, st=st, at=at)

            if not g.done and not g.penalty_popup:
                renpy.redraw(self, 0)
            if g.need_refresh:
                renpy.timeout(0)
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.need_refresh:
                g.need_refresh = False
                renpy.restart_interaction()
            if g.done or g.penalty_popup:
                return None
            if ev.type in (pygame.KEYDOWN, pygame.KEYUP):
                if mg_handle_held_keys(g, ev):
                    raise renpy.IgnoreEvent()
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and 0 <= x < self.W and self.TOP <= y < self.H:
                g.mouse_target = (x, y - self.TOP)
            elif ev.type == pygame.MOUSEMOTION and g.mouse_target is not None:
                g.mouse_target = (max(0, min(self.W, x)), max(0, min(g.H, y - self.TOP)))
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                g.mouse_target = None
            return None


    # --------------------------------------------------------------------------
    # СБОРКА БУТЕРА (ФОТО КУХНИ + PNG-ИНГРЕДИЕНТЫ + ШТРАФЫ ЗА ПРОМАХ И ОШИБКИ)
    # --------------------------------------------------------------------------
    class BurgerGame(object):
        LAYERS = [
            ("bun_bottom", {"name": "Булка низ", "src": "bun", "col": "#d9a05b", "h": 38, "iw": 340, "ih": 56, "ay": 0.90}),
            ("patty", {"name": "Котлета", "src": "patty", "col": "#6b3b1f", "h": 36, "iw": 340, "ih": 56, "ay": 0.88}),
            ("cheese", {"name": "Сыр", "src": "cheese", "col": "#ffd23f", "h": 20, "iw": 340, "ih": 48, "ay": 0.68}),
            ("lettuce", {"name": "Салат", "src": "lettuce", "col": "#5fcf4a", "h": 26, "iw": 340, "ih": 46, "ay": 0.88}),
            ("tomato", {"name": "Помидор", "src": "tomato", "col": "#e8412c", "h": 24, "iw": 340, "ih": 40, "ay": 0.88}),
            ("sauce", {"name": "Соус", "src": "sauce", "col": "#ff7a1a", "h": 18, "iw": 340, "ih": 34, "ay": 0.86}),
            ("cucumber", {"name": "Огурцы", "src": "cucumber", "col": "#3f9c35", "h": 22, "iw": 340, "ih": 36, "ay": 0.88}),
            ("bacon", {"name": "Бекон", "src": "bacon", "col": "#c8553d", "h": 22, "iw": 340, "ih": 40, "ay": 0.88}),
            ("bun_top", {"name": "Булка верх", "src": "bun", "col": "#e0a95f", "h": 92, "iw": 340, "ih": 112, "ay": 0.94}),
        ]
        ORDER = ["bun_bottom", "patty", "cheese", "lettuce", "tomato", "sauce", "bun_top"]
        PLATE_X, PLATE_Y = 930, 885
        SWING = 330
        DROP_Y = 225.0

        def __init__(self):
            self.stolen = []
            self.mistakes = 0
            self.reset_stack(clear_mistakes=True)

        def info(self, lid):
            for k, v in self.LAYERS:
                if k == lid:
                    return v
            return None

        def setup(self, stolen):
            self.stolen = list(stolen)
            self.reset_stack(clear_mistakes=True)

        def reset_stack(self, clear_mistakes=False):
            if clear_mistakes:
                self.mistakes = 0
            self.stack = []
            self.holding = None
            self.falling = None
            self.phase = 0.0
            self.served = False
            self.grade = None
            self.penalty_msg = ""
            self.penalty_timer = 0.0
            self.need_refresh = False
            self.message = ""

        def available(self):
            used = [l["id"] for l in self.stack]
            if self.holding:
                used.append(self.holding)
            if self.falling:
                used.append(self.falling["id"])
            return [k for k, v in self.LAYERS if v["src"] in self.stolen and k not in used]

        def pick(self, lid):
            if self.served or self.falling is not None:
                return
            used = [l["id"] for l in self.stack]
            if lid not in used and self.info(lid)["src"] in self.stolen:
                self.holding = lid

        def hand_x(self):
            return self.PLATE_X + self.SWING * math.sin(self.phase)

        def drop(self):
            if self.served or self.falling is not None or not self.holding:
                return
            self.falling = {"id": self.holding, "x": self.hand_x(), "y": self.DROP_Y, "vy": 0.0}
            self.holding = None

        def stack_height(self):
            return sum(self.info(l["id"])["h"] for l in self.stack)

        def is_complete(self):
            return len(self.stack) == len(self.ORDER)

        def all_ok(self):
            return self.is_complete() and all(l["ok"] for l in self.stack)

        def has_wrong(self):
            return any(not l["ok"] for l in self.stack)

        def neatness(self):
            if not self.stack:
                return 0.0
            return sum(abs(l["off"]) for l in self.stack) / float(len(self.stack))

        def update(self, dt):
            if self.served:
                return
            if self.penalty_timer > 0:
                self.penalty_timer = max(0.0, self.penalty_timer - dt)
            # С каждым штрафом рука двигается быстрее (сложнее целиться!)
            spd_mult = 1.48 + 0.21 * len(self.stack) + 0.14 * min(5, self.mistakes)
            self.phase += dt * spd_mult
            f = self.falling
            if f is None:
                return
            f["vy"] += 2100.0 * dt
            f["y"] += f["vy"] * dt
            target_y = self.PLATE_Y - self.stack_height()
            if f["y"] >= target_y:
                off = f["x"] - self.PLATE_X
                dropped_id = f["id"]
                self.falling = None
                if abs(off) > 195:
                    self.mistakes += 1
                    mg_sfx("audio/turnstile_fail.wav")
                    self.penalty_msg = "МИМО ТАРЕЛКИ! Штраф +1 (рука движется быстрее!)"
                    self.penalty_timer = 2.2
                    self.holding = dropped_id
                else:
                    idx = len(self.stack)
                    ok = idx < len(self.ORDER) and self.ORDER[idx] == dropped_id
                    self.stack.append({"id": dropped_id, "off": off, "ok": ok})
                    if ok:
                        mg_sfx("audio/burger_drop.wav")
                        if self.all_ok():
                            self.serve()
                    else:
                        self.mistakes += 1
                        mg_sfx("audio/turnstile_fail.wav")
                        self.penalty_msg = "НАРУШЕН РЕЦЕПТ! Штраф +1 — сбросьте бутер!"
                        self.penalty_timer = 2.6
                self.need_refresh = True

        def serve(self):
            if not self.all_ok():
                return
            n = self.neatness() + self.mistakes * 14.0
            if self.mistakes == 0 and n <= 26:
                self.grade = "perfect"
            elif self.mistakes <= 2 and n <= 68:
                self.grade = "good"
            else:
                self.grade = "sloppy"
            self.served = True
            mg_sfx("audio/bun_win.wav")


    class BurgerDisplayable(renpy.Displayable):
        W, H = 1430, 1080
        ARENA_X = 410
        _bg_cache = None

        def __init__(self, game, **kwargs):
            super(BurgerDisplayable, self).__init__(**kwargs)
            self.game = game
            self.last_st = None

        def _blit_burger_layer(self, rv, lid, cx, yb, st, at):
            info = self.game.info(lid)
            mg_blit_img(rv, "images/mg/layer_%s.png" % lid,
                        int(cx), int(yb), info["iw"], info["ih"],
                        align_x=0.5, align_y=info["ay"], st=st, at=at)

        def render(self, width, height, st, at):
            g = self.game
            dt = 0.0 if self.last_st is None else max(0.0, min(0.05, st - self.last_st))
            self.last_st = st
            g.update(dt)

            rv = renpy.Render(self.W, self.H)
            cv = rv.canvas()

            # Фотография учебного цеха поваров на заднем плане + прежний цвет столешницы
            cv.rect("#05122c", (0, 0, self.W, self.H))
            if renpy.loadable("images/bg/pgt_culinary_hall.png"):
                if BurgerDisplayable._bg_cache is None:
                    BurgerDisplayable._bg_cache = Transform(
                        "images/bg/pgt_culinary_hall.png",
                        size=(self.W - self.ARENA_X, 850),
                        fit="cover",
                        matrixcolor=BrightnessMatrix(-0.38)
                    )
                rv.blit(renpy.render(BurgerDisplayable._bg_cache, self.W - self.ARENA_X, 850, st, at), (self.ARENA_X, 0))
            else:
                cv.rect("#2e1e15", (self.ARENA_X, 0, self.W - self.ARENA_X, 850))
            cv.rect("#5f6b76", (self.ARENA_X, 850, self.W - self.ARENA_X, 230))
            cv.rect("#9aa8b5", (self.ARENA_X, 850, self.W - self.ARENA_X, 14))

            # Список слоёв слева в стиле Persona 3 Reload (Белый-Синий-Голубой)
            cv.rect("#f2f8ff", (24, 26, 366, 900))
            cv.rect("#0b2868", (24, 26, 366, 86))
            cv.rect("#00d4ff", (24, 26, 366, 900), 4)
            mg_text(rv, "РЕЦЕПТ", 242, 52, 30, "#ffffff", True, align=0.5, st=st, at=at)

            for i, lid in enumerate(reversed(g.ORDER)):
                idx = len(g.ORDER) - 1 - i
                ry = 122 + i * 110
                info = g.info(lid)
                is_next = (idx == len(g.stack) and not g.has_wrong())
                if is_next:
                    cv.rect("#cceeff", (38, ry - 6, 338, 92))
                    cv.rect("#00a8f0", (38, ry - 6, 338, 92), 3)

                mg_blit_img(rv, "images/mg/ingr_%s.png" % info["src"], 78, ry + 38, 64, 64, st=st, at=at)
                mg_text(rv, "%d. %s" % (idx + 1, info["name"]), 120, ry + 22, 23, "#082567", True, st=st, at=at)

                mark, mcol = "•", "#6b94c8"
                if idx < len(g.stack):
                    if g.stack[idx]["ok"]:
                        mark, mcol = "+", "#0088ee"
                    else:
                        mark, mcol = "Х", "#1b449c"
                mg_text(rv, mark, 358, ry + 18, 28, mcol, True, align=1.0, st=st, at=at)

            # PNG-тарелка на столе
            px, py = g.PLATE_X, g.PLATE_Y
            mg_blit_img(rv, "images/mg/burger_plate.png", px, py + 4, 520, 130,
                        align_x=0.5, align_y=0.52, st=st, at=at)

            # Подсказка-прицел на тарелке при удержании ингредиента
            if not g.served and g.holding:
                hx_f = g.hand_x()
                on_plate = abs(hx_f - px) <= 185
                cv.line("#00e5ff66" if on_plate else "#ffffff44", (int(hx_f), 230), (int(hx_f), int(py - g.stack_height())), 3)

            # Собранные PNG-слои бутера на тарелке
            yb = py
            for layer in g.stack:
                info = g.info(layer["id"])
                self._blit_burger_layer(rv, layer["id"], px + layer["off"], yb, st, at)
                if not layer["ok"]:
                    cv.rect("#00e5ff", (int(px + layer["off"] - 165), int(yb - info["h"] - 8), 330, info["h"] + 12), 4)
                yb -= info["h"]

            # Падающий PNG-ингредиент при выбросе на тарелку
            if g.falling:
                f = g.falling
                self._blit_burger_layer(rv, f["id"], f["x"], f["y"], st, at)

            # PNG-рука сверху, держащая выбранный PNG-ингредиент
            if not g.served:
                hx = int(g.hand_x())
                if g.holding:
                    self._blit_burger_layer(rv, g.holding, hx, int(g.DROP_Y), st, at)
                mg_blit_img(rv, "images/mg/burger_hand.png", hx, 0, 216, 225,
                            align_x=0.5, align_y=0.0, st=st, at=at)

            if g.has_wrong() and not g.served:
                mg_text(rv, "ОШИБКА СЛОЯ", px, 290, 34, "#00e5ff", True, align=0.5, st=st, at=at)

            if not g.served:
                renpy.redraw(self, 0)
            if g.need_refresh:
                renpy.timeout(0)
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.need_refresh:
                g.need_refresh = False
                renpy.restart_interaction()
            if g.served:
                return None
            if ev.type == pygame.KEYDOWN and mg_is_space(ev):
                g.drop()
                renpy.restart_interaction()
                raise renpy.IgnoreEvent()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.ARENA_X <= x < self.W and 0 <= y < self.H:
                g.drop()
                renpy.restart_interaction()
            return None


default mg_kitchen = KitchenStealGame()
default mg_burger = BurgerGame()

# ------------------------------------------------------------------------------
# ЭКРАН: КРАЖА ИНГРЕДИЕНТОВ (ФОТО ЦЕХА + СПРАЙТЫ + ПЕНАЛЬТИ ЗА ПОИМКУ)
# ------------------------------------------------------------------------------
screen screen_minigame_kitchen():
    modal True

    fixed:
        xsize 1920
        ysize 1080

        if renpy.loadable("images/bg/pgt_culinary_hall.png"):
            add Transform("images/bg/pgt_culinary_hall.png", size=(1920, 1080), fit="cover", matrixcolor=BrightnessMatrix(-0.62))
        else:
            add Solid("#1a120d")

        # Арена кухни 1460 x 1018
        add KitchenStealDisplayable(mg_kitchen) xpos 20 ypos 30
        add Transform("images/ui/logo_pgt_white.png", size=(76, 76), fit="contain") xpos 28 ypos 18

        # Правая скруглённая панель: список Семёна с PNG-иконками + сенсорная крестовина
        frame:
            xpos 1500
            ypos 30
            xsize 400
            ysize 1018
            background Frame("images/ui/round_panel.png", 26, 26)
            padding (22, 20)

            vbox:
                spacing 12
                xfill True
                yfill True

                hbox:
                    xfill True
                    text "СПИСОК" size 26 color "#ffffff" bold True yalign 0.5
                    if not mg_kitchen.done:
                        textbutton "Сброс":
                            action Function(mg_kitchen.reset, False)
                            keyboard_focus False
                            xalign 1.0
                            background Frame("images/ui/round_btn_idle.png", 14, 14)
                            hover_background Frame("images/ui/round_btn_hover.png", 14, 14)
                            text_size 20
                            text_bold True
                            text_color "#ffffff"
                            padding (18, 8)

                for it in mg_kitchen.INGR:
                    if it["need"]:
                        $ got_it = it["id"] in mg_kitchen.collected
                        frame:
                            xfill True
                            background Frame("images/ui/round_badge_green.png" if got_it else "images/ui/round_btn_idle.png", 16, 16)
                            padding (14, 8)
                            hbox:
                                spacing 14
                                add Transform("images/mg/ingr_" + it["id"] + ".png", size=(48, 48), fit="contain") yalign 0.5
                                text it["name"] size 23 bold True color "#ffffff" yalign 0.5
                                text ("+" if got_it else "") size 26 bold True color "#ffffff" xalign 1.0 yalign 0.5

                if mg_kitchen.done:
                    null height 18
                    textbutton "СОБРАТЬ БУТЕР":
                        action Return(True)
                        xfill True
                        background Frame("images/ui/round_mg_green.png", 20, 20)
                        hover_background Frame("images/ui/round_mg_green_hover.png", 20, 20)
                        text_size 28
                        text_bold True
                        text_color "#ffffff"
                        text_xalign 0.5
                        padding (18, 30)

        # Сенсорная крестовина слева снизу
        if not mg_kitchen.done:
            add MGTouchPad(mg_kitchen, size=258) xpos 36 ypos 754

        # Модальное скруглённое окно проигрыша без лишнего текста
        if mg_kitchen.penalty_popup:
            button:
                xfill True
                yfill True
                background Solid("#030a1cbb")
                action Function(mg_kitchen.dismiss_penalty)

            frame:
                xalign 0.5
                yalign 0.5
                xsize 680
                background Frame("images/ui/round_mg_red_modal.png", 28, 28)
                padding (44, 38)

                vbox:
                    spacing 24
                    xalign 0.5

                    text "Вас выдвинули с кухни" size 38 color "#7ae8ff" bold True xalign 0.5 text_align 0.5

                    textbutton "Заново":
                        xalign 0.5
                        action Function(mg_kitchen.dismiss_penalty)
                        background Frame("images/ui/round_mg_red_btn.png", 18, 18)
                        hover_background Frame("images/ui/round_mg_red_btn_hover.png", 18, 18)
                        text_size 26
                        text_bold True
                        text_color "#ffffff"
                        padding (48, 16)

# ------------------------------------------------------------------------------
# ЭКРАН: СБОРКА БУТЕРА (ФОТО КУХНИ + PNG-КАРТОЧКИ + ШТРАФЫ)
# ------------------------------------------------------------------------------
screen screen_minigame_burger():
    modal True

    if mg_burger.all_ok():
        timer 1.5 action [Function(mg_burger.serve), Return(True)]

    fixed:
        xsize 1920
        ysize 1080

        add BurgerDisplayable(mg_burger) xpos 0 ypos 0
        add Transform("images/ui/logo_pgt_white.png", size=(76, 76), fit="contain") xpos 36 ypos 31

        # Скруглённая кнопка разбора бутера под чеком слева
        if not mg_burger.served and not mg_burger.all_ok():
            textbutton "Сброс":
                xpos 24
                ypos 946
                xsize 366
                action Function(mg_burger.reset_stack, False)
                keyboard_focus False
                background Frame("images/ui/round_btn_idle.png", 20, 20)
                hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                text_size 26
                text_bold True
                text_color "#ffffff"
                text_xalign 0.5
                padding (16, 22)

        # Правая скруглённая панель: крупные PNG-кнопки ингредиентов под большой палец
        frame:
            xpos 1430
            ypos 12
            xsize 478
            ysize 1056
            background Frame("images/ui/round_panel.png", 26, 26)
            padding (18, 22)

            vbox:
                spacing 14
                xfill True
                yfill True

                text "ИНГРЕДИЕНТЫ" size 26 color "#ffffff" bold True xalign 0.5

                $ burger_choices = [k for k, v in mg_burger.LAYERS if v["src"] in mg_burger.stolen and k not in [l["id"] for l in mg_burger.stack] and (mg_burger.falling is None or mg_burger.falling["id"] != k)]

                hbox:
                    box_wrap True
                    spacing 12
                    box_wrap_spacing 12
                    xsize 440
                    xalign 0.5
                    for lid in burger_choices:
                        $ b_info = mg_burger.info(lid)
                        $ is_held = (mg_burger.holding == lid)
                        button:
                            xsize 214
                            ysize 154
                            action Function(mg_burger.pick, lid)
                            keyboard_focus False
                            background Frame("images/ui/round_btn_active.png" if is_held else "images/ui/round_btn_idle.png", 18, 18)
                            hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                            padding (10, 10)
                            vbox:
                                xalign 0.5
                                yalign 0.5
                                spacing 6
                                if lid == "bun_bottom":
                                    add Transform("images/mg/layer_bun_bottom.png", size=(150, 48), fit="contain") xalign 0.5
                                elif lid == "bun_top":
                                    add Transform("images/mg/layer_bun_top.png", size=(150, 62), fit="contain") xalign 0.5
                                else:
                                    add Transform("images/mg/ingr_" + b_info["src"] + ".png", size=(78, 78), fit="contain") xalign 0.5
                                text b_info["name"] size 22 bold True color "#ffffff" xalign 0.5

        # Полупрозрачная табличка посередине экрана по всей ширине (как в сборке сайта) + переход через 1.5 сек
        if mg_burger.all_ok():
            frame:
                xpos 0
                yalign 0.5
                xsize 1920
                ysize 148
                background Solid("#082868dc")
                padding (0, 0)

                vbox:
                    xsize 1920
                    yfill True
                    add Solid("#00e5ff") xsize 1920 ysize 4
                    text "БУТЕРБРОД СОБРАН ПРАВИЛЬНО!" size 46 color "#ffffff" bold True xalign 0.5 yalign 0.5 text_align 0.5
                    add Solid("#00e5ff") xsize 1920 ysize 4 yalign 1.0

            button:
                xsize 1920
                ysize 1080
                background None
                action [Function(mg_burger.serve), Return(True)]
