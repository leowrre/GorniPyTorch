## ==============================================================================
## МИНИ-ИГРА: СБОРКА САЙТА ТЕХНИКУМА ПО ГОССТАНДАРТУ «ГОСВЕБ» (ИСП / ВЕБ-РАЗРАБОТКА)
## Контент и структура соответствуют официальному сайту https://pgt.kemobl.ru/
## и требованиям Рособрнадзора / ФГИС «Госвеб» к сайтам образовательных организаций
## ==============================================================================

init python:

    class SiteBuilderGame(object):
        PARTS = [
            {"id": "header", "title": "Шапка ОО + «Для слабовидящих»", "color": "#163a7a"},
            {"id": "nav", "title": "Меню: Сведения об ОО (ГОСТ)", "color": "#0d5bd7"},
            {"id": "banner", "title": "Баннер «Профессионалитет»", "color": "#ffbf1f"},
            {"id": "links", "title": "Госуслуги • Решаем вместе (ПОС)", "color": "#0b7a5c"},
            {"id": "news", "title": "Официальная лента новостей", "color": "#e8eff8"},
            {"id": "contacts", "title": "Контакты, ВК/MAX и НОКО", "color": "#2f4f7f"},
            {"id": "footer", "title": "Подвал: Минпросвещения и ПДн", "color": "#1e2936"},
            {"id": "gif", "title": "Гифка «В разработке» (БРАК)", "color": "#ff33cc"},
            {"id": "counter", "title": "Счётчик и реклама 2005 г.", "color": "#111111"},
        ]
        # Блоки внутри полноэкранной страницы (1366 x 844)
        PAGE_W, PAGE_H = 1366, 844
        SLOTS = [
            {"id": "s_header", "rect": (0, 0, 1366, 126), "need": "header", "hint": "Шапка ОО + версия для слабовидящих"},
            {"id": "s_nav", "rect": (0, 136, 1366, 66), "need": "nav", "hint": "Обязательное меню разделов ОО"},
            {"id": "s_banner", "rect": (0, 212, 900, 266), "need": "banner", "hint": "Главный баннер кластера"},
            {"id": "s_links", "rect": (916, 212, 450, 266), "need": "links", "hint": "Виджет «Госуслуги. Решаем вместе»"},
            {"id": "s_news", "rect": (0, 488, 900, 240), "need": "news", "hint": "Лента новостей техникума"},
            {"id": "s_contacts", "rect": (916, 488, 450, 240), "need": "contacts", "hint": "Контакты, Госпаблики и рейтинг"},
            {"id": "s_footer", "rect": (0, 738, 1366, 106), "need": "footer", "hint": "Подвал: ведомства и политика cookies"},
        ]

        def __init__(self):
            self.reset()

        def reset(self):
            self.placed = {}
            for s in self.SLOTS:
                self.placed[s["id"]] = None
            self.palette_order = [p["id"] for p in self.PARTS]
            random.shuffle(self.palette_order)
            self.held = None
            self.held_from = None
            self.sticky = False
            self.drag_pos = (0, 0)
            self.press_pos = (0, 0)
            self.errors = 0
            self.published = False
            self.popup_open = False
            self.popup_title = ""
            self.popup_text = ""
            self.message = "Соберите официальный сайт ПГТ на платформе «Госвеб» строго по образцу слева сверху!"

        def close_popup(self):
            self.popup_open = False

        def part(self, pid):
            for p in self.PARTS:
                if p["id"] == pid:
                    return p
            return None

        def filled_count(self):
            return sum(1 for v in self.placed.values() if v)

        def place(self, slot_id):
            """Ставит деталь из руки в блок. Если блок занят — детали меняются местами."""
            if self.held is None:
                return
            prev = self.placed[slot_id]
            self.placed[slot_id] = self.held
            if prev is not None and self.held_from is not None and self.held_from != slot_id:
                self.placed[self.held_from] = prev
            self.held = None
            self.held_from = None
            self.sticky = False
            mg_sfx("audio/pc_slide.wav")
            self.message = "Компонент размещён. Проверьте соответствие макету Госвеба!"

        def drop_back(self):
            self.held = None
            self.held_from = None
            self.sticky = False

        def publish(self):
            if self.published:
                return
            if self.filled_count() < len(self.SLOTS):
                mg_sfx("audio/turnstile_fail.wav")
                empty_cnt = len(self.SLOTS) - self.filled_count()
                self.popup_title = "САЙТ НЕ ПРОШЁЛ ПРОВЕРКУ!"
                self.popup_text = (
                    "По госстандарту на главной странице ОО все обязательные разделы должны быть заполнены.\n"
                    "Пустых блоков осталось: %d из 7. Сверьтесь с образцом слева сверху!" % empty_cnt
                )
                self.popup_open = True
                self.message = self.popup_text
                return
            wrong = [s for s in self.SLOTS if self.placed[s["id"]] != s["need"]]
            if wrong:
                used_retro = any(self.placed[s["id"]] in ("gif", "counter") for s in wrong)
                for s in wrong:
                    self.placed[s["id"]] = None
                self.errors += 1
                mg_sfx("audio/turnstile_fail.wav")
                self.popup_title = "ДИЗАЙН НЕ ПОДОШЁЛ (НЕ ПО ГОСТУ)!"
                if used_retro:
                    self.popup_text = (
                        "Рособрнадзор такой дизайн не примет: устаревшие гифки и счётчики нарушают стандарт «Госвеб»!\n"
                        "Ошибочные блоки (%d шт.) сняты со страницы — расставьте официальные блоки по образцу." % len(wrong)
                    )
                else:
                    self.popup_text = (
                        "Дизайн не подошёл — расположение блоков нарушает стандарт сайта образовательной организации!\n"
                        "Неверно расставлено блоков: %d шт. Они возвращены на панель слева." % len(wrong)
                    )
                self.popup_open = True
                self.message = self.popup_text
            else:
                self.popup_open = False
                self.published = True
                mg_sfx("audio/bun_win.wav")
                self.message = "САЙТ ОПУБЛИКОВАН ПО ГОССТАНДАРТУ! Все разделы ПГТ прошли проверку!"


    class SiteBuilderDisplayable(renpy.Displayable):
        W, H = 1880, 950
        PX, PY = 478, 76
        SAMPLE = (22, 102, 386, 190)
        PAL_X, PAL_Y, PAL_W, PAL_H, PAL_STEP = 14, 344, 404, 58, 65

        def __init__(self, game, **kwargs):
            super(SiteBuilderDisplayable, self).__init__(**kwargs)
            self.game = game

        def palette_items(self):
            g = self.game
            used = set(v for v in g.placed.values() if v)
            return [pid for pid in g.palette_order if pid not in used and pid != g.held]

        def palette_at(self, x, y):
            for i, pid in enumerate(self.palette_items()):
                py = self.PAL_Y + i * self.PAL_STEP
                if self.PAL_X <= x <= self.PAL_X + self.PAL_W and py <= y <= py + self.PAL_H:
                    return pid
            return None

        def slot_at(self, x, y):
            lx, ly = x - self.PX, y - self.PY
            for s in self.game.SLOTS:
                sx, sy, sw, sh = s["rect"]
                if sx <= lx <= sx + sw and sy <= ly <= sy + sh:
                    return s["id"]
            return None

        def draw_part_into(self, r, pid, w, h, st, at):
            """Отрисовка блока официального сайта ПГТ по стандарту ФГИС «Госвеб»."""
            c = r.canvas()
            p = self.game.part(pid)
            c.rect(p["color"], (0, 0, w, h))

            if pid == "header":
                rad = max(12, min(44, h // 2 - 10))
                cx, cy = 20 + rad, h // 2
                c.circle("#ffffff", (cx, cy), rad + 2)
                logo_path = "images/ui/logo_pgt_black.png"
                if mg_loadable(logo_path):
                    lsz = max(16, int(rad * 1.65))
                    mg_blit_img(r, logo_path, cx, cy, lsz, lsz, st=st, at=at)
                else:
                    mg_text(r, "ПГТ", cx, cy - 12, 20, "#163a7a", True, align=0.5, st=st, at=at)
                tx = 38 + rad * 2
                if w >= 900:
                    # Кнопка версии для слабовидящих и Госуслуги (обязательно по ГОСТ / Приказу № 1493)
                    c.rect("#ffffff", (w - 332, 16, 312, 42))
                    mg_text(r, "Версия для слабовидящих", w - 176, 24, 18, "#163a7a", True, align=0.5, st=st, at=at)
                    c.rect("#2557a7", (w - 332, 68, 312, 38))
                    mg_text(r, "Госвеб • Вход через ЕСИА", w - 176, 75, 17, "#d9e8ff", True, align=0.5, st=st, at=at)
                    _tw, th = mg_text(r, "ГБПОУ «Прокопьевский горнотехнический техникум им. В. П. Романова»",
                                      tx, 18, 20, "#ffffff", True, width=max(120, w - tx - 350), st=st, at=at)
                    sub_y = max(68, 18 + int(th) + 6)
                    mg_text(r, "Министерство образования Кузбасса • Официальный сайт ОО",
                            tx, sub_y, 17, "#ffd34d", False, width=max(120, w - tx - 350), st=st, at=at)
                else:
                    mg_text(r, "Шапка ОО + Версия для ОВЗ", tx, h // 2 - 16, 20, "#ffffff", True, width=max(60, w - tx - 14), st=st, at=at)

            elif pid == "nav":
                items = [
                    "Сведения об ОО", "Абитуриенту", "Студенту",
                    "Профессионалитет", "Антикоррупция", "Контакты"
                ]
                x = 20
                for item in items:
                    if x > w - 110:
                        break
                    tw, _th = mg_text(r, item, x, h // 2 - 13, 21, "#ffffff", True, st=st, at=at)
                    x += int(tw) + 34

            elif pid == "banner":
                for k in range(7):
                    c.polygon("#f2a300", mg_pts([(w - 80 - k * 100, 0), (w - 25 - k * 100, 0),
                                                (w - 170 - k * 100, h), (w - 225 - k * 100, h)]))
                mg_text(r, "ПРОФЕССИОНАЛИТЕТ", 30, 26, 42 if w >= 700 else 26, "#16243d", True, st=st, at=at)
                mg_text(r, "Кластер «Кузница машиностроения»", 30, 88, 26 if w >= 700 else 19, "#16243d", True, st=st, at=at)
                mg_text(r, "Приём документов через портал Госуслуг (ЕПГУ)", 30, 134, 20, "#1f3050", False, width=max(80, w - 50), st=st, at=at)
                if h >= 210 and w >= 520:
                    c.rect("#163a7a", (30, h - 66, 310, 46))
                    mg_text(r, "Подать заявление онлайн", 185, h - 55, 20, "#ffffff", True, align=0.5, st=st, at=at)

            elif pid == "links":
                # Официальный виджет ПОС «Госуслуги. Решаем вместе» + ЭИОС
                c.rect("#ffffff", (14, 14, max(40, w - 28), max(54, h // 2 - 18)))
                mg_text(r, "ГОСУСЛУГИ • РЕШАЕМ ВМЕСТЕ", 28, 22, 18, "#0d5bd7", True, width=max(60, w - 56), st=st, at=at)
                mg_text(r, "Есть предложения по учебному процессу?", 28, 48, 16, "#22303f", False, width=max(60, w - 56), st=st, at=at)
                if h >= 180:
                    c.rect("#0d5bd7", (28, 78, min(230, max(60, w - 56)), 34))
                    mg_text(r, "Написать обращение", 38, 84, 16, "#ffffff", True, st=st, at=at)
                    labels = ["Эл. журнал", "Расписание", "СДО Moodle"]
                    bw = max(30, (w - 56) // 3)
                    by = h // 2 + 12
                    bh = max(34, h - by - 14)
                    for i, lab in enumerate(labels):
                        bx = 14 + i * (bw + 14)
                        c.rect("#e8f5f0", (bx, by, bw, bh))
                        mg_text(r, lab, bx + bw // 2, by + bh // 2 - 11, 17, "#0b5c45", True, align=0.5, st=st, at=at)

            elif pid == "news":
                mg_text(r, "ОФИЦИАЛЬНЫЕ НОВОСТИ", 22, 14, 25, "#163a7a", True, st=st, at=at)
                items = [
                    "• Культурный код Кузбасса и Единый день открытых дверей ПГТ",
                    "• Вкусные каникулы: профпробы по кулинарии в техникуме",
                    "• Региональный этап чемпионата «Профессионалы» в ПГТ",
                ]
                for i, it in enumerate(items):
                    if 62 + i * 48 < h - 18:
                        mg_text(r, it, 22, 62 + i * 48, 20, "#1f2d3d", False, width=max(60, w - 40), st=st, at=at)

            elif pid == "contacts":
                mg_text(r, "КОНТАКТЫ И ГОСПАБЛИКИ", 20, 14, 22, "#ffffff", True, width=max(60, w - 36), st=st, at=at)
                mg_text(r, "+7 (384) 666-80-08 • Приёмная: 66-80-20", 20, 56, 19, "#ffffff", False, width=max(60, w - 36), st=st, at=at)
                mg_text(r, "pgtkromanov@mail.ru • ул. Шишкина, д. 26", 20, 94, 19, "#dce8ff", False, width=max(60, w - 36), st=st, at=at)
                if h >= 175:
                    c.rect("#1d3559", (20, 134, max(60, w - 40), 42))
                    mg_text(r, "Официальные сети: ВКонтакте • MAX", 32, 144, 18, "#7fd4ff", True, width=max(50, w - 64), st=st, at=at)
                if h >= 215:
                    mg_text(r, "Оценка качества ОО: bus.gov.ru", 20, 188, 17, "#ffd966", False, width=max(60, w - 36), st=st, at=at)

            elif pid == "footer":
                mg_text(r, "Министерство просвещения РФ • Министерство образования Кузбасса • Цифровой профиль ОО",
                        22, 16, 19, "#dce4ec", True, width=max(60, w - 44), st=st, at=at)
                mg_text(r, "Политика обработки персональных данных и файлов cookies • © ГБПОУ ПГТ им. В. П. Романова",
                        22, 54, 18, "#9fb2c4", False, width=max(60, w - 44), st=st, at=at)

            elif pid == "gif":
                for k in range(0, w + h, 52):
                    c.line("#ffee00", (k, 0), (k - h, h), 14)
                if int(st * 3) % 2 == 0:
                    mg_text(r, "САЙТ В РАЗРАБОТКЕ!!!", w // 2, h // 2 - 22, 34, "#ffffff", True, align=0.5, st=st, at=at)

            elif pid == "counter":
                mg_text(r, "Посетитель № 000137 • БЕЗ ГОСТа", w // 2, h // 2 - 32, 19, "#66ff00", False, align=0.5, st=st, at=at)
                mg_text(r, "СКАЧАТЬ РЕФЕРАТЫ 2005", w // 2, h // 2 + 2, 26, "#ff5533", True, align=0.5, st=st, at=at)

        def part_render(self, pid, w, h, st, at):
            r = renpy.Render(w, h)
            self.draw_part_into(r, pid, w, h, st, at)
            return r

        def blit_clipped(self, rv, sub, w, h, pos):
            try:
                rv.blit(sub.subsurface((0, 0, w, h)), pos)
            except Exception:
                rv.blit(sub, pos)

        def card_render(self, pid, st, at, highlight=False):
            key = ("site_card", pid, bool(highlight))
            def _build(r, _st, _at):
                p = self.game.part(pid)
                bg_path = "images/ui/round_btn_active.png" if highlight else "images/ui/round_btn_idle.png"
                r.blit(renpy.render(Frame(bg_path, 18, 18), self.PAL_W, self.PAL_H, _st, _at), (0, 0))
                c = r.canvas()
                cy = self.PAL_H // 2
                c.circle("#ffffff", (26, cy), 15)
                c.circle(p["color"], (26, cy), 13)
                mg_text(r, p["title"], 48, cy - 13, 19, "#ffffff", True, width=self.PAL_W - 58, st=_st, at=_at)
            layer = MGStaticLayer.get(key, self.PAL_W, self.PAL_H, _build)
            return renpy.render(layer, self.PAL_W, self.PAL_H, st, at)

        def cached_part_render(self, pid, w, h, st, at):
            blink = (int(st * 3) % 2) if pid == "gif" else 0
            key = ("site_part", pid, int(w), int(h), blink)
            def _build(r, _st, _at):
                self.draw_part_into(r, pid, w, h, (0.0 if blink == 0 else 0.35), _at)
            layer = MGStaticLayer.get(key, w, h, _build, clip=True)
            return renpy.render(layer, w, h, st, at)

        def _base_render(self, st, at):
            g = self.game
            def _build(rv, _st, _at):
                cv = rv.canvas()
                cv.rect("#061638", (0, 0, self.W, self.H))

                # --- Образец макета слева сверху ---
                cv.rect("#0b265c", (10, 8, 412, 298))
                cv.rect("#00d8ff", (10, 8, 412, 298), 3)
                mg_text(rv, "МАКЕТ САЙТА", 248, 32, 25, "#ffffff", True, align=0.5, st=_st, at=_at)
                sx, sy, sw, sh = self.SAMPLE
                kx = sw / float(g.PAGE_W)
                ky = sh / float(g.PAGE_H)
                cv.rect("#f4f8ff", (sx, sy - 20, sw, sh + 20))
                for s in g.SLOTS:
                    x, y, w, h = s["rect"]
                    p = g.part(s["need"])
                    rx, ry = int(sx + x * kx), int((sy - 20) + y * ky)
                    rw, rh = max(3, int(w * kx)), max(3, int(h * ky))
                    cv.rect(p["color"], (rx, ry, rw, rh))
                    lc = "#5c6f86" if s["need"] in ("news", "banner") else "#ffffff"
                    for li in range(min(3, max(1, rh // 12))):
                        cv.line(lc, (rx + 6, ry + 6 + li * 8), (rx + int(rw * 0.62), ry + 6 + li * 8), 2)

                # --- Полноэкранное окно браузера ---
                cv.rect("#dcebff", (442, 0, 1438, 950))
                cv.circle("#00c8ff", (472, 30), 10)
                cv.circle("#1864d8", (504, 30), 10)
                cv.circle("#ffffff", (536, 30), 10)
                cv.rect("#ffffff", (570, 12, 930, 38))
                mg_text(rv, "pgt.kemobl.ru", 588, 17, 21, "#0a2c6e", True, st=_st, at=_at)
                cv.rect("#f4f8ff", (458, 60, 1406, 876))

                for s in g.SLOTS:
                    x, y, w, h = s["rect"]
                    ax, ay = self.PX + x, self.PY + y
                    cv.rect("#e2eefc", (ax, ay, w, h))
                    cv.rect("#38a8ff", (ax, ay, w, h), 2)

            layer = MGStaticLayer.get(("site_base_chrome",), self.W, self.H, _build)
            return renpy.render(layer, self.W, self.H, st, at)

        @staticmethod
        def _draw_box_outline(rv, color, x, y, w, h, thick, st, at):
            mg_solid(rv, color, x, y, w, thick, st, at)
            mg_solid(rv, color, x, y + h - thick, w, thick, st, at)
            mg_solid(rv, color, x, y + thick, thick, h - 2 * thick, st, at)
            mg_solid(rv, color, x + w - thick, y + thick, thick, h - 2 * thick, st, at)

        def render(self, width, height, st, at):
            g = self.game
            rv = renpy.Render(self.W, self.H)
            rv.blit(self._base_render(st, at), (0, 0))

            # --- Крупные карточки деталей (закэшированы на GPU) ---
            for i, pid in enumerate(self.palette_items()):
                rv.blit(self.card_render(pid, st, at, False), (self.PAL_X, self.PAL_Y + i * self.PAL_STEP))

            hover_slot = self.slot_at(*g.drag_pos) if g.held else None
            for s in g.SLOTS:
                x, y, w, h = s["rect"]
                ax, ay = self.PX + x, self.PY + y
                pid = g.placed[s["id"]]
                if pid:
                    rv.blit(self.cached_part_render(pid, w, h, st, at), (ax, ay))
                elif g.held:
                    self._draw_box_outline(rv, "#00d8ff", ax + 2, ay + 2, w - 4, h - 4, 3, st, at)
                if hover_slot == s["id"]:
                    self._draw_box_outline(rv, "#00d8ff", ax, ay, w, h, 6, st, at)

            # --- Деталь в руке ---
            if g.held:
                mx, my = g.drag_pos
                rv.blit(self.card_render(g.held, st, at, True), (int(mx - self.PAL_W // 3), int(my - self.PAL_H // 2)))

            if any(v == "gif" for v in g.placed.values()):
                renpy.redraw(self, 0.35)
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.published or g.popup_open:
                return None

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if not (0 <= x <= self.W and 0 <= y <= self.H):
                    return None
                if g.held is not None and g.sticky:
                    slot = self.slot_at(x, y)
                    if slot:
                        g.place(slot)
                    else:
                        pid = self.palette_at(x, y)
                        g.drop_back()
                        if pid:
                            g.held = pid
                            g.press_pos = (x, y)
                            g.drag_pos = (x, y)
                    renpy.redraw(self, 0)
                    renpy.restart_interaction()
                    return None

                pid = self.palette_at(x, y)
                if pid:
                    g.held = pid
                    g.held_from = None
                else:
                    slot = self.slot_at(x, y)
                    if slot and g.placed[slot]:
                        g.held = g.placed[slot]
                        g.placed[slot] = None
                        g.held_from = slot
                if g.held:
                    g.sticky = False
                    g.press_pos = (x, y)
                    g.drag_pos = (x, y)
                    renpy.redraw(self, 0)
                return None

            elif ev.type == pygame.MOUSEMOTION and g.held is not None:
                g.drag_pos = (x, y)
                renpy.redraw(self, 0)
                return None

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and g.held is not None and not g.sticky:
                moved = math.hypot(x - g.press_pos[0], y - g.press_pos[1])
                slot = self.slot_at(x, y)
                if slot and moved >= 24:
                    g.place(slot)
                elif moved < 24:
                    g.sticky = True
                else:
                    g.drop_back()
                renpy.redraw(self, 0)
                renpy.restart_interaction()
                return None

            return None


default mg_site = SiteBuilderGame()

# ------------------------------------------------------------------------------
# ЭКРАН: СБОРКА САЙТА ПО ГОССТАНДАРТУ (НА ВЕСЬ ЭКРАН 1920x1080)
# ------------------------------------------------------------------------------
screen screen_minigame_site():
    modal True

    $ site_filled = mg_site.filled_count()

    if mg_site.published:
        timer 1.5 action Return(True)

    fixed:
        xsize 1920
        ysize 1080

        add Solid("#05102a")
        add SiteBuilderDisplayable(mg_site) xpos 20 ypos 14
        add Transform("images/ui/logo_pgt_white.png", size=(76, 76), fit="contain") xpos 36 ypos 18

        hbox:
            xpos 24
            ypos 976
            xsize 1872
            spacing 30

            frame:
                background Frame("images/ui/round_panel.png", 20, 20)
                yalign 0.5
                padding (28, 14)
                text "[site_filled] / 7" size 28 color ("#7ae8ff" if site_filled == 7 else "#ffffff") bold True

            if not mg_site.published:
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 24
                    textbutton "Очистить":
                        action Function(mg_site.reset)
                        background Frame("images/ui/round_btn_idle.png", 18, 18)
                        hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                        text_size 26
                        text_bold True
                        text_color "#ffffff"
                        padding (32, 16)
                    textbutton "СОБРАТЬ САЙТ":
                        action Function(mg_site.publish)
                        background Frame("images/ui/round_mg_green.png" if site_filled == 7 else "images/ui/round_btn_idle.png", 18, 18)
                        hover_background Frame("images/ui/round_mg_green_hover.png" if site_filled == 7 else "images/ui/round_btn_hover.png", 18, 18)
                        text_size 28
                        text_bold True
                        text_color "#ffffff"
                        padding (42, 16)

        # Полупрозрачная табличка посередине экрана по всей ширине до краёв, если сайт собран правильно
        if mg_site.published:
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
                    text "САЙТ СОБРАН ПРАВИЛЬНО!" size 46 color "#ffffff" bold True xalign 0.5 yalign 0.5 text_align 0.5
                    add Solid("#00e5ff") xsize 1920 ysize 4 yalign 1.0

            button:
                xsize 1920
                ysize 1080
                background None
                action Return(True)

        # Всплывающее скруглённое окно при неправильной сборке сайта
        if mg_site.popup_open:
            button:
                xfill True
                yfill True
                background Solid("#030a1cbb")
                action Function(mg_site.close_popup)

            frame:
                xalign 0.5
                yalign 0.5
                xsize 680
                background Frame("images/ui/round_mg_red_modal.png", 28, 28)
                padding (46, 38)

                vbox:
                    spacing 26
                    xalign 0.5

                    text "ОШИБКА СБОРКИ" size 38 color "#7ae8ff" bold True xalign 0.5 text_align 0.5

                    textbutton "ОК":
                        xalign 0.5
                        action Function(mg_site.close_popup)
                        background Frame("images/ui/round_mg_red_btn.png", 18, 18)
                        hover_background Frame("images/ui/round_mg_red_btn_hover.png", 18, 18)
                        text_size 28
                        text_bold True
                        text_color "#ffffff"
                        padding (56, 16)
