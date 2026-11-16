## ==============================================================================
## МИНИ-ИГРА: ПРОВОДКА НИКОЛЫ ТЕСЛЫ (В ДУХЕ ПАЗЛОВ ULTRAKILL / THE TALOS PRINCIPLE)
## Провод каждой фазы идёт от клеммы к клемме через свои обязательные точки.
## Провода не должны пересекаться — иначе игрока бьёт током.
## Сбоку — памятка по технике безопасности (чтобы к нам вопросов не было).
## ==============================================================================

init python:

    class WiringGame(object):
        N = 7
        ORDER = ["A", "B", "C", "N"]
        # Цветовая маркировка: A — жёлтый, B — зелёный, C — красный, N (ноль) — синий
        PHASES = {
            "A": {"name": "Фаза A", "col": "#ffdd33"},
            "B": {"name": "Фаза B", "col": "#44dd66"},
            "C": {"name": "Фаза C", "col": "#ff4444"},
            "N": {"name": "Ноль N", "col": "#3399ff"},
        }
        TERMINALS = {
            "C": [(0, 0), (6, 6)],
            "N": [(6, 0), (1, 5)],
            "A": [(5, 1), (2, 5)],
            "B": [(4, 4), (2, 4)],
        }
        CHECKPOINTS = {
            "C": [(0, 5), (4, 6)],
            "N": [(3, 0)],
            "A": [(5, 3)],
            "B": [(3, 2)],
        }

        def __init__(self):
            self.reset()

        def reset(self):
            self.tb_signed = False
            self.shocks = 0
            self.clear_wires()

        def clear_wires(self):
            self.paths = {}
            for k in self.ORDER:
                self.paths[k] = []
            self.drawing = None
            self.shock_left = 0.0
            if self.tb_signed:
                self.message = "Тяните провод мышкой от клеммы к клемме того же цвета через все свои контрольные ромбы!"
            else:
                self.message = "Сначала изучите памятку по ТБ справа и распишитесь в журнале инструктажа!"

        def sign(self):
            self.tb_signed = True
            mg_sfx("audio/wire_snap.wav")
            self.message = "Инструктаж пройден, подпись в журнале стоит. Щит под напряжением — тяните провода!"

        def terminal_at(self, cell):
            for k, v in self.TERMINALS.items():
                if cell in v:
                    return k
            return None

        def checkpoint_at(self, cell):
            for k, v in self.CHECKPOINTS.items():
                if cell in v:
                    return k
            return None

        def owner_at(self, cell):
            for k, p in self.paths.items():
                if cell in p:
                    return k
            return None

        def ends_connected(self, k):
            p = self.paths[k]
            t = self.TERMINALS[k]
            return len(p) >= 2 and p[0] in t and p[-1] in t and p[0] != p[-1]

        def is_complete(self, k):
            return self.ends_connected(k) and all(cp in self.paths[k] for cp in self.CHECKPOINTS.get(k, []))

        def complete_count(self):
            return sum(1 for k in self.ORDER if self.is_complete(k))

        def is_done(self):
            return self.complete_count() == len(self.ORDER)

        def start_draw(self, cell):
            t = self.terminal_at(cell)
            if t is not None:
                self.paths[t] = [cell]
                self.drawing = t
                self.message = "Тянем провод: %s. Не задевайте чужие провода и клеммы!" % self.PHASES[t]["name"]
                return
            o = self.owner_at(cell)
            if o is not None:
                p = self.paths[o]
                del p[p.index(cell) + 1:]
                self.drawing = o
                self.message = "Продолжаем провод: %s." % self.PHASES[o]["name"]
                return
            self.message = "Начинайте провод с клеммы (большой кружок с буквой) или с конца уже проложенного провода."

        def extend_to(self, cell):
            """Ведёт провод к клетке под курсором по шагам. True — произошло важное событие."""
            important = False
            guard = 0
            while self.drawing is not None and guard < 30:
                guard += 1
                k = self.drawing
                last = self.paths[k][-1]
                if cell == last:
                    break
                dr, dc = cell[0] - last[0], cell[1] - last[1]
                if abs(dr) >= abs(dc):
                    step = (last[0] + (1 if dr > 0 else -1), last[1])
                else:
                    step = (last[0], last[1] + (1 if dc > 0 else -1))
                res = self._step(k, step)
                if res == "shock":
                    important = True
                    break
                if res == "stop":
                    break
                if res == "complete":
                    important = True
            return important

        def _step(self, k, c):
            p = self.paths[k]
            if len(p) >= 2 and c == p[-2]:
                p.pop()
                return "ok"
            if c in p:
                del p[p.index(c) + 1:]
                return "ok"
            if self.ends_connected(k):
                return "stop"
            t = self.terminal_at(c)
            if t is not None and t != k:
                return self.shock(k, "Провод коснулся клеммы «%s»!" % self.PHASES[t]["name"])
            o = self.owner_at(c)
            if o is not None and o != k:
                return self.shock(k, "%s пересеклась с проводом «%s» — короткое замыкание!" % (self.PHASES[k]["name"], self.PHASES[o]["name"]))
            cp = self.checkpoint_at(c)
            if cp is not None and cp != k:
                return self.shock(k, "Провод залез на контрольную точку чужой фазы!")
            p.append(c)
            if t == k:
                mg_sfx("audio/wire_snap.wav")
                if self.is_complete(k):
                    self.message = "ЩЁЛК! %s подключена правильно!" % self.PHASES[k]["name"]
                else:
                    self.message = "%s дошла до клеммы, но пропустила обязательную точку! Перетяните провод." % self.PHASES[k]["name"]
                return "complete"
            return "ok"

        def shock(self, k, why):
            self.shocks += 1
            self.shock_left = 0.8
            self.paths[k] = []
            self.drawing = None
            mg_sfx("audio/electric_shock.wav")
            self.message = "БЗЗЗТ! УДАР ТОКОМ! " + why + " Провод сгорел — прокладывайте заново."
            return "shock"

        def finish_draw(self):
            self.drawing = None
            if self.is_done():
                mg_sfx("audio/bun_win.wav")
                self.message = "ВСЕ ФАЗЫ И НОЛЬ РАЗВЕДЕНЫ БЕЗ ПЕРЕСЕЧЕНИЙ! Можно включать рубильник."


    class WiringDisplayable(renpy.Displayable):
        M, CELL = 20, 136

        def __init__(self, game, **kwargs):
            super(WiringDisplayable, self).__init__(**kwargs)
            self.game = game
            self.size = self.M * 2 + self.CELL * game.N
            self.last_st = None

        def center(self, cell):
            return (self.M + cell[1] * self.CELL + self.CELL // 2, self.M + cell[0] * self.CELL + self.CELL // 2)

        def cell_at(self, x, y):
            if x < self.M or y < self.M:
                return None
            c = int((x - self.M) // self.CELL)
            r = int((y - self.M) // self.CELL)
            if 0 <= r < self.game.N and 0 <= c < self.game.N:
                return (r, c)
            return None

        def render(self, width, height, st, at):
            g = self.game
            S = self.size
            dt = 0.0 if self.last_st is None else max(0.0, min(0.1, st - self.last_st))
            self.last_st = st
            if g.shock_left > 0:
                g.shock_left = max(0.0, g.shock_left - dt)

            rv = renpy.Render(S, S)
            board = renpy.Render(S, S)
            cv = board.canvas()
            cv.rect("#10161f", (0, 0, S, S))
            cv.rect("#2b3a4f", (3, 3, S - 6, S - 6), 4)
            for r in range(g.N):
                for c in range(g.N):
                    x0, y0 = self.M + c * self.CELL, self.M + r * self.CELL
                    cv.rect("#16202c", (x0 + 3, y0 + 3, self.CELL - 6, self.CELL - 6), 1)
                    cv.circle("#223042", self.center((r, c)), 9)

            # Провода
            for k in g.ORDER:
                p = g.paths[k]
                col = g.PHASES[k]["col"]
                if len(p) >= 2:
                    pts = [self.center(cell) for cell in p]
                    for i in range(len(pts) - 1):
                        cv.line("#05080c", pts[i], pts[i + 1], 42)
                    for i in range(len(pts) - 1):
                        cv.line(col, pts[i], pts[i + 1], 26)
                    for pt in pts:
                        cv.circle(col, pt, 13)

            # Обязательные точки
            for k, cps in g.CHECKPOINTS.items():
                col = g.PHASES[k]["col"]
                for cell in cps:
                    cx, cy = self.center(cell)
                    cv.polygon("#05080c", mg_pts([(cx, cy - 40), (cx + 40, cy), (cx, cy + 40), (cx - 40, cy)]))
                    dia = mg_pts([(cx, cy - 33), (cx + 33, cy), (cx, cy + 33), (cx - 33, cy)])
                    cv.polygon(col, dia, 0 if cell in g.paths[k] else 6)

            # Клеммы
            for k, terms in g.TERMINALS.items():
                col = g.PHASES[k]["col"]
                for cell in terms:
                    cx, cy = self.center(cell)
                    cv.circle("#05080c", (cx, cy), 52)
                    cv.circle(col, (cx, cy), 46)
                    cv.circle("#141b26", (cx, cy), 29)
                    mg_text(board, k, cx, cy - 21, 36, col, True, align=0.5, st=st, at=at)

            ox, oy = 0, 0
            if g.shock_left > 0.2:
                ox, oy = random.randint(-14, 14), random.randint(-14, 14)
            rv.blit(board, (ox, oy))

            # Эффект удара током
            if g.shock_left > 0:
                fx = renpy.Render(S, S)
                fc = fx.canvas()
                alpha = int(210 * min(1.0, g.shock_left / 0.8))
                fc.rect("#bfe9ff%02x" % alpha, (0, 0, S, S))
                for _ in range(6):
                    pts = [(random.randint(0, S), 0)]
                    while pts[-1][1] < S:
                        pts.append((pts[-1][0] + random.randint(-65, 65), pts[-1][1] + random.randint(45, 95)))
                    fc.lines("#ffffff", False, mg_pts(pts), 6)
                    fc.lines("#3399ff", False, mg_pts(pts), 3)
                mg_text(fx, "КЗ!", S // 2, S // 2 - 42, 68, "#0b2a66", True, align=0.5, st=st, at=at)
                rv.blit(fx, (0, 0))
                renpy.redraw(self, 0)

            # Пока нет подписи в журнале — щит закрыт
            if not g.tb_signed:
                ov = renpy.Render(S, S)
                ov.canvas().rect("#000000c8", (0, 0, S, S))
                mg_text(ov, "ДОПУСК ЗАКРЫТ", S // 2, S // 2 - 52, 42, "#ffcc00", True, align=0.5, st=st, at=at)
                mg_text(ov, "Распишитесь справа", S // 2, S // 2 + 12, 28, "#ffffff", True, align=0.5, st=st, at=at)
                rv.blit(ov, (0, 0))
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.is_done():
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                cell = self.cell_at(x, y)
                if cell is None:
                    return None
                if not g.tb_signed:
                    mg_sfx("audio/turnstile_fail.wav")
                    renpy.restart_interaction()
                    return None
                g.start_draw(cell)
                renpy.redraw(self, 0)
                renpy.restart_interaction()
            elif ev.type == pygame.MOUSEMOTION and g.drawing is not None:
                cell = self.cell_at(x, y)
                if cell is not None:
                    if g.extend_to(cell):
                        renpy.restart_interaction()
                    renpy.redraw(self, 0)
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and g.drawing is not None:
                g.finish_draw()
                renpy.redraw(self, 0)
                renpy.restart_interaction()
            return None


default mg_wiring = WiringGame()

# ------------------------------------------------------------------------------
# ЭКРАН: ПРОВОДКА НИКОЛЫ ТЕСЛЫ (НА ВЕСЬ ЭКРАН 1920x1080)
# ------------------------------------------------------------------------------
screen screen_minigame_wiring():
    modal True

    $ wires_ok = mg_wiring.complete_count()

    fixed:
        xsize 1920
        ysize 1080

        add Solid("#090d16")

        add WiringDisplayable(mg_wiring) xpos 44 ypos 44

        # Правая панель: краткий журнал ТБ + статус + крупные кнопки
        frame:
            xpos 1076
            ypos 44
            xsize 800
            ysize 992
            background Solid("#1c1a12f5")
            padding (36, 32)

            vbox:
                spacing 24
                xfill True
                yfill True

                text "ТЕХНИКА БЕЗОПАСНОСТИ" size 32 color "#ffcc00" bold True xalign 0.5

                frame:
                    background Solid("#282314")
                    xfill True
                    padding (24, 20)
                    vbox:
                        spacing 14
                        text "1. Соединить одноимённые клеммы (A, B, C, N)" size 23 color "#f5ebd2"
                        text "2. Пройти через все свои контрольные ромбы" size 23 color "#88ddff" bold True
                        text "3. Не пересекать провода!" size 23 color "#ff9988" bold True

                if not mg_wiring.tb_signed:
                    frame:
                        background Solid("#4a3808")
                        xfill True
                        padding (8, 8)
                        textbutton "РАСПИСАТЬСЯ В ЖУРНАЛЕ":
                            action Function(mg_wiring.sign)
                            xfill True
                            text_size 28
                            text_bold True
                            text_color "#ffea66"
                            text_xalign 0.5
                            padding (24, 26)
                else:
                    frame:
                        background Solid("#143320")
                        xfill True
                        padding (22, 18)
                        text "ДОПУСК ПОЛУЧЕН" size 26 color "#66ff88" bold True xalign 0.5

                frame:
                    background Solid("#121822")
                    xfill True
                    padding (26, 22)
                    vbox:
                        spacing 14
                        text "Цепи: [wires_ok] / 4" size 32 color ("#66ff88" if wires_ok == 4 else "#ffdd66") bold True
                        text "Разряды: [mg_wiring.shocks]" size 26 color "#ff8866" bold True

                null height 20

                if wires_ok < 4:
                    frame:
                        background Solid("#222d3d")
                        xfill True
                        padding (8, 8)
                        textbutton "Снять провода":
                            action Function(mg_wiring.clear_wires)
                            xfill True
                            text_size 28
                            text_bold True
                            text_xalign 0.5
                            padding (24, 22)
                else:
                    frame:
                        background Solid("#154d2b")
                        xfill True
                        padding (8, 8)
                        textbutton "ВКЛЮЧИТЬ СВЕТ":
                            action Return(True)
                            xfill True
                            text_size 32
                            text_bold True
                            text_color "#66ff88"
                            text_xalign 0.5
                            padding (24, 26)
