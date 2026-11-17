## ==============================================================================
## МИНИ-ИГРА: РЕДУКТОР СТАНКА — СБОРКА ШЕСТЕРЁНОК (МУСКУЛИСТЫЕ РАБОТЯГИ / МТО)
## Игрок подбирает и устанавливает шестерни разных размеров на оси коробки передач,
## чтобы передать вращение от ведущего мотора ко всем трём узлам станка.
## ==============================================================================

init python:

    class GearMachineGame(object):
        # Модуль зацепления m = 15.5 px: R = teeth * 7.75
        GEAR_SPECS = {
            "S": {"title": "Малая шестерня", "short": "МАЛАЯ", "teeth": 8, "r": 62,
                  "fill": "#3399ee", "rim": "#1d5d96", "hub": "#99ddff"},
            "M": {"title": "Средняя шестерня", "short": "СРЕДНЯЯ", "teeth": 12, "r": 93,
                  "fill": "#f0a028", "rim": "#9c6212", "hub": "#ffe08a"},
            "L": {"title": "Большая шестерня", "short": "БОЛЬШАЯ", "teeth": 16, "r": 124,
                  "fill": "#48c774", "rim": "#237341", "hub": "#b8f5cd"},
        }

        FIXED_NODES = [
            {"id": "motor", "pos": (660, 455), "size": "M", "role": "motor", "label": "МОТОР", "sub": "ведущий вал"},
            {"id": "out1",  "pos": (1283, 197), "size": "M", "role": "out",   "label": "ШПИНДЕЛЬ", "sub": "верхний узел"},
            {"id": "out2",  "pos": (1218, 455), "size": "M", "role": "out",   "label": "ПОДАЧА",   "sub": "средний узел"},
            {"id": "out3",  "pos": (1378, 723), "size": "S", "role": "out",   "label": "НАСОС СОЖ","sub": "нижний узел"},
        ]

        PINS = [
            {"id": "p1", "pos": (877, 455),  "need": "L"},
            {"id": "p2", "pos": (992, 271),  "need": "M"},
            {"id": "p3", "pos": (1128, 197), "need": "S"},
            {"id": "p4", "pos": (1063, 455), "need": "S"},
            {"id": "p5", "pos": (992, 639),  "need": "M"},
            {"id": "p6", "pos": (1192, 723), "need": "L"},
        ]

        INVENTORY_TEMPLATE = [
            ("g1", "L"), ("g2", "L"),
            ("g3", "M"), ("g4", "M"),
            ("g5", "S"), ("g6", "S"),
        ]

        MESH_TOL = 8.0

        def __init__(self):
            self.reset()

        def reset(self):
            self.placed = {p["id"]: None for p in self.PINS}  # pin_id -> (item_id, size_code)
            self.items = list(self.INVENTORY_TEMPLATE)
            random.shuffle(self.items)
            self.held = None        # (item_id, size_code)
            self.held_from = None   # pin_id or None
            self.sticky = False
            self.drag_pos = (0, 0)
            self.press_pos = (0, 0)
            self.moves = 0
            self.used_help = False
            self.flash_pin = None
            self.flash_until = 0.0
            self.status_hint = "Перетащите шестерни слева на оси редуктора, чтобы запустить все 3 узла станка!"

        def solve(self):
            pool = list(self.INVENTORY_TEMPLATE)
            self.placed = {}
            for p in self.PINS:
                need = p["need"]
                for i, (gid, gsz) in enumerate(pool):
                    if gsz == need:
                        self.placed[p["id"]] = pool.pop(i)
                        break
            self.held = None
            self.held_from = None
            self.sticky = False
            self.used_help = True
            mg_sfx("audio/bun_win.wav")
            self.status_hint = "Работяга осторожно подтолкнул шестерни мизинцем — редуктор собран!"

        def free_items(self):
            used_ids = set(v[0] for v in self.placed.values() if v is not None)
            held_id = self.held[0] if self.held is not None else None
            return [it for it in self.items if it[0] not in used_ids and it[0] != held_id]

        def all_active_gears(self):
            """Возвращает словарь node_id -> {pos, size, teeth, r, role}."""
            nodes = {}
            for fn in self.FIXED_NODES:
                sp = self.GEAR_SPECS[fn["size"]]
                nodes[fn["id"]] = {
                    "pos": fn["pos"],
                    "size": fn["size"],
                    "teeth": sp["teeth"],
                    "r": sp["r"],
                    "role": fn["role"],
                }
            for p in self.PINS:
                val = self.placed.get(p["id"])
                if val is not None:
                    sp = self.GEAR_SPECS[val[1]]
                    nodes[p["id"]] = {
                        "pos": p["pos"],
                        "size": val[1],
                        "teeth": sp["teeth"],
                        "r": sp["r"],
                        "role": "pin",
                    }
            return nodes

        def compute_kinematics(self, motor_angle):
            """Считает углы и вращение всех зацеплённых с мотором шестерней."""
            nodes = self.all_active_gears()
            spinning = {"motor": True}
            angles = {"motor": motor_angle}
            queue = ["motor"]
            qi = 0
            while qi < len(queue):
                cur_id = queue[qi]
                qi += 1
                ca = nodes[cur_id]
                cx, cy = ca["pos"]
                theta1 = angles[cur_id]
                n1 = ca["teeth"]

                for other_id, cb in nodes.items():
                    if other_id in spinning:
                        continue
                    ox, oy = cb["pos"]
                    dist = math.hypot(ox - cx, oy - cy)
                    if abs(dist - (ca["r"] + cb["r"])) <= self.MESH_TOL:
                        phi = math.atan2(oy - cy, ox - cx)
                        n2 = cb["teeth"]
                        angles[other_id] = phi + math.pi - (math.pi - n1 * (phi - theta1)) / float(n2)
                        spinning[other_id] = True
                        queue.append(other_id)

            for nid in nodes:
                if nid not in angles:
                    angles[nid] = 0.0
                    spinning[nid] = False
            return nodes, spinning, angles

        def ok_count(self):
            _nodes, spinning, _angles = self.compute_kinematics(0.0)
            return sum(1 for oid in ("out1", "out2", "out3") if spinning.get(oid, False))

        def is_done(self):
            return self.ok_count() == 3

        def fits_on_pin(self, pin_id, size_code):
            """Проверяет, не перекрываются ли зубья шестерни с соседними шестернями."""
            target_pin = None
            for p in self.PINS:
                if p["id"] == pin_id:
                    target_pin = p
                    break
            if target_pin is None:
                return False
            px, py = target_pin["pos"]
            r_new = self.GEAR_SPECS[size_code]["r"]

            for fn in self.FIXED_NODES:
                fx, fy = fn["pos"]
                r_other = self.GEAR_SPECS[fn["size"]]["r"]
                if math.hypot(px - fx, py - fy) < (r_new + r_other) - self.MESH_TOL:
                    return False

            for p in self.PINS:
                if p["id"] == pin_id:
                    continue
                val = self.placed.get(p["id"])
                if val is None:
                    continue
                ox, oy = p["pos"]
                r_other = self.GEAR_SPECS[val[1]]["r"]
                if math.hypot(px - ox, py - oy) < (r_new + r_other) - self.MESH_TOL:
                    return False
            return True

        def try_place(self, pin_id, st=0.0):
            if self.held is None or self.is_done():
                return
            prev = self.placed.get(pin_id)
            # Временно освобождаем целевую ось для проверки зазоров
            self.placed[pin_id] = None
            if not self.fits_on_pin(pin_id, self.held[1]):
                self.placed[pin_id] = prev
                # Если меняли местами и возврат на старую ось возможен — вернём на старую ось
                if self.held_from is not None and self.placed.get(self.held_from) is None:
                    self.placed[self.held_from] = self.held
                self.held = None
                self.held_from = None
                self.sticky = False
                self.flash_pin = pin_id
                self.flash_until = st + 0.65
                mg_sfx("audio/turnstile_fail.wav")
                self.status_hint = "Слишком крупная шестерня для этой оси — зубья упираются в соседнюю!"
                return

            # Если на целевой оси уже была шестерня и мы тянули с другой оси — пробуем поменять местами
            self.placed[pin_id] = self.held
            if prev is not None and self.held_from is not None and self.held_from != pin_id:
                if self.fits_on_pin(self.held_from, prev[1]):
                    self.placed[self.held_from] = prev

            self.held = None
            self.held_from = None
            self.sticky = False
            self.moves += 1

            if self.is_done():
                mg_sfx("audio/bun_win.wav")
                self.status_hint = "РЕДУКТОР СОБРАН! Все три узла станка вращаются синхронно!"
            else:
                mg_sfx("audio/gear_click.wav")
                cnt = self.ok_count()
                self.status_hint = "Шестерня села на ось! Запущено узлов станка: %d из 3." % cnt

        def drop_back(self):
            self.held = None
            self.held_from = None
            self.sticky = False


    class GearMachineDisplayable(renpy.Displayable):
        W, H = 1860, 910
        TRAY_X, TRAY_Y, TRAY_W, CARD_H, CARD_STEP = 18, 108, 396, 122, 132
        BOX_X, BOX_Y, BOX_W, BOX_H = 436, 12, 1412, 886

        def __init__(self, game, **kwargs):
            super(GearMachineDisplayable, self).__init__(**kwargs)
            self.game = game

        @staticmethod
        def draw_gear(cv, cx, cy, pitch_r, teeth, angle, fill_col, rim_col, hub_col, active=False):
            m = (2.0 * pitch_r) / float(teeth)
            r_tip = pitch_r + 0.70 * m
            r_root = pitch_r - 0.84 * m
            half_p = math.pi / float(teeth)

            pts = []
            for i in range(teeth):
                ca = angle + i * (2.0 * math.pi / float(teeth))
                a0 = ca - 0.68 * half_p
                a1 = ca - 0.34 * half_p
                a2 = ca + 0.34 * half_p
                a3 = ca + 0.68 * half_p
                pts.append((int(cx + math.cos(a0) * r_root), int(cy + math.sin(a0) * r_root)))
                pts.append((int(cx + math.cos(a1) * r_tip),  int(cy + math.sin(a1) * r_tip)))
                pts.append((int(cx + math.cos(a2) * r_tip),  int(cy + math.sin(a2) * r_tip)))
                pts.append((int(cx + math.cos(a3) * r_root), int(cy + math.sin(a3) * r_root)))

            # Тень под шестернёй
            shadow_pts = [(px + 4, py + 5) for (px, py) in pts]
            cv.polygon("#080b0f", shadow_pts)

            # Зубчатый венец
            cv.polygon(fill_col, pts)
            cv.polygon("#11171f", pts, 3)

            # Внутреннее углубление и спицы для наглядности вращения
            inner_r = max(24, int(r_root - 9))
            hole_r = max(16, int(inner_r * 0.68))
            cv.circle(rim_col, (cx, cy), inner_r)
            if inner_r > 38:
                cv.circle("#18212b", (cx, cy), hole_r)
                for k in range(4):
                    sa = angle + k * (math.pi * 0.5)
                    sx = int(cx + math.cos(sa) * (inner_r - 2))
                    sy = int(cy + math.sin(sa) * (inner_r - 2))
                    cv.line(fill_col, (cx, cy), (sx, sy), 11)

            # Ступица и посадочный вал
            hub_r = min(26, max(16, int(pitch_r * 0.28)))
            cv.circle("#0e141b", (cx, cy), hub_r + 3)
            cv.circle("#55ff88" if active else hub_col, (cx, cy), hub_r)
            cv.circle("#1b242e", (cx, cy), 10)

        def tray_item_at(self, x, y):
            free = self.game.free_items()
            for i, it in enumerate(free):
                cy = self.TRAY_Y + i * self.CARD_STEP
                if self.TRAY_X <= x <= self.TRAY_X + self.TRAY_W and cy <= y <= cy + self.CARD_H:
                    return it
            return None

        def pin_at(self, x, y):
            best = None
            best_d = 1e9
            for p in self.game.PINS:
                px, py = p["pos"]
                val = self.game.placed.get(p["id"])
                hit_r = self.game.GEAR_SPECS[val[1]]["r"] + 12 if val else 68
                d = math.hypot(x - px, y - py)
                if d <= hit_r and d < best_d:
                    best = p["id"]
                    best_d = d
            return best

        def render(self, width, height, st, at):
            g = self.game
            motor_angle = st * 1.65
            nodes, spinning, angles = g.compute_kinematics(motor_angle)

            rv = renpy.Render(self.W, self.H)
            cv = rv.canvas()
            cv.rect("#05122c", (0, 0, self.W, self.H))

            # --- Левый лоток с деталями в стиле Persona 3 Reload ---
            cv.rect("#092252", (8, 12, 416, self.H - 24))
            cv.rect("#00d8ff", (8, 12, 416, self.H - 24), 3)
            mg_text(rv, "ШЕСТЕРНИ", 236, 40, 28, "#ffffff", True, align=0.5, st=st, at=at)

            for i, (gid, sz) in enumerate(g.free_items()):
                sp = g.GEAR_SPECS[sz]
                cy = self.TRAY_Y + i * self.CARD_STEP
                cv.rect("#0d3074", (self.TRAY_X, cy, self.TRAY_W, self.CARD_H))
                cv.rect(sp["fill"], (self.TRAY_X, cy, self.TRAY_W, self.CARD_H), 2)
                icon_r = 26 if sz == "S" else (34 if sz == "M" else 42)
                self.draw_gear(cv, self.TRAY_X + 64, cy + self.CARD_H // 2, icon_r, sp["teeth"], 0.2,
                               sp["fill"], sp["rim"], sp["hub"], False)
                mg_text(rv, sp["short"], self.TRAY_X + 128, cy + 44, 25, "#ffffff", True, st=st, at=at)

            # --- Стальной корпус редуктора станка (исходный вид) ---
            cv.rect("#1b222b", (self.BOX_X, self.BOX_Y, self.BOX_W, self.BOX_H))
            cv.rect("#ffcc33", (self.BOX_X, self.BOX_Y, self.BOX_W, self.BOX_H), 4)
            cv.rect("#232c37", (self.BOX_X + 18, self.BOX_Y + 18, self.BOX_W - 36, self.BOX_H - 36))

            # Декоративные болты по углам кожуха
            for bx in (self.BOX_X + 26, self.BOX_X + self.BOX_W - 26):
                for by in (self.BOX_Y + 26, self.BOX_Y + self.BOX_H - 26):
                    cv.circle("#4b5a6b", (bx, by), 9)
                    cv.circle("#141920", (bx, by), 4)

            # --- Подсказывающие масляные каналы между валами ---
            links = [
                ((660, 455), (877, 455)),
                ((877, 455), (992, 271)), ((992, 271), (1128, 197)), ((1128, 197), (1283, 197)),
                ((877, 455), (1063, 455)), ((1063, 455), (1218, 455)),
                ((877, 455), (992, 639)), ((992, 639), (1192, 723)), ((1192, 723), (1378, 723)),
            ]
            for a, b in links:
                cv.line("#171d24", a, b, 18)
                cv.line("#2d3947", a, b, 4)

            # --- Посадочные пустые шпильки (оси) ---
            hover_pin = self.pin_at(*g.drag_pos) if g.held else None
            for p in g.PINS:
                pid = p["id"]
                px, py = p["pos"]
                if g.placed.get(pid) is None:
                    is_flash = (g.flash_pin == pid and st < g.flash_until)
                    ring_col = "#ff4444" if is_flash else ("#ffcc33" if hover_pin == pid else "#5a6e82")
                    cv.circle("#131820", (px, py), 34)
                    cv.circle(ring_col, (px, py), 34, 4)
                    cv.circle("#8da2b8", (px, py), 15)
                    cv.circle("#141a22", (px, py), 7)
                    if g.held is not None:
                        ghost_r = g.GEAR_SPECS[g.held[1]]["r"]
                        if hover_pin == pid:
                            ok_fit = g.fits_on_pin(pid, g.held[1])
                            cv.circle("#55ff88" if ok_fit else "#ff4444", (px, py), ghost_r, 4)

            # --- Отрисовка фиксированных валов (мотор и 3 выходных узла) ---
            for fn in g.FIXED_NODES:
                nid = fn["id"]
                fx, fy = fn["pos"]
                sp = g.GEAR_SPECS[fn["size"]]
                is_spin = spinning.get(nid, False)
                if fn["role"] == "motor":
                    fill_c, rim_c, hub_c = "#e05a33", "#8c2f14", "#ffbb99"
                else:
                    fill_c = "#42b868" if is_spin else "#667382"
                    rim_c = "#206638" if is_spin else "#3c4652"
                    hub_c = "#b8ffd0" if is_spin else "#a5b2c0"
                self.draw_gear(cv, fx, fy, sp["r"], sp["teeth"], angles[nid], fill_c, rim_c, hub_c, is_spin)

                # Короткие лаконичные подписи мотора и выходных узлов
                if fn["role"] == "motor":
                    cv.rect("#121820eb", (fx - 72, fy + 116, 144, 48))
                    cv.rect("#ff7744", (fx - 72, fy + 116, 144, 48), 2)
                    mg_text(rv, fn["label"], fx, fy + 126, 22, "#ff9966", True, align=0.5, st=st, at=at)
                else:
                    lx = fx + sp["r"] + 26
                    cv.rect("#121820eb", (lx, fy - 28, 226, 56))
                    cv.rect("#44ff77" if is_spin else "#ff5555", (lx, fy - 28, 226, 56), 3)
                    cv.circle("#33ff66" if is_spin else "#ff3333", (lx + 26, fy), 12)
                    mg_text(rv, fn["label"], lx + 48, fy - 14, 22, "#66ff88" if is_spin else "#ffffff", True, st=st, at=at)

            # --- Отрисовка установленных игроком шестерней ---
            for p in g.PINS:
                pid = p["id"]
                val = g.placed.get(pid)
                if val is None:
                    continue
                px, py = p["pos"]
                sp = g.GEAR_SPECS[val[1]]
                is_spin = spinning.get(pid, False)
                self.draw_gear(cv, px, py, sp["r"], sp["teeth"], angles[pid],
                               sp["fill"], sp["rim"], sp["hub"], is_spin)

            # --- Шестерня в руке при перетаскивании ---
            if g.held is not None:
                mx, my = g.drag_pos
                sp = g.GEAR_SPECS[g.held[1]]
                drag_layer = renpy.Render(self.W, self.H)
                self.draw_gear(drag_layer.canvas(), int(mx), int(my), sp["r"], sp["teeth"],
                               motor_angle * 0.5, sp["fill"], sp["rim"], "#ffffff", False)
                rv.blit(drag_layer, (0, 0))

            renpy.redraw(self, 0.03)
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.is_done():
                return None

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if not (0 <= x <= self.W and 0 <= y <= self.H):
                    return None
                if g.held is not None and g.sticky:
                    pin = self.pin_at(x, y)
                    if pin:
                        g.try_place(pin, st)
                    else:
                        it = self.tray_item_at(x, y)
                        if g.held_from is not None and g.placed.get(g.held_from) is None and not it:
                            # Сброс обратно в лоток кликом мимо осей
                            g.drop_back()
                        else:
                            g.drop_back()
                            if it:
                                g.held = it
                                g.press_pos = (x, y)
                                g.drag_pos = (x, y)
                    renpy.redraw(self, 0)
                    renpy.restart_interaction()
                    return None

                it = self.tray_item_at(x, y)
                if it:
                    g.held = it
                    g.held_from = None
                else:
                    pin = self.pin_at(x, y)
                    if pin and g.placed.get(pin) is not None:
                        g.held = g.placed[pin]
                        g.placed[pin] = None
                        g.held_from = pin

                if g.held is not None:
                    g.sticky = False
                    g.press_pos = (x, y)
                    g.drag_pos = (x, y)
                    renpy.redraw(self, 0)
                    renpy.restart_interaction()
                return None

            elif ev.type == pygame.MOUSEMOTION and g.held is not None:
                g.drag_pos = (x, y)
                renpy.redraw(self, 0)
                return None

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and g.held is not None and not g.sticky:
                moved = math.hypot(x - g.press_pos[0], y - g.press_pos[1])
                pin = self.pin_at(x, y)
                if pin and moved >= 20 and pin != g.held_from:
                    g.try_place(pin, st)
                elif moved < 20:
                    g.sticky = True
                else:
                    g.drop_back()
                renpy.redraw(self, 0)
                renpy.restart_interaction()
                return None

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                # ПКМ по установленной шестерне быстро снимает её обратно в лоток
                pin = self.pin_at(x, y)
                if pin and g.placed.get(pin) is not None:
                    g.placed[pin] = None
                    g.moves += 1
                    mg_sfx("audio/pc_slide.wav")
                    g.status_hint = "Шестерня снята с оси и возвращена в лоток."
                    renpy.redraw(self, 0)
                    renpy.restart_interaction()
                raise renpy.IgnoreEvent()

            return None


default mg_pipes = GearMachineGame()

# ------------------------------------------------------------------------------
# ЭКРАН: РЕДУКТОР СТАНКА — ШЕСТЕРЁНКИ (НА ВЕСЬ ЭКРАН 1920x1080)
# ------------------------------------------------------------------------------
screen screen_minigame_pipes():
    modal True

    $ gears_ok = mg_pipes.ok_count()

    if gears_ok >= 3:
        timer 1.5 action Return(True)

    fixed:
        xsize 1920
        ysize 1080

        add Solid("#05102a")
        add GearMachineDisplayable(mg_pipes) xpos 30 ypos 22
        add Transform("images/ui/logo_pgt_white.png", size=(52, 52), fit="contain") xpos 54 ypos 48

        hbox:
            xpos 36
            ypos 954
            xsize 1848
            spacing 30

            frame:
                background Frame("images/ui/round_panel.png", 20, 20)
                yalign 0.5
                padding (28, 16)
                text "[gears_ok] / 3" size 30 color ("#7ae8ff" if gears_ok == 3 else "#ffffff") bold True

            if gears_ok < 3:
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 24
                    if mg_pipes.moves >= 12:
                        textbutton "Помощь":
                            action Function(mg_pipes.solve)
                            background Frame("images/ui/round_mg_amber.png", 18, 18)
                            hover_background Frame("images/ui/round_mg_amber_hover.png", 18, 18)
                            text_size 26
                            text_bold True
                            text_color "#ffffff"
                            padding (32, 16)
                    textbutton "Заново":
                        action Function(mg_pipes.reset)
                        background Frame("images/ui/round_btn_idle.png", 18, 18)
                        hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                        text_size 26
                        text_bold True
                        text_color "#ffffff"
                        padding (32, 16)

        # Плашка по центру экрана, когда станок собран верно (исчезает через 1.5 секунды)
        if gears_ok >= 3:
            frame:
                xalign 0.5
                yalign 0.5
                background Frame("images/ui/round_mg_green.png", 24, 24)
                padding (68, 36)
                text "СТАНОК СОБРАН ВЕРНО!" size 44 color "#ffffff" bold True xalign 0.5 text_align 0.5
