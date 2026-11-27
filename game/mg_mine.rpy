## ==============================================================================
## МИНИ-ИГРА: ШАХТНЫЙ ПОЛИГОН В СТИЛЕ BOMBERMAN
## Школьник бегает по штреку, убегает от крыс, закладывает учебные заряды,
## дробит завалы породы и прокапывается к пролому во второй корпус.
## ==============================================================================

init python:

    class MineBomberGame(object):
        ROWS, COLS = 9, 13
        STEP = 0.15          # сек на клетку для игрока
        RAT_STEP = 0.42      # сек на клетку для крысы
        RAT_GNAW_STEP = 0.92 # сек на прогрызание блока породы крысой
        FUSE = 2.0           # время горения фитиля
        BLAST_T = 0.45       # длительность вспышки
        RADIUS = 2
        MAX_CHARGES = 2
        DR = [-1, 0, 1, 0]
        DC = [0, 1, 0, -1]
        RAT_STARTS = [(0, 12), (8, 0), (4, 6), (6, 10)]

        def __init__(self):
            self.reset()

        def reset(self):
            rng = random.Random(1987)
            self.exit = (self.ROWS - 1, self.COLS - 1)
            keep_free = set([(0, 0), (0, 1), (1, 0), (0, 2), (2, 0), self.exit])
            rat_clear = set([(0, 12), (0, 11), (8, 0), (8, 1), (4, 6), (4, 5), (4, 7), (6, 10), (6, 9)])
            self.rock = set()
            for r in range(self.ROWS):
                for c in range(self.COLS):
                    if self.is_pillar(r, c) or (r, c) in keep_free or (r, c) in rat_clear:
                        continue
                    if rng.random() < 0.62:
                        self.rock.add((r, c))
            # Пролом во 2-й корпус всегда завален породой
            self.rock.add((self.ROWS - 1, self.COLS - 2))
            self.rock.add((self.ROWS - 2, self.COLS - 1))

            self.rats = []
            for (r, c) in self.RAT_STARTS:
                self.rats.append({"r": r, "c": c, "pr": r, "pc": c, "t": 1.0, "d": rng.randint(0, 3), "step_dur": self.RAT_STEP, "alive": True})
            self.p_cell = (0, 0)
            self.p_prev = (0, 0)
            self.pt = 1.0
            self.p_face = 1
            self.p_dir = 2
            self.charges = []
            self.blasts = []
            self.crumbles = []
            self.last_gnaw_sfx = -1.0
            self.gnaw_warned = False
            self.held = []
            self.auto_path = []
            self.hits = 0
            self.rocks_broken = 0
            self.invuln = 0.0
            self.time = 0.0
            self.done = False
            self.need_refresh = False
            self.message = "Закладывайте заряд (ПРОБЕЛ) у завала и отбегайте за крепь! Цель — пролом во 2-й корпус в правом нижнем углу."

        def is_pillar(self, r, c):
            return r % 2 == 1 and c % 2 == 1

        def in_bounds(self, r, c):
            return 0 <= r < self.ROWS and 0 <= c < self.COLS

        def charge_at(self, r, c):
            for b in self.charges:
                if b["r"] == r and b["c"] == c:
                    return True
            return False

        def walkable(self, r, c):
            return self.in_bounds(r, c) and not self.is_pillar(r, c) and (r, c) not in self.rock and not self.charge_at(r, c)

        def rats_left(self):
            return sum(1 for rt in self.rats if rt["alive"])

        def place_charge(self):
            if self.done:
                return
            r, c = self.p_cell
            if self.charge_at(r, c):
                return
            if len(self.charges) >= self.MAX_CHARGES:
                self.message = "Больше двух зарядов одновременно нельзя — техника безопасности!"
                return
            self.charges.append({"r": r, "c": c, "t": self.FUSE})
            mg_sfx("audio/bomb_place.wav")
            self.message = "Фитиль горит! Бегите за угол крепи!"

        def _move_to(self, cell):
            dr = cell[0] - self.p_cell[0]
            dc = cell[1] - self.p_cell[1]
            if dr < 0:
                self.p_dir = 0
            elif dc > 0:
                self.p_dir = 1
                self.p_face = 1
            elif dr > 0:
                self.p_dir = 2
            elif dc < 0:
                self.p_dir = 3
                self.p_face = -1
            self.p_prev = self.p_cell
            self.p_cell = cell
            self.pt = 0.0

        def try_move(self, d):
            self.p_dir = d
            if d == 1:
                self.p_face = 1
            elif d == 3:
                self.p_face = -1
            r, c = self.p_cell
            nr, nc = r + self.DR[d], c + self.DC[d]
            if self.walkable(nr, nc):
                self._move_to((nr, nc))

        def path_to(self, target):
            """Поиск пути в ширину по свободным клеткам (для управления мышкой)."""
            start = self.p_cell
            if target == start:
                return []
            prev = {start: None}
            queue = [start]
            qi = 0
            while qi < len(queue):
                cur = queue[qi]
                qi += 1
                if cur == target:
                    break
                for d in range(4):
                    nb = (cur[0] + self.DR[d], cur[1] + self.DC[d])
                    if nb not in prev and self.walkable(*nb):
                        prev[nb] = cur
                        queue.append(nb)
            if target not in prev:
                return None
            path = []
            cur = target
            while cur != start:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path

        def click_cell(self, r, c):
            if self.done:
                return
            if (r, c) == self.p_cell:
                self.place_charge()
                return
            path = self.path_to((r, c))
            if path:
                self.auto_path = path
            else:
                self.message = "Туда не пройти — путь завален породой. Сначала раздробите завал!"

        def detonate(self, b):
            self.charges = [x for x in self.charges if x is not b]
            cells = [(b["r"], b["c"])]
            for d in range(4):
                for k in range(1, self.RADIUS + 1):
                    nr, nc = b["r"] + self.DR[d] * k, b["c"] + self.DC[d] * k
                    if not self.in_bounds(nr, nc) or self.is_pillar(nr, nc):
                        break
                    cells.append((nr, nc))
                    if (nr, nc) in self.rock:
                        self.rock.discard((nr, nc))
                        self.rocks_broken += 1
                        break
                    for ob in self.charges:
                        if ob["r"] == nr and ob["c"] == nc:
                            ob["t"] = min(ob["t"], 0.05)
            self.blasts.append({"cells": cells, "t": self.BLAST_T})
            mg_sfx("audio/bomb_explosion.wav")

        def knock_back(self, why):
            self.hits += 1
            self.p_cell = (0, 0)
            self.p_prev = (0, 0)
            self.pt = 1.0
            self.invuln = 2.2
            self.auto_path = []
            mg_sfx("audio/stealth_spotted.wav")
            self.message = why

        def update(self, dt, d):
            if self.done:
                return
            self.time += dt
            if self.invuln > 0:
                self.invuln = max(0.0, self.invuln - dt)

            # Игрок
            if self.pt < 1.0:
                self.pt = min(1.0, self.pt + dt / self.STEP)
            if self.pt >= 1.0:
                if d is not None:
                    self.auto_path = []
                    self.try_move(d)
                elif self.auto_path:
                    nxt = self.auto_path.pop(0)
                    adj = abs(nxt[0] - self.p_cell[0]) + abs(nxt[1] - self.p_cell[1]) == 1
                    if adj and self.walkable(*nxt):
                        self._move_to(nxt)
                    else:
                        self.auto_path = []

            # Заряды и вспышки
            for b in list(self.charges):
                b["t"] -= dt
                if b["t"] <= 0:
                    self.detonate(b)
            alive = []
            for f in self.blasts:
                f["t"] -= dt
                if f["t"] > 0:
                    alive.append(f)
            self.blasts = alive
            self.crumbles = [cr for cr in self.crumbles if cr["t"] - dt > 0]
            for cr in self.crumbles:
                cr["t"] -= dt
            hot = set()
            for f in self.blasts:
                for cell in f["cells"]:
                    hot.add(tuple(cell))

            # Крысы (могут разгрызать и ломать блоки породы при столкновении!)
            for rat in self.rats:
                if not rat["alive"]:
                    continue
                if (rat["r"], rat["c"]) in hot:
                    rat["alive"] = False
                    mg_sfx("audio/wire_snap.wav")
                    left = self.rats_left()
                    if left:
                        self.message = "Крысу сдуло взрывной волной! Осталось крыс: %d." % left
                    else:
                        self.message = "Все крысы разбежались из штрека! Теперь — к пролому!"
                    continue
                step_dur = rat.get("step_dur", self.RAT_STEP)
                if rat["t"] < 1.0:
                    rat["t"] = min(1.0, rat["t"] + dt / step_dur)
                    continue

                free_opts = []
                rock_opts = []
                for k in range(4):
                    nr, nc = rat["r"] + self.DR[k], rat["c"] + self.DC[k]
                    if not self.in_bounds(nr, nc) or self.is_pillar(nr, nc) or self.charge_at(nr, nc) or (nr, nc) in hot:
                        continue
                    if (nr, nc) in self.rock:
                        # Оставляем старт (0,0) и выход неприкосновенными в первые пару секунд
                        if self.time > 1.0:
                            rock_opts.append(k)
                    else:
                        free_opts.append(k)

                d_fwd = rat["d"]
                k = None
                # Если прямо по курсу крысы блок породы — она с разбегу врезается и прогрызает его!
                if d_fwd in rock_opts and (not free_opts or random.random() < 0.42):
                    k = d_fwd
                elif not free_opts and rock_opts:
                    k = random.choice(rock_opts)
                elif rock_opts and random.random() < 0.10:
                    k = random.choice(rock_opts)
                elif free_opts:
                    if d_fwd in free_opts and random.random() < 0.72:
                        k = d_fwd
                    else:
                        k = random.choice(free_opts)

                if k is None:
                    continue

                nr, nc = rat["r"] + self.DR[k], rat["c"] + self.DC[k]
                if (nr, nc) in self.rock:
                    self.rock.discard((nr, nc))
                    self.rocks_broken += 1
                    self.crumbles.append({"r": nr, "c": nc, "t": 0.42})
                    if self.time - self.last_gnaw_sfx >= 0.35:
                        mg_sfx("audio/drill_hit.wav")
                        self.last_gnaw_sfx = self.time
                    if not self.gnaw_warned:
                        self.gnaw_warned = True
                        self.message = "Крысы врезаются в завалы породы и прогрызают блоки насквозь!"
                    rat["step_dur"] = self.RAT_GNAW_STEP
                else:
                    rat["step_dur"] = self.RAT_STEP

                rat["d"] = k
                rat["pr"], rat["pc"] = rat["r"], rat["c"]
                rat["r"], rat["c"] = nr, nc
                rat["t"] = 0.0

            # Столкновения с игроком
            if self.invuln <= 0:
                if self.p_cell in hot:
                    self.knock_back("БАХ! Задело собственным зарядом. Каска спасла, но придётся начать от входа в штрек!")
                else:
                    for rat in self.rats:
                        if rat["alive"] and (rat["r"], rat["c"]) == self.p_cell:
                            self.knock_back("Крыса цапнула за ботинок! Вы с визгом убежали обратно ко входу в штрек.")
                            break

            # Победа
            if self.p_cell == self.exit and self.pt >= 1.0:
                self.done = True
                self.charges = []
                self.held = []
                mg_sfx("audio/drill_breakthrough.wav")
                self.message = "ВЫ ПРОКОПАЛИСЬ К ПРОЛОМУ ВО ВТОРОЙ КОРПУС!"
                self.need_refresh = True


    class MineBomberDisplayable(renpy.Displayable):
        TOP, CELL = 56, 100

        def __init__(self, game, **kwargs):
            super(MineBomberDisplayable, self).__init__(**kwargs)
            self.game = game
            self.W = game.COLS * self.CELL
            self.H = self.TOP + game.ROWS * self.CELL
            self.last_st = None
            self.im_beton = Image("images/mg/mine_beton.png")
            self.im_dirt_light = Image("images/mg/mine_dirt_light.png")
            self.im_dirt_dark = Image("images/mg/mine_dirt_dark.png")
            self.im_ugeli = Image("images/mg/mine_ugeli.png")
            self.im_rats = {
                0: [Image("images/mg/rat_0_%d.png" % i) for i in range(11)],
                1: [Image("images/mg/rat_1_%d.png" % i) for i in range(8)],
                2: [Image("images/mg/rat_2_%d.png" % i) for i in range(11)],
                3: [Image("images/mg/rat_3_%d.png" % i) for i in range(8)],
            }
            self.im_miner = {
                d: [Image("images/mg/miner_%d_%d.png" % (d, i)) for i in range(4)]
                for d in range(4)
            }

        def cell_xy(self, r, c):
            return (int(c * self.CELL + self.CELL / 2), int(self.TOP + r * self.CELL + self.CELL / 2))

        def _static_arena_render(self, st, at):
            g = self.game
            C = self.CELL
            T = self.TOP
            def _build(rv, _st, _at):
                mg_solid(rv, "#061433", 0, 0, self.W, self.H, _st, _at)
                mg_solid(rv, "#0b2866", 0, 0, self.W, T - 4, _st, _at)
                mg_solid(rv, "#00d8ff", 0, T - 4, self.W, 4, _st, _at)
                r_beton = renpy.render(self.im_beton, C, C, _st, _at)
                r_dirt_light = renpy.render(self.im_dirt_light, C, C, _st, _at)
                r_dirt_dark = renpy.render(self.im_dirt_dark, C, C, _st, _at)
                for r in range(g.ROWS):
                    for c in range(g.COLS):
                        x, y = c * C, T + r * C
                        rv.blit(r_dirt_light if (r + c) % 2 == 0 else r_dirt_dark, (x, y))
                        if g.is_pillar(r, c):
                            rv.blit(r_beton, (x, y))
                ex_x, ex_y = g.exit[1] * C, T + g.exit[0] * C
                mg_solid(rv, "#123d29cc", ex_x + 6, ex_y + 6, C - 12, C - 12, _st, _at)
                mg_solid(rv, "#44ff99", ex_x + 4, ex_y + 4, C - 8, 5, _st, _at)
                mg_solid(rv, "#44ff99", ex_x + 4, ex_y + C - 9, C - 8, 5, _st, _at)
                mg_solid(rv, "#44ff99", ex_x + 4, ex_y + 9, 5, C - 18, _st, _at)
                mg_solid(rv, "#44ff99", ex_x + C - 9, ex_y + 9, 5, C - 18, _st, _at)
                mg_text(rv, "ВЫХОД", ex_x + C // 2, ex_y + C // 2 - 13, 20, "#aaffcc", True, align=0.5, st=_st, at=_at)
            layer = MGStaticLayer.get(("mine_static_arena",), self.W, self.H, _build)
            return renpy.render(layer, self.W, self.H, st, at)

        @staticmethod
        def _bomb_sprite_render(spark_idx, st, at):
            S = 88
            key = ("mine_bomb_spr", spark_idx)
            def _build(r, _st, _at):
                cv = r.canvas()
                cx, cy = 44, 48
                pulse = 28 if spark_idx == 0 else 32
                cv.circle("#000000", (cx, cy), pulse + 3)
                cv.circle("#1b1b1b", (cx, cy), pulse)
                cv.circle("#555555", (cx - 9, cy - 9), 8)
                cv.line("#c8a165", (cx + 10, cy - 22), (cx + 22, cy - 38), 4)
                cv.circle("#ffdd33" if spark_idx == 0 else "#ff5522", (cx + 23, cy - 40), 8)
            layer = MGStaticLayer.get(key, S, S, _build)
            return renpy.render(layer, S, S, st, at)

        def render(self, width, height, st, at):
            g = self.game
            dt = 0.0 if self.last_st is None else max(0.0, min(0.05, st - self.last_st))
            self.last_st = st
            g.update(dt, g.held[-1][1] if g.held else None)

            C = self.CELL
            T = self.TOP
            rv = renpy.Render(self.W, self.H)
            rv.blit(self._static_arena_render(st, at), (0, 0))

            r_ugeli = renpy.render(self.im_ugeli, C, C, st, at)
            for (r, c) in g.rock:
                rv.blit(r_ugeli, (c * C, T + r * C))

            # Осколки угля, разгрызенного крысами (без полноэкранного canvas)
            for cr in g.crumbles:
                cx, cy = self.cell_xy(cr["r"], cr["c"])
                prog = 1.0 - max(0.0, cr["t"]) / 0.42
                rad_out = 10 + int(prog * 36)
                sz = max(4, int(12 * (1.0 - prog * 0.5)))
                for k in range(6):
                    ang = k * 1.047 + 0.3
                    px = int(cx + math.cos(ang) * rad_out) - sz // 2
                    py = int(cy + math.sin(ang) * rad_out) - sz // 2
                    mg_solid(rv, "#3a3a42" if k % 2 == 0 else "#1e1e24", px, py, sz, sz, st, at)

            # Вспышки (через GPU Solid)
            for f in g.blasts:
                for (r, c) in f["cells"]:
                    x, y = c * C, T + r * C
                    mg_solid(rv, "#ff7a1a", x + 5, y + 5, C - 10, C - 10, st, at)
                    mg_solid(rv, "#ffe066", x + 22, y + 22, C - 44, C - 44, st, at)

            # Заряды с горящим фитилём (закэшированный на GPU спрайт)
            spark_idx = int(g.time * 10) % 2
            for b in g.charges:
                cx, cy = self.cell_xy(b["r"], b["c"])
                rv.blit(self._bomb_sprite_render(spark_idx, st, at), (cx - 44, cy - 44))

            # Крысы (анимация mish по 4 направлениям)
            for rat in g.rats:
                if not rat["alive"]:
                    continue
                t = rat["t"]
                fr = rat["pr"] + (rat["r"] - rat["pr"]) * t
                fc = rat["pc"] + (rat["c"] - rat["pc"]) * t
                cx = int(fc * C + C / 2)
                cy = int(T + fr * C + C / 2)
                rd = rat.get("d", 2)
                frames = self.im_rats.get(rd, self.im_rats[2])
                f_idx = int(t * len(frames) + g.time * 8) % len(frames)
                r_rat = renpy.render(frames[f_idx], 92, 92, st, at)
                rv.blit(r_rat, (cx - 46, cy - 46))

            # Шахтёр (анимация ходьбы в 4 стороны)
            t = g.pt
            pr = g.p_prev[0] + (g.p_cell[0] - g.p_prev[0]) * t
            pc = g.p_prev[1] + (g.p_cell[1] - g.p_prev[1]) * t
            cx = int(pc * C + C / 2)
            cy = int(T + pr * C + C / 2)
            if not (g.invuln > 0 and int(g.time * 12) % 2 == 0):
                p_dir = getattr(g, "p_dir", 2)
                m_frames = self.im_miner.get(p_dir, self.im_miner[2])
                if t < 0.85:
                    m_idx = 1 if ((g.p_cell[0] + g.p_cell[1]) % 2 == 0) else 3
                elif g.held or g.auto_path:
                    m_idx = int(g.time * 10) % 4
                else:
                    m_idx = 0
                r_miner = renpy.render(m_frames[m_idx], 92, 92, st, at)
                rv.blit(r_miner, (cx - 46, cy - 48))

            # Лаконичный HUD
            hud = "Заряды: %d / %d      Крысы: %d      Уголь: %d" % (
                g.MAX_CHARGES - len(g.charges), g.MAX_CHARGES, g.rats_left(), g.rocks_broken)
            mg_text(rv, hud, self.W // 2, 11, 26, "#ffffff", True, align=0.5, st=st, at=at)

            if not g.done:
                renpy.redraw(self, 0.022)

            if g.need_refresh:
                renpy.timeout(0)
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.need_refresh:
                g.need_refresh = False
                renpy.restart_interaction()
            if g.done:
                return None

            if ev.type in (pygame.KEYDOWN, pygame.KEYUP):
                if mg_handle_held_keys(g, ev):
                    raise renpy.IgnoreEvent()
                if ev.type == pygame.KEYDOWN:
                    u = (getattr(ev, "unicode", "") or "").lower()
                    if mg_is_space(ev) or ev.key == pygame.K_e or u in ("e", "у"):
                        g.place_charge()
                        raise renpy.IgnoreEvent()
                return None

            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and 0 <= x < self.W and self.TOP <= y < self.H:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    r = int((y - self.TOP) // self.CELL)
                    c = int(x // self.CELL)
                    if ev.button == 1:
                        g.click_cell(r, c)
                    elif ev.button == 3:
                        g.place_charge()
                if ev.button == 3:
                    raise renpy.IgnoreEvent()
            return None


default mg_mine = MineBomberGame()

# ------------------------------------------------------------------------------
# ЭКРАН: ШАХТНЫЙ ПОЛИГОН (НА ВЕСЬ ЭКРАН 1920x1080 + СЕНСОРНОЕ УПРАВЛЕНИЕ)
# ------------------------------------------------------------------------------
screen screen_minigame_mine():
    modal True

    if mg_mine.done:
        timer 1.5 action Return(True)

    fixed:
        xsize 1920
        ysize 1080

        if renpy.loadable("images/bg/poligon.webp"):
            add Transform("images/bg/poligon.webp", size=(1920, 1080), fit="cover", matrixcolor=BrightnessMatrix(-0.52))
        else:
            add Solid("#130e0b")

        # Центральное поле шахты 1300 x 956
        add MineBomberDisplayable(mg_mine) xpos 310 ypos 52
        add Transform("images/ui/logo_pgt_white.png", size=(116, 116), fit="contain") xpos 28 ypos 22

        # Слева сверху: скруглённая кнопка сброса в стиле Persona 3 Reload
        if not mg_mine.done:
            textbutton "Заново":
                xpos 26
                ypos 154
                xsize 258
                action Function(mg_mine.reset)
                keyboard_focus False
                background Frame("images/ui/round_btn_idle.png", 20, 20)
                hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                text_size 26
                text_bold True
                text_color "#ffffff"
                text_xalign 0.5
                padding (18, 22)

            # Слева снизу: крестовина из FOTOVSTAVIT2
            add MGTouchPad(mg_mine, size=258) xpos 26 ypos 750

            # Справа снизу: кнопка B из FOTOVSTAVIT2 (затемняется при нажатии)
            add MGBombButton(mg_mine, size=248) xpos 1640 ypos 755
        else:
            # Полупрозрачная табличка посередине экрана по всей ширине (как в сборке сайта) + переход через 1.5 сек
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
                    text "ПРОЛОМ ОТКРЫТ!" size 46 color "#ffffff" bold True xalign 0.5 yalign 0.5 text_align 0.5
                    add Solid("#00e5ff") xsize 1920 ysize 4 yalign 1.0

            button:
                xsize 1920
                ysize 1080
                background None
                action Return(True)
