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
            cv.rect("#07183d", (0, 0, S, S))
            cv.rect("#00d8ff", (3, 3, S - 6, S - 6), 4)
            for r in range(g.N):
                for c in range(g.N):
                    x0, y0 = self.M + c * self.CELL, self.M + r * self.CELL
                    cv.rect("#0d2864", (x0 + 3, y0 + 3, self.CELL - 6, self.CELL - 6), 1)
                    cv.circle("#1c4ca8", self.center((r, c)), 9)

            # Провода
            for k in g.ORDER:
                p = g.paths[k]
                col = g.PHASES[k]["col"]
                if len(p) >= 2:
                    pts = [self.center(cell) for cell in p]
                    for i in range(len(pts) - 1):
                        cv.line("#040b1c", pts[i], pts[i + 1], 42)
                    for i in range(len(pts) - 1):
                        cv.line(col, pts[i], pts[i + 1], 26)
                    for pt in pts:
                        cv.circle(col, pt, 13)

            # Обязательные точки
            for k, cps in g.CHECKPOINTS.items():
                col = g.PHASES[k]["col"]
                for cell in cps:
                    cx, cy = self.center(cell)
                    cv.polygon("#040b1c", mg_pts([(cx, cy - 40), (cx + 40, cy), (cx, cy + 40), (cx - 40, cy)]))
                    dia = mg_pts([(cx, cy - 33), (cx + 33, cy), (cx, cy + 33), (cx - 33, cy)])
                    cv.polygon(col, dia, 0 if cell in g.paths[k] else 6)

            # Клеммы
            for k, terms in g.TERMINALS.items():
                col = g.PHASES[k]["col"]
                for cell in terms:
                    cx, cy = self.center(cell)
                    cv.circle("#040b1c", (cx, cy), 52)
                    cv.circle(col, (cx, cy), 46)
                    cv.circle("#091e4a", (cx, cy), 29)
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
                    fc.lines("#00d8ff", False, mg_pts(pts), 3)
                mg_text(fx, "КЗ!", S // 2, S // 2 - 42, 68, "#071844", True, align=0.5, st=st, at=at)
                rv.blit(fx, (0, 0))
                renpy.redraw(self, 0)

            # Пока нет подписи в журнале — щит закрыт
            if not g.tb_signed:
                ov = renpy.Render(S, S)
                ov.canvas().rect("#05122ed8", (0, 0, S, S))
                mg_text(ov, "ДОПУСК ЗАКРЫТ", S // 2, S // 2 - 24, 44, "#00e5ff", True, align=0.5, st=st, at=at)
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

    if wires_ok >= 4:
        timer 1.5 action Return(True)

    fixed:
        xsize 1920
        ysize 1080

        add Solid("#05102a")

        add WiringDisplayable(mg_wiring) xpos 44 ypos 44

        # Правая скруглённая панель с логотипом в правом верхнем углу
        frame:
            xpos 1076
            ypos 44
            xsize 800
            ysize 992
            background Frame("images/ui/round_wiring_panel.png", 26, 26)
            padding (36, 28)

            vbox:
                spacing 20
                xfill True

                fixed:
                    xfill True
                    ysize 96
                    text "ТЕХНИКА БЕЗОПАСНОСТИ" size 31 color "#ffffff" bold True xalign 0.0 yalign 0.5
                    add Transform("images/ui/logo_pgt_white.png", size=(96, 96), fit="contain") xalign 1.0 yalign 0.5

                frame:
                    background Frame("images/ui/round_wiring_sub.png", 20, 20)
                    xfill True
                    padding (24, 20)
                    vbox:
                        spacing 14
                        text "1. Соединить одноимённые клеммы (A, B, C, N)" size 23 color "#ffffff"
                        text "2. Пройти через свои ромбы" size 23 color "#7ae8ff" bold True
                        text "3. Не пересекать провода" size 23 color "#ffffff" bold True

                # Функциональная текстовая строка росписи с чекбоксом справа (хитбокс — всё пространство между блоками)
                button:
                    xfill True
                    ysize 110
                    background None
                    hover_background None
                    action Function(mg_wiring.sign)
                    padding (8, 0)

                    fixed:
                        xfill True
                        ysize 110
                        text "Расписаться в журнале" size 30 bold True color ("#7ae8ff" if mg_wiring.tb_signed else "#ffffff") xalign 0.0 yalign 0.5
                        add Transform("images/ui/p3_checkbox_checked.png" if mg_wiring.tb_signed else "images/ui/p3_checkbox_empty.png", size=(58, 58), fit="contain") xalign 1.0 yalign 0.5

                frame:
                    background Frame("images/ui/round_panel.png", 22, 22)
                    xfill True
                    padding (26, 22)
                    text "Цепи: [wires_ok] / 4" size 32 color ("#7ae8ff" if wires_ok == 4 else "#ffffff") bold True xalign 0.5

                null height 20

                if wires_ok < 4:
                    textbutton "Сброс":
                        action Function(mg_wiring.clear_wires)
                        xfill True
                        background Frame("images/ui/round_btn_idle.png", 20, 20)
                        hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                        text_size 28
                        text_bold True
                        text_color "#ffffff"
                        text_xalign 0.5
                        padding (24, 22)

        # Полупрозрачная табличка посередине экрана по всей ширине (как у сайта) + переход через 1.5 сек
        if wires_ok >= 4:
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
                    text "КОММУТАЦИЯ ЭЛЕКТРИЧЕСКИХ ЦЕПЕЙ ВЫПОЛНЕНА УСПЕШНО!" size 42 color "#ffffff" bold True xalign 0.5 yalign 0.5 text_align 0.5
                    add Solid("#00e5ff") xsize 1920 ysize 4 yalign 1.0

            button:
                xsize 1920
                ysize 1080
                background None
                action Return(True)
