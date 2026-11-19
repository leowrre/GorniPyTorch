## ==============================================================================
## МИНИ-ИГРЫ, ПРОФОРИЕНТАЦИОННЫЙ ИТОГ И ИНТЕРАКТИВНЫЙ БУКЛЕТ ПГТ (23 ПРОФЕССИИ)
## ==============================================================================

init python:
    import random
    import math
    import pygame

    def play_sfx(path):
        if renpy.loadable(path):
            renpy.sound.play(path)

    # --------------------------------------------------------------------------
    # ВИЗУАЛЬНЫЙ ЭФФЕКТ ДЛЯ СЦЕНЫ С ТЕСЛОЙ (МЕРЦАНИЕ В ТЕМНОТЕ КАК В FNAF 1)
    # --------------------------------------------------------------------------
    class TeslaDarknessDisplayable(renpy.Displayable):
        _cache = {}

        def __init__(self, **kwargs):
            super(TeslaDarknessDisplayable, self).__init__(**kwargs)
            self.width = 1920
            self.height = 1080

        def render(self, width, height, st, at):
            rv = renpy.Render(self.width, self.height)

            bg_path = "images/bg/pgt_workshop_corridor.png"
            if renpy.loadable(bg_path):
                bg_disp = self._cache.get("dark_corridor")
                if bg_disp is None:
                    bg_disp = Transform(
                        bg_path,
                        size=(self.width, self.height),
                        fit="cover",
                        matrixcolor=TintMatrix("#1b2a44") * BrightnessMatrix(-0.80)
                    )
                    self._cache["dark_corridor"] = bg_disp
                rv.blit(renpy.render(bg_disp, self.width, self.height, st, at), (0, 0))
            else:
                rv.canvas().rect("#030408", (0, 0, self.width, self.height))

            phase = (st * 6.5) % 1.0
            flicker_on = (phase < 0.38) or (0.55 < phase < 0.72) or (math.sin(st * 19.0) > 0.65)

            if flicker_on:
                cx, cy = 960, 430
                glow_layer = renpy.Render(self.width, self.height)
                glow_cv = glow_layer.canvas()
                glow_cv.circle("#0a2238aa", (cx, cy - 30), 250)
                glow_cv.circle("#11385a88", (cx, cy - 30), 180)
                rv.blit(glow_layer, (0, 0))

                tesla_path = "images/chars/tesla.png"
                if renpy.loadable(tesla_path):
                    t_disp = self._cache.get("tesla_flicker")
                    if t_disp is None:
                        t_disp = Transform(
                            tesla_path,
                            size=(560, 790),
                            fit="contain",
                            matrixcolor=TintMatrix("#88eeff")
                        )
                        self._cache["tesla_flicker"] = t_disp
                    tr = renpy.render(t_disp, 560, 790, st, at)
                    tw, th = tr.get_size()
                    rv.blit(tr, (int(cx - tw / 2), int(835 - th)))

                spark_layer = renpy.Render(self.width, self.height)
                spark_cv = spark_layer.canvas()
                for _ in range(4):
                    ax = cx + random.randint(-190, 190)
                    ay = cy + random.randint(-210, 180)
                    bx = ax + random.randint(-40, 40)
                    by = ay + random.randint(-40, 40)
                    spark_cv.line("#66ffff", (ax, ay), (bx, by), 2)
                rv.blit(spark_layer, (0, 0))

            renpy.redraw(self, 0.06)
            return rv

    # --------------------------------------------------------------------------
    # 1. ТУРНИКЕТ (РЕАЛЬНОЕ ФОТО ТУРНИКЕТА ПГТ + ИНТЕРАКТИВНЫЙ СТЕНД ПРОХОДНОЙ)
    # --------------------------------------------------------------------------
    class TurnstileGame:
        def __init__(self):
            self.reset()

        def reset(self):
            self.light = "red"
            self.tick_counter = 0
            self.status = "ready"
            self.card_anim_x = 0.15
            self.flash_timer = 0
            self.message = ""
            self.attempts = 0
            self.skipped = False

        def update_gauge(self):
            if self.flash_timer > 0:
                self.flash_timer -= 1
            if self.status != "success":
                self.tick_counter += 1
                cycle_pos = self.tick_counter % 14
                if cycle_pos >= 9:
                    self.light = "green"
                else:
                    self.light = "red"
                    if self.flash_timer == 0:
                        self.card_anim_x = 0.15

        def cycle_progress(self):
            return self.tick_counter % 14

        def swipe(self):
            if self.status == "success":
                return
            self.attempts += 1
            self.flash_timer = 4
            if self.light == "green":
                self.status = "success"
                self.card_anim_x = 0.85
                play_sfx("audio/turnstile_ok.wav")
            else:
                self.status = "fail"
                self.card_anim_x = 0.55
                play_sfx("audio/turnstile_fail.wav")


    class TurnstileDisplayable(renpy.Displayable):
        _bg_disp = None

        def __init__(self, game, **kwargs):
            super(TurnstileDisplayable, self).__init__(**kwargs)
            self.game = game
            self.width = 1920
            self.height = 1080

        def render(self, width, height, st, at):
            rv = renpy.Render(self.width, self.height)

            # Крупный план реального турникета ПГТ из photos2 (или общий план проходной)
            cp_path = "images/bg/pgt_turnstile_closeup.png"
            if not renpy.loadable(cp_path):
                cp_path = "images/bg/pgt_checkpoint.png"
            if renpy.loadable(cp_path):
                if TurnstileDisplayable._bg_disp is None:
                    TurnstileDisplayable._bg_disp = Transform(
                        cp_path,
                        size=(self.width, self.height),
                        fit="cover",
                        matrixcolor=BrightnessMatrix(-0.46)
                    )
                rv.blit(renpy.render(TurnstileDisplayable._bg_disp, self.width, self.height, st, at), (0, 0))
            else:
                bg_cv = rv.canvas()
                bg_cv.rect("#0d151e", (0, 0, self.width, self.height))

            ui = renpy.Render(self.width, self.height)
            canvas = ui.canvas()

            # Левая и правая тумбы турникета (исходные цвета)
            canvas.rect("#2c3c4cd8", (170, 210, 380, 660))
            canvas.rect("#4a627a", (170, 210, 380, 660), 5)
            canvas.rect("#394d60", (190, 210, 340, 44))

            canvas.rect("#2c3c4cd8", (1370, 210, 380, 660))
            canvas.rect("#4a627a", (1370, 210, 380, 660), 5)
            canvas.rect("#394d60", (1390, 210, 340, 44))

            is_green = (self.game.light == "green" or self.game.status == "success")

            if self.game.status == "success":
                canvas.rect("#1e5938", (550, 280, 58, 500))
                canvas.rect("#1e5938", (1312, 280, 58, 500))
                canvas.circle("#44ff77", (960, 520), 115)
                canvas.circle("#133a24", (960, 520), 92)
                canvas.line("#ffffff", (960, 585), (960, 455), 16)
                canvas.line("#ffffff", (905, 510), (960, 450), 16)
                canvas.line("#ffffff", (1015, 510), (960, 450), 16)
            else:
                flap_col = "#1f6b3dcc" if is_green else "#752028cc"
                border_col = "#55ff88" if is_green else "#ff5555"
                canvas.polygon(flap_col, [(550, 275), (942, 345), (942, 715), (550, 775)])
                canvas.polygon(border_col, [(550, 275), (942, 345), (942, 715), (550, 775)], 5)
                canvas.polygon(flap_col, [(1370, 275), (978, 345), (978, 715), (1370, 775)])
                canvas.polygon(border_col, [(1370, 275), (978, 345), (978, 715), (1370, 775)], 5)

            # Светофор-индикатор на левой тумбе
            canvas.rect("#111921", (255, 290, 210, 460))
            canvas.rect("#53687e", (255, 290, 210, 460), 3)

            if not is_green:
                canvas.circle("#6b1515", (360, 415), 78)
                canvas.circle("#ff3333", (360, 415), 60)
                canvas.circle("#ffaaaa", (342, 396), 18)
            else:
                canvas.circle("#2e1818", (360, 415), 56)

            if is_green:
                canvas.circle("#145e28", (360, 625), 78)
                canvas.circle("#33ff66", (360, 625), 60)
                canvas.circle("#b8ffcc", (342, 606), 18)
            else:
                canvas.circle("#162c1e", (360, 625), 56)

            # Считыватель пропуска на правой тумбе
            canvas.rect("#16202a", (1430, 290, 260, 460))
            canvas.rect("#44ff88" if is_green else "#3a88cc", (1430, 290, 260, 460), 4)
            canvas.circle("#223242", (1560, 470), 74)
            canvas.circle("#66ff99" if is_green else "#66ccff", (1560, 470), 74, 4)
            canvas.circle("#66ff99" if is_green else "#66ccff", (1560, 470), 42, 3)
            canvas.circle("#66ff99" if is_green else "#66ccff", (1560, 470), 14)

            cx = int(1340 + self.game.card_anim_x * 165)
            cy = int(595 - self.game.card_anim_x * 115)
            canvas.rect("#0b1015", (cx + 8, cy + 10, 190, 118))
            canvas.rect("#e8f1f8", (cx, cy, 190, 118))
            canvas.rect("#1d5fa8", (cx, cy + 16, 190, 26))
            canvas.rect("#8ca0b5", (cx + 20, cy + 62, 110, 12))
            canvas.rect("#8ca0b5", (cx + 20, cy + 84, 75, 10))
            canvas.rect("#336699", (cx, cy, 190, 118), 3)

            cyc = self.game.cycle_progress()
            for idx in range(14):
                bx = 400 + idx * 80
                by = 935
                col = "#33ff66" if idx >= 9 else "#ff4444"
                if idx == cyc and self.game.status != "success":
                    canvas.rect("#ffffff", (bx - 4, by - 5, 72, 42))
                canvas.rect(col if idx <= cyc or self.game.status == "success" else "#202b36", (bx, by, 64, 32))

            rv.blit(ui, (0, 0))
            if self.game.status != "success":
                renpy.redraw(self, 0.05)
            return rv

        def event(self, ev, x, y, st):
            if self.game.status == "success":
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if 0 <= x <= self.width and 0 <= y <= self.height:
                    self.game.swipe()
                    renpy.redraw(self, 0)
                    renpy.restart_interaction()
            return None


    # --------------------------------------------------------------------------
    # 3. ВОКАЛ НА СЦЕНЕ: СВЯЗНЫЙ КУПЛЕТ ГИМНА ПГТ + ПЕНАЛЬТИ ЗА ЛИШНИЕ СЛОВА
    # --------------------------------------------------------------------------
    class VocalGame:
        # Осмысленный студенческий куплет про ПГТ и Кузбасс (10 рифмованных фраз по порядку!)
        SONG_LINES = [
            "Родной Кузбасс",
            "зовёт вперёд,",
            "Горный техникум",
            "нас ждёт!",
            "В цехах и шахтах",
            "мы растём,",
            "Труд и знания",
            "несём!",
            "Славим дружно",
            "наш ПГТ!",
        ]
        # Неподходящие слова-ловушки: сбивают песню и дают пенальти (-1 фраза и штраф)!
        WRONG_WORDS = [
            "Проспал ко второй",
            "Двойка в зачётку",
            "Хвост по физике",
            "Забыл пропуск",
            "Прогулял пару",
            "Сорвал петуха",
            "Потерял зачётку",
            "Шпаргалка выпала",
            "Перепутал корпус",
            "Сгорел дедлайн",
        ]
        NOTES = ["ДО", "РЕ", "МИ", "ФА", "СОЛЬ", "ЛЯ", "СИ", "ДО"]
        MIN_X = 0.16
        MAX_X = 0.84

        def __init__(self):
            self.reset()

        def reset(self):
            self.collected_words = []
            self.target_count = len(self.SONG_LINES)
            self.mistakes = 0
            self.penalty_flash = 0
            self.last_note = "ДО"
            self.player_x = 0.5
            self.facing = 1
            self.step_phase = 0.0
            self.falling_words = []
            self.popups = []
            self.spawn_timer = 0
            self.message = ""

        def current_target_phrase(self):
            idx = len(self.collected_words)
            if idx < len(self.SONG_LINES):
                return self.SONG_LINES[idx]
            return ""

        def sung_preview(self):
            if not self.collected_words:
                return "Собранный текст появится здесь..."
            return " ".join(self.collected_words)

        def move_player(self, dx):
            if not self.is_finished():
                if dx < -0.001:
                    self.facing = -1
                elif dx > 0.001:
                    self.facing = 1
                self.step_phase += abs(dx) * 38.0
                self.player_x = max(self.MIN_X, min(self.MAX_X, self.player_x + dx))

        def set_player_x(self, x_val):
            if not self.is_finished():
                clamped = max(self.MIN_X, min(self.MAX_X, x_val))
                dx = clamped - self.player_x
                if dx < -0.002:
                    self.facing = -1
                elif dx > 0.002:
                    self.facing = 1
                self.step_phase += abs(dx) * 38.0
                self.player_x = clamped

        def update_tick(self):
            if self.is_finished():
                return

            if self.penalty_flash > 0:
                self.penalty_flash -= 1

            try:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.move_player(-0.024)
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.move_player(0.024)
            except Exception:
                pass

            self.spawn_timer += 1
            if self.spawn_timer >= 13 or len(self.falling_words) == 0:
                self.spawn_timer = 0
                if len(self.falling_words) < 4:
                    need_phrase = self.current_target_phrase()
                    has_good_on_screen = any(not w["bad"] for w in self.falling_words)
                    # Гарантируем, что нужная строка песни всегда регулярно падает вместе с ловушками
                    spawn_bad = has_good_on_screen and (random.random() < 0.56)
                    # Выбираем X без наложения на совсем недавние слова сверху
                    cand_x = random.uniform(0.18, 0.82)
                    for _ in range(6):
                        if all(abs(cand_x - w["x"]) > 0.17 or w["y"] > 0.28 for w in self.falling_words):
                            break
                        cand_x = random.uniform(0.18, 0.82)
                    if spawn_bad:
                        self.falling_words.append({
                            "word": random.choice(self.WRONG_WORDS),
                            "bad": True,
                            "x": cand_x,
                            "y": 0.12,
                            "speed": random.uniform(0.017, 0.026),
                        })
                    else:
                        self.falling_words.append({
                            "word": need_phrase,
                            "bad": False,
                            "x": cand_x,
                            "y": 0.12,
                            "speed": random.uniform(0.016, 0.024),
                        })

            new_popups = []
            for p in self.popups:
                p["y"] -= 0.020
                p["ttl"] -= 1
                if p["ttl"] > 0:
                    new_popups.append(p)
            self.popups = new_popups

            remaining = []
            for item in self.falling_words:
                item["y"] += item["speed"]
                if 0.68 <= item["y"] <= 0.99 and abs(item["x"] - self.player_x) <= 0.105:
                    if item["bad"]:
                        # ПЕНАЛЬТИ за подбор неправильных слов в песню!
                        self.mistakes += 1
                        self.penalty_flash = 10
                        if self.collected_words:
                            self.collected_words.pop()
                        play_sfx("audio/turnstile_fail.wav")
                        self.popups.append({
                            "text": "ФАЛЬШЬ! Штраф -1",
                            "col": "#ff5555",
                            "x": self.player_x,
                            "y": 0.65,
                            "ttl": 18,
                        })
                        # Обновляем уже летящие хорошие карточки под актуальную строку куплета
                        cur_need = self.current_target_phrase()
                        for other in self.falling_words:
                            if not other["bad"]:
                                other["word"] = cur_need
                    else:
                        idx = len(self.collected_words)
                        self.collected_words.append(self.SONG_LINES[idx])
                        note_idx = idx % len(self.NOTES)
                        self.last_note = self.NOTES[note_idx]
                        play_sfx("audio/note_%d.wav" % note_idx)
                        self.popups.append({
                            "text": self.last_note,
                            "col": "#66ffff",
                            "x": self.player_x,
                            "y": 0.65,
                            "ttl": 16,
                        })
                        if len(self.collected_words) >= self.target_count:
                            self.falling_words = []
                            play_sfx("audio/bun_win.wav")
                            return
                        nxt_need = self.current_target_phrase()
                        for other in self.falling_words:
                            if not other["bad"]:
                                other["word"] = nxt_need
                elif item["y"] < 1.03:
                    remaining.append(item)
            self.falling_words = remaining

        def is_finished(self):
            return len(self.collected_words) >= self.target_count


    class VocalStageController(renpy.Displayable):
        """Полноэкранное сенсорное и мышиное управление школьником на сцене актового зала."""
        def __init__(self, game, width=1920, height=1080, **kwargs):
            super(VocalStageController, self).__init__(**kwargs)
            self.game = game
            self.width = width
            self.height = height
            self.touching = False

        def render(self, width, height, st, at):
            rv = renpy.Render(self.width, self.height)
            canvas = rv.canvas()
            if self.game.penalty_flash > 0:
                canvas.rect("#ff112238", (0, 0, self.width, self.height))
            else:
                canvas.polygon("#ffd8661c", [(520, 0), (290, 885), (760, 885)])
                canvas.polygon("#ffffff18", [(960, 0), (720, 885), (1200, 885)])
                canvas.polygon("#ffd8661c", [(1400, 0), (1160, 885), (1630, 885)])
            return rv

        def event(self, ev, x, y, st):
            if self.game.is_finished():
                self.touching = False
                return None
            inside = (0 <= x <= self.width and 0 <= y <= self.height)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and inside:
                self.touching = True
                self.game.set_player_x(float(x) / float(self.width))
                renpy.restart_interaction()
            elif ev.type == pygame.MOUSEMOTION and inside:
                if self.touching or pygame.mouse.get_pressed()[0]:
                    self.game.set_player_x(float(x) / float(self.width))
                    renpy.restart_interaction()
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                self.touching = False
            return None


    # --------------------------------------------------------------------------
    # 4А. УЖЕСТОЧЁННАЯ СВАРКА ПО ФИРМЕННОМУ ШАБЛОНУ «ПГТ»
    #   • Вместо простой волны — многоходовой стальной шаблон букв «П Г Т»
    #   • Узкий допуск шва, контроль обрыва дуги, перегрева на одном месте и отрыва электрода
    #   • Если электрод сгорает до 0% — брак ОТК и повторная попытка
    # --------------------------------------------------------------------------
    class WeldGame:
        def __init__(self):
            self.retries = 0
            self.reset(full=True)

        @staticmethod
        def _interp_segment(p0, p1, steps):
            pts = []
            for i in range(steps + 1):
                t = i / float(steps)
                pts.append((int(round(p0[0] + (p1[0] - p0[0]) * t)),
                            int(round(p0[1] + (p1[1] - p0[1]) * t))))
            return pts

        def _build_pgt_strokes(self):
            # Буква П (единый непрерывный проход: снизу-слева -> вверх -> вправо -> вниз)
            s_p = (
                self._interp_segment((210, 680), (210, 190), 11)[:-1]
                + self._interp_segment((210, 190), (570, 190), 9)[:-1]
                + self._interp_segment((570, 190), (570, 680), 11)
            )
            # Буква Г (снизу -> вверх -> вправо)
            s_g = (
                self._interp_segment((760, 680), (760, 190), 11)[:-1]
                + self._interp_segment((760, 190), (1120, 190), 9)
            )
            # Буква Т — стойка (снизу -> вверх по центру)
            s_t_stem = self._interp_segment((1440, 680), (1440, 190), 11)
            # Буква Т — верхняя полка (слева -> направо)
            s_t_bar = self._interp_segment((1240, 190), (1640, 190), 10)
            return [s_p, s_g, s_t_stem, s_t_bar]

        def reset(self, full=False):
            if full:
                self.retries = 0
            self.strokes = self._build_pgt_strokes()
            self.total_segments = sum(len(s) - 1 for s in self.strokes)
            self.done_segments = 0
            self.stroke_idx = 0
            self.pt_idx = 0
            self.welded_strokes = [[] for _ in self.strokes]
            self.burn_marks = []
            self.points = 100.0
            self.spent_points = 0.0
            self.is_holding = False
            self.failed = False
            self.hold_still_ticks = 0
            self.cursor_pos = self.strokes[0][0]
            self.last_sfx_time = 0.0
            self.status_msg = "Зажгите дугу в жёлтой точке и ведите ровно по пазу шаблона «ПГТ» без рывков и остановок!"
            self.status_col = "#ffcc66"

        def retry_electrode(self):
            self.retries += 1
            self.reset(full=False)

        def active_target(self):
            if self.is_all_welded():
                return self.strokes[-1][-1]
            return self.strokes[self.stroke_idx][self.pt_idx]

        def spend(self, amount):
            # После 2 браков слегка смягчаем расход электрода (на 18%), чтобы игрок не застрял навечно
            mult = 0.82 if self.retries >= 2 else 1.0
            self.spent_points = round(self.spent_points + amount * mult, 1)
            self.points = max(0.0, round(100.0 - self.spent_points, 1))
            if self.points <= 0.0 and not self.is_all_welded():
                self.points = 0.0
                self.is_holding = False
                self.failed = True
                play_sfx("audio/turnstile_fail.wav")
                self.status_msg = "БРАК ОТК! Электрод полностью сгорел — шов «ПГТ» не завершён!"
                self.status_col = "#ff5555"

        def tick_heat(self):
            """Вызывается по таймеру 0.12 сек: карает за удержание дуги на одном месте (прожог!)."""
            if self.failed or self.is_all_welded() or not self.is_holding:
                self.hold_still_ticks = 0
                return
            if self.pt_idx > 0:
                self.hold_still_ticks += 1
                if self.hold_still_ticks >= 7:
                    self.hold_still_ticks = 3
                    cx, cy = self.cursor_pos
                    self.burn_marks.append((cx, cy))
                    play_sfx("audio/electric_shock.wav")
                    self.status_msg = "ПЕРЕГРЕВ И ПРОЖОГ МЕТАЛЛА! Не держите дугу на месте (-5%)!"
                    self.status_col = "#ff6655"
                    self.spend(5.0)

        def progress_percent(self):
            if self.total_segments <= 0:
                return 100
            return min(100, int(round((self.done_segments / float(self.total_segments)) * 100)))

        def is_all_welded(self):
            return self.stroke_idx >= len(self.strokes)

        def get_grade(self):
            if self.points >= 76.0 and self.retries == 0:
                return "perfect"
            elif self.points >= 46.0:
                return "good"
            return "sloppy"


    class WeldContourDisplayable(renpy.Displayable):
        def __init__(self, game, **kwargs):
            super(WeldContourDisplayable, self).__init__(**kwargs)
            self.game = game
            self.width = 1840
            self.height = 860

        def render(self, width, height, st, at):
            rv = renpy.Render(self.width, self.height)
            canvas = rv.canvas()
            g = self.game

            # Стальной лист на сварочном столе с накладным трафаретом «ПГТ»
            canvas.rect("#22272e", (0, 0, self.width, self.height))
            canvas.rect("#2b323b", (90, 80, self.width - 180, self.height - 160))
            canvas.rect("#45505e", (90, 80, self.width - 180, self.height - 160), 4)
            canvas.rect("#3b4450", (14, 14, self.width - 28, self.height - 28), 3)

            # Струбцины и крепёжные болты шаблона
            for cx, cy in [(56, 56), (self.width - 56, 56), (56, self.height - 56), (self.width - 56, self.height - 56),
                (665, 130), (665, 730), (1185, 130), (1185, 730)]:
                canvas.circle("#525e6c", (cx, cy), 20)
                canvas.circle("#15181c", (cx, cy), 8)

            # Фрезерованные разделки кромок под буквы «П», «Г», «Т»
            for s_i, stroke in enumerate(g.strokes):
                is_cur_stroke = (s_i == g.stroke_idx and not g.is_all_welded())
                groove_center = "#8da6bf" if is_cur_stroke else "#566678"
                for i in range(len(stroke) - 1):
                    canvas.line("#0d1014", stroke[i], stroke[i + 1], 36)
                    canvas.line("#1b222a", stroke[i], stroke[i + 1], 24)
                    canvas.line(groove_center, stroke[i], stroke[i + 1], 5)

            # Следы прожогов
            for bx, by in g.burn_marks:
                canvas.circle("#120908", (bx, by), 22)
                canvas.circle("#ff442288", (bx, by), 15, 3)

            # Наложенный сварной шов по всем проходам
            for w_stroke in g.welded_strokes:
                for i in range(len(w_stroke) - 1):
                    p1 = (w_stroke[i][0], w_stroke[i][1])
                    p2 = (w_stroke[i + 1][0], w_stroke[i + 1][1])
                    dev = w_stroke[i + 1][2]
                    if dev <= 14:
                        col = "#44ff66"
                    elif dev <= 26:
                        col = "#ffbb33"
                    else:
                        col = "#ff4433"
                    canvas.line(col, p1, p2, 20)
                    canvas.circle("#e6ffee" if dev <= 14 else "#ffd8cc", p2, 7)

            # Пульсирующая целевая точка электрода
            if not g.is_all_welded() and not g.failed:
                tx, ty = g.active_target()
                pulse = 26 + int(4 * math.sin(st * 8.0))
                canvas.circle("#ffcc00", (tx, ty), pulse, 4)
                canvas.circle("#ffcc0066", (tx, ty), 16)
                canvas.circle("#ffffff", (tx, ty), 6)

            # Держатель электрода и сварочная дуга
            if g.is_holding and not g.is_all_welded() and not g.failed:
                cx, cy = g.cursor_pos
                canvas.line("#c8cfd8", (cx, cy), (cx + 95, cy - 115), 9)
                canvas.line("#d97724", (cx + 68, cy - 82), (cx + 125, cy - 150), 18)
                canvas.circle("#ffffff", (cx, cy), 13)
                canvas.circle("#ffaa00", (cx, cy), 26, 4)
                for _ in range(9):
                    sx = cx + random.randint(-52, 52)
                    sy = cy + random.randint(-52, 52)
                    canvas.line("#ffea66", (cx, cy), (sx, sy), 3)

            if not g.is_all_welded() and not g.failed:
                renpy.redraw(self, 0.05)
            return rv

        def event(self, ev, x, y, st):
            g = self.game
            if g.is_all_welded() or g.failed:
                return None

            inside = (0 <= x <= self.width and 0 <= y <= self.height)

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and inside:
                tx, ty = g.active_target()
                if math.hypot(x - tx, y - ty) <= 58:
                    g.is_holding = True
                    g.hold_still_ticks = 0
                    g.cursor_pos = (int(x), int(y))
                    self._process_weld(int(x), int(y), st)
                else:
                    play_sfx("audio/turnstile_fail.wav")
                    g.status_msg = "Начинайте сварку точно в жёлтом кольце активного шва!"
                    g.status_col = "#ffcc44"
                renpy.redraw(self, 0)
                renpy.restart_interaction()
                return None

            elif ev.type == pygame.MOUSEMOTION and g.is_holding and inside:
                g.cursor_pos = (int(x), int(y))
                self._process_weld(int(x), int(y), st)
                renpy.redraw(self, 0)
                renpy.restart_interaction()
                return None

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if g.is_holding:
                    g.is_holding = False
                    # Штраф за преждевременный отрыв электрода посреди незавершённой линии!
                    if not g.is_all_welded() and g.pt_idx > 0:
                        play_sfx("audio/turnstile_fail.wav")
                        g.status_msg = "Отрыв электрода посреди шва (-3.5% электрода)! Продолжайте с жёлтой точки."
                        g.status_col = "#ffaa44"
                        g.spend(3.5)
                    renpy.redraw(self, 0)
                    renpy.restart_interaction()
                return None

            return None

        def _process_weld(self, x, y, st):
            g = self.game
            if g.is_all_welded() or g.failed:
                return

            stroke = g.strokes[g.stroke_idx]
            tx, ty = stroke[g.pt_idx]
            dist_cur = math.hypot(x - tx, y - ty)

            # Первая точка линии (поджиг дуги)
            if g.pt_idx == 0:
                if dist_cur <= 52:
                    dev = int(dist_cur)
                    g.welded_strokes[g.stroke_idx].append((int(x), int(y), dev))
                    g.pt_idx = 1
                    g.hold_still_ticks = 0
                    play_sfx("audio/weld_spark.wav")
                    g.last_sfx_time = st
                    g.status_msg = "Дуга горит! Ведите плавно и точно по оси разделки кромок."
                    g.status_col = "#66ff88"
                return

            # Ужесточение: увод руки дальше 56 px от текущей/предыдущей точки срывает дугу с прожогом!
            px_prev, py_prev = stroke[g.pt_idx - 1]
            if dist_cur > 62 and math.hypot(x - px_prev, y - py_prev) > 62:
                g.is_holding = False
                g.burn_marks.append((x, y))
                play_sfx("audio/electric_shock.wav")
                g.status_msg = "ОБРЫВ ДУГИ! Рука ушла со шва (-7.5% электрода)! Зажгите дугу в жёлтом кольце."
                g.status_col = "#ff5555"
                g.spend(7.5)
                return

            # Разрешаем продвижение не более чем на 2 узла за одно событие (защита от читерского рывка мышью)
            steps_this_event = 0
            advanced = False
            while not g.is_all_welded() and steps_this_event < 2:
                stroke = g.strokes[g.stroke_idx]
                tx, ty = stroke[g.pt_idx]
                d = math.hypot(x - tx, y - ty)
                if d <= 40:
                    # Отклонение по нормали к отрезку шва
                    ax, ay = stroke[g.pt_idx - 1]
                    seg_len = max(1.0, math.hypot(tx - ax, ty - ay))
                    cross = abs((tx - ax) * (ay - y) - (ax - x) * (ty - ay)) / seg_len
                    dev = int(round(cross))

                    if dev <= 12:
                        cost = 0.65
                    elif dev <= 24:
                        cost = 1.65
                    else:
                        cost = 3.10

                    g.spend(cost)
                    if g.failed:
                        return

                    # Притягиваем визуальный валик чуть ближе к разделке, сохраняя видимую кривизну при ошибке
                    wx = int(round(tx + max(-28, min(28, x - tx))))
                    wy = int(round(ty + max(-28, min(28, y - ty))))
                    g.welded_strokes[g.stroke_idx].append((wx, wy, dev))
                    g.done_segments += 1
                    g.pt_idx += 1
                    g.hold_still_ticks = 0
                    steps_this_event += 1
                    advanced = True

                    # Если текущий проход буквы завершён — чисто гасим дугу и переводим на следующую деталь!
                    if g.pt_idx >= len(stroke):
                        g.stroke_idx += 1
                        g.pt_idx = 0
                        g.is_holding = False
                        play_sfx("audio/wire_snap.wav")
                        if g.is_all_welded():
                            play_sfx("audio/bun_win.wav")
                            g.status_msg = "ШАБЛОН «ПГТ» ПРОВАРЕН ПОЛНОСТЬЮ!"
                            g.status_col = "#66ff88"
                        else:
                            labels = ["буква «Г»", "стойка буквы «Т»", "верхняя полка буквы «Т»"]
                            nxt_lbl = labels[min(g.stroke_idx - 1, len(labels) - 1)]
                            g.status_msg = "Шов лёг отлично! Теперь проварите следующий участок: %s." % nxt_lbl
                            g.status_col = "#66ff88"
                        break
                else:
                    break

            if advanced and not g.is_all_welded():
                if st - g.last_sfx_time >= 0.11:
                    play_sfx("audio/weld_spark.wav")
                    g.last_sfx_time = st


    # --------------------------------------------------------------------------
    # ПОЛНЫЙ ОФИЦИАЛЬНЫЙ СПРАВОЧНИК СПЕЦИАЛЬНОСТЕЙ И ПРОФЕССИЙ ПГТ (23 НАПРАВЛЕНИЯ)
    # Данные синхронизированы с приёмной комиссией https://pgt.kemobl.ru/
    # --------------------------------------------------------------------------
    PGT_BOOKLET_CATEGORIES = [
        ("it", "ИТ и Цифра (6)"),
        ("mining", "Горное дело (5)"),
        ("energy", "Энергетика (4)"),
        ("mech", "Сварка и станки (3)"),
        ("service", "Повара и право (5)"),
    ]

    PGT_ALL_SPECIALTIES = [
        # --- IT (6) ---
        {
            "id": "09.02.01", "cat": "it",
            "short": "Компьютерные системы и комплексы",
            "title": "09.02.01 Компьютерные системы и комплексы",
            "qual": "Специалист по компьютерным системам",
            "term": "Очная форма (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: связь, информационные и коммуникационные технологии (цифровые устройства, микропроцессорные системы, САПР, компьютерные комплексы, сети и средства информационной безопасности).\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Проектирование цифровых систем и микропроцессорных комплексов;\n"
                "• Проектирование управляющих программ компьютерных систем и комплексов;\n"
                "• Техническое обслуживание, диагностика и ремонт компьютерных систем и комплексов.\n\n"
                "Трудоустройство: крупные вычислительные центры, сервисные центры по ремонту и обслуживанию вычислительной техники, ИТ-отделы предприятий."
            ),
        },
        {
            "id": "09.02.06", "cat": "it",
            "short": "Сетевое и системное администрирование",
            "title": "09.02.06 Сетевое и системное администрирование",
            "qual": "Сетевой и системный администратор",
            "term": "Очная форма (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Основные компетенции и виды профессиональной деятельности:\n"
                "• Выполнение работ по проектированию сетевой инфраструктуры: кабельная структура компьютерной сети и защита информации;\n"
                "• Организация сетевого администрирования: администрирование локальных вычислительных сетей и сетевых ресурсов;\n"
                "• Эксплуатация объектов сетевой инфраструктуры: мониторинг работы сети, диагностика, поиск и устранение неисправностей;\n"
                "• Управление сетевыми сервисами: формализация процессов управления инцидентами и технологической поддержки;\n"
                "• Сопровождение модернизации сетевой инфраструктуры: планирование сети и оптимизация работы серверов."
            ),
        },
        {
            "id": "09.02.09", "cat": "it",
            "short": "Веб-разработка",
            "title": "09.02.09 Веб-разработка",
            "qual": "Разработчик веб-приложений",
            "term": "Очная форма (на базе 9 классов) — 2 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: создание, поддержка и развитие сайтов, порталов и веб-приложений (Frontend и Backend).\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Проектирование и разработка веб-ресурсов: создание структуры, функционала и кода для сайтов и порталов;\n"
                "• Дизайн веб-приложений: разработка пользовательских интерфейсов (UI/UX) и дизайн-концепций;\n"
                "• Вёрстка и программирование: визуальная часть (HTML, CSS, JS) и серверная логика (PHP, Python, Java, Node.js);\n"
                "• Работа с базами данных, тестирование, оптимизация безопасности и сопровождение готовых веб-проектов."
            ),
        },
        {
            "id": "09.02.10", "cat": "it",
            "short": "Разработка игр и VR/AR",
            "title": "09.02.10 Разработка компьютерных игр, дополненной и виртуальной реальности",
            "qual": "Разработчик компьютерных игр, дополненной и виртуальной реальности",
            "term": "Очная форма (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: создание интерактивных цифровых продуктов, компьютерных игр различных жанров, VR/AR-приложений, 2D/3D-графики и анимации.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Разработка программных модулей и графического интерфейса пользователя;\n"
                "• 3D-моделирование и визуализация компонентов системы;\n"
                "• Разработка иммерсивных приложений, компьютерных игр и мультимедийных приложений;\n"
                "• Работа с базами данных и тестирование информационных систем."
            ),
        },
        {
            "id": "09.02.11", "cat": "it",
            "short": "Разработка и управление ПО",
            "title": "09.02.11 Разработка и управление программным обеспечением",
            "qual": "Программист",
            "term": "Очная форма (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: создание, внедрение и сопровождение программных продуктов, компьютерных систем и автоматизированных систем обработки информации и управления.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Разработка, администрирование и защита баз данных;\n"
                "• Разработка и интеграция модулей программного обеспечения;\n"
                "• Проектирование и разработка информационных систем."
            ),
        },
        {
            "id": "09.02.12", "cat": "it",
            "short": "Эксплуатация информационных систем",
            "title": "09.02.12 Техническая эксплуатация и сопровождение информационных систем",
            "qual": "Специалист по технической эксплуатации и сопровождению информационных систем",
            "term": "Очная форма (на базе 9 классов) — 2 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: связь, информационные и коммуникационные технологии (аппаратные и программные компоненты ИС, сети, ОС, СУБД и средства информационной безопасности).\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Инсталляция, настройка и сопровождение операционных систем и прикладного ПО;\n"
                "• Администрирование локальных вычислительных сетей и защита информации от несанкционированного доступа;\n"
                "• Выявление и устранение неисправностей аппаратного и программного обеспечения;\n"
                "• Техническое обслуживание компьютерной техники, консультирование пользователей и ведение документации."
            ),
        },

        # --- ГОРНОЕ ДЕЛО (5) ---
        {
            "id": "21.02.14", "cat": "mining",
            "short": "Маркшейдерское дело",
            "title": "21.02.14 Маркшейдерское дело",
            "qual": "Горный специалист-маркшейдер",
            "term": "Очная форма (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: организация и проведение маркшейдерско-геодезических работ и геометрического контроля качества технологических процессов на горнодобывающих и строительных предприятиях.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Выполнение геодезических работ и пространственно-геометрических измерений;\n"
                "• Маркшейдерское обеспечение ведения горных работ и контроль параметров горных выработок;\n"
                "• Учёт выемки полезного ископаемого из недр и организация работы коллектива исполнителей.\n\n"
                "Рабочая профессия: «Горнорабочий на маркшейдерских работах»."
            ),
        },
        {
            "id": "21.02.15", "cat": "mining",
            "short": "Открытые горные работы",
            "title": "21.02.15 Открытые горные работы",
            "qual": "Специалист по горным работам",
            "term": "Очно (9 кл.) — 3 года 10 мес. • Заочно (11 кл.) — 3 года 10 мес.",
            "desc": (
                "Открытый способ разработки обеспечивает наиболее эффективные и безопасные условия добычи каменного угля и других полезных ископаемых на разрезах.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Организация и контроль технологических процессов при проведении открытых горных работ;\n"
                "• Обеспечение функционирования системы управления охраной труда и промышленной безопасностью на горном участке;\n"
                "• Организация деятельности персонала производственного подразделения и эксплуатация горнотранспортного оборудования."
            ),
        },
        {
            "id": "21.02.17", "cat": "mining",
            "short": "Подземная разработка (ПРМПИ)",
            "title": "21.02.17 Подземная разработка месторождений полезных ископаемых",
            "qual": "Специалист по горным работам",
            "term": "Очно (9 кл.) — 3 года 10 мес. • Заочно (11 кл.) — 3 года 10 мес.",
            "desc": (
                "Область профессиональной деятельности: организация и проведение работ на производственном участке по добыче полезных ископаемых подземным способом.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Организация и контроль технологических процессов горных и взрывных работ в соответствии с технической и нормативной документацией;\n"
                "• Обеспечение функционирования системы управления охраной труда и промышленной безопасностью на участке;\n"
                "• Организация деятельности персонала производственного подразделения.\n\n"
                "Кем работают выпускники: горный техник, горный мастер, машинист горных выемочных машин, проходчик, техник-технолог."
            ),
        },
        {
            "id": "21.02.18", "cat": "mining",
            "short": "Обогащение полезных ископаемых",
            "title": "21.02.18 Обогащение полезных ископаемых",
            "qual": "Специалист по обогащению полезных ископаемых",
            "term": "Очно (9 кл.) — 3 года 10 мес. • Заочно (11 кл.) — 3 года 10 мес.",
            "desc": (
                "Область профессиональной деятельности: добыча и переработка угля, руд и других полезных ископаемых на обогатительных фабриках.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Ведение технологических процессов обогащения полезных ископаемых согласно заданным параметрам;\n"
                "• Организация безопасных условий труда и производственной деятельности технического персонала.\n\n"
                "Кем работают выпускники: контролёр продуктов обогащения, концентраторщик, флотатор, сепараторщик, грохотовщик, дробильщик, машинист установок."
            ),
        },
        {
            "id": "21.02.19", "cat": "mining",
            "short": "Землеустройство",
            "title": "21.02.19 Землеустройство",
            "qual": "Специалист по землеустройству",
            "term": "Очно (9 кл.) — 3 года 10 мес. • Заочно (11 кл.) — 3 года 10 мес.",
            "desc": (
                "Специалист по топографической съёмке, измерениям и межеванию земельных угодий, контролирующий рациональное и законное использование земель.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Подготовка, планирование и выполнение полевых и камеральных работ по инженерно-геодезическим изысканиям;\n"
                "• Проведение технической инвентаризации и технической оценки объектов недвижимости;\n"
                "• Ведение ЕГРН, проведение кадастрового учёта и регистрации прав на объекты недвижимости;\n"
                "• Контроль использования и охраны земельных ресурсов, мониторинг земель."
            ),
        },

        # --- ЭНЕРГЕТИКА И ЭЛЕКТРООБОРУДОВАНИЕ (4) ---
        {
            "id": "13.02.02", "cat": "energy",
            "short": "Теплоснабжение и теплотехника",
            "title": "13.02.02 Теплоснабжение и теплотехническое оборудование",
            "qual": "Техник-теплотехник",
            "term": "Очно (9 кл.) — 3 года 10 мес. • Заочно (11 кл.) — 3 года 10 мес.",
            "desc": (
                "Область профессиональной деятельности: техническое обслуживание и эксплуатация теплотехнического оборудования систем тепловодогазоснабжения и средств учёта тепловой энергии.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Эксплуатация теплотехнического оборудования и систем тепло- и топливоснабжения;\n"
                "• Ремонт теплотехнического оборудования и систем тепло- и топливоснабжения;\n"
                "• Наладка и испытания теплотехнического оборудования и систем тепло- и топливоснабжения.\n\n"
                "Рабочая профессия: «Слесарь по обслуживанию тепловых сетей»."
            ),
        },
        {
            "id": "13.02.12", "cat": "energy",
            "short": "Электрические станции, сети и РЗА",
            "title": "13.02.12 Электрические станции, сети, их релейная защита и автоматизация",
            "qual": "Техник-электрик",
            "term": "Очно, заочно (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: техническое обслуживание, эксплуатация, ремонт, наладка и испытание электрооборудования электрических станций, сетей и систем.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Обслуживание и эксплуатация электрооборудования электрических станций, сетей и систем;\n"
                "• Контроль и управление технологическими процессами производства, передачи и распределения электроэнергии;\n"
                "• Диагностика состояния электрооборудования электрических станций, сетей и систем;\n"
                "• Организация и управление коллективом исполнителей."
            ),
        },
        {
            "id": "13.02.13", "cat": "energy",
            "short": "Эксплуатация электрооборудования",
            "title": "13.02.13 Эксплуатация и обслуживание электрического и электромеханического оборудования (по отраслям)",
            "qual": "Техник",
            "term": "Очно (9 кл.) — 3 года 10 мес. • Заочно (11 кл.) — 3 года 10 мес.",
            "desc": (
                "Область профессиональной деятельности: электроэнергетика, промышленность, горные предприятия, транспорт, строительство и ЖКХ.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Техническое обслуживание и ремонт электрического и электромеханического оборудования;\n"
                "• Организационное обеспечение эксплуатации, ТО и ремонта электрооборудования;\n"
                "• Эксплуатация и обслуживание электрооборудования с автоматизированными системами управления;\n"
                "• Разработка и оформление технической документации."
            ),
        },
        {
            "id": "13.01.10", "cat": "energy",
            "short": "Электромонтёр электрооборудования",
            "title": "13.01.10 Электромонтёр по ремонту и обслуживанию электрооборудования (по отраслям)",
            "qual": "Электромонтёр по ремонту и обслуживанию электрооборудования",
            "term": "Очная форма (на базе 9 классов) — 1 год 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: техническое обслуживание, ремонт и испытание электрического и электромеханического оборудования отрасли.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Сборка, монтаж, регулировка и ремонт узлов и механизмов электрооборудования;\n"
                "• Обслуживание силовых и осветительных электроустановок, кабельных линий и распределительных устройств;\n"
                "• Проверка, наладка и испытание электрического и электромеханического оборудования на предприятиях."
            ),
        },

        # --- СВАРКА, СЛЕСАРНОЕ ДЕЛО И МАШИНОСТРОЕНИЕ (3) ---
        {
            "id": "15.01.05", "cat": "mech",
            "short": "Сварщик (ручной и мех. сварки)",
            "title": "15.01.05 Сварщик (ручной и частично механизированной сварки (наплавки))",
            "qual": "Сварщик",
            "term": "Очная форма (на базе 9 классов) — 1 год 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: изготовление, реконструкция, монтаж, ремонт и строительство конструкций с применением ручной и частично механизированной сварки (наплавки) во всех пространственных положениях сварного шва.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Проведение подготовительных и сборочных операций перед сваркой, зачистка и контроль сварных швов;\n"
                "• Ручная дуговая сварка (наплавка, резка) плавящимся покрытым электродом и неплавящимся электродом в защитном газе;\n"
                "• Частично механизированная сварка (наплавка) плавлением, газовая, термитная и сварка деталей из полимерных материалов."
            ),
        },
        {
            "id": "15.01.35", "cat": "mech",
            "short": "Мастер слесарных работ",
            "title": "15.01.35 Мастер слесарных работ",
            "qual": "Слесарь механосборочных работ • Слесарь-инструментальщик • Слесарь-ремонтник",
            "term": "Очная форма (на базе 9 классов) — 2 года 10 месяцев",
            "desc": (
                "Квалификации и основные компетенции выпускника:\n\n"
                "• Слесарь механосборочных работ — осуществляет сборку и наладку машин и механизмов из деталей.\n\n"
                "• Слесарь-инструментальщик — выполняет изготовление и ремонт инструмента, штампов и приспособлений с применением специальной оснастки и шаблонов, слесарную обработку, закалку, доводку и притирку деталей.\n\n"
                "• Слесарь-ремонтник — осуществляет подготовку деталей, сборку машин и механизмов, подгонку, соединение и регулировку узлов, сверление, нарезание резьбы, неразъёмные соединения и стендовые испытания собираемых станков и машин."
            ),
        },
        {
            "id": "15.02.17", "cat": "mech",
            "short": "Монтаж и ремонт пром. оборудования",
            "title": "15.02.17 Монтаж, техническое обслуживание, эксплуатация и ремонт промышленного оборудования (по отраслям)",
            "qual": "Техник-механик",
            "term": "Очная форма (на базе 9 классов) — 2 года 10 месяцев",
            "desc": (
                "Механики являются фундаментом инженерной мысли промышленного предприятия, работающего в любой отрасли экономики.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Монтаж, пусконаладка, техническое обслуживание, эксплуатация и ремонт промышленного оборудования;\n"
                "• Диагностика и восстановление узлов, приводов, редукторов, гидравлических и механических систем.\n\n"
                "Трудоустройство: машиностроительные заводы, горнодобывающие и нефтехимические предприятия, электростанции, КБ и НИИ."
            ),
        },

        # --- КУЛИНАРИЯ, ЭКОНОМИКА, ТОРГОВЛЯ, ЮРИСПРУДЕНЦИЯ, ДОКУМЕНТООБОРОТ (5) ---
        {
            "id": "38.02.01", "cat": "service",
            "short": "Экономика и бухгалтерский учёт",
            "title": "38.02.01 Экономика и бухгалтерский учёт (по отраслям)",
            "qual": "Бухгалтер",
            "term": "Очно (9 кл.) — 2 года 10 мес. • Заочно (11 кл.) — 2 года 10 мес.",
            "desc": (
                "Современный специалист, владеющий знаниями в экономической, финансовой сфере и в области информационных технологий, сочетающий высокую компьютерную грамотность и умение управлять финансами.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Документирование хозяйственных операций и ведение бухгалтерского учёта имущества организации;\n"
                "• Ведение бухгалтерского учёта источников формирования имущества, инвентаризация имущества и обязательств;\n"
                "• Проведение расчётов с бюджетом и внебюджетными фондами, составление и использование бухгалтерской отчётности.\n\n"
                "Рабочая профессия: «Кассир»."
            ),
        },
        {
            "id": "38.02.08", "cat": "service",
            "short": "Торговое дело",
            "title": "38.02.08 Торговое дело",
            "qual": "Специалист по торговому делу",
            "term": "Очно (9 кл.) — 2 года 10 мес. • Заочно (11 кл.) — 2 года 10 мес.",
            "desc": (
                "Область профессиональной деятельности: организация и проведение коммерческой деятельности в производственных, торговых и сервисных организациях.\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Организация и осуществление торговой и предпринимательской деятельности в сфере торговли;\n"
                "• Товароведение и организация экспертизы качества потребительских товаров;\n"
                "• Организация и осуществление интернет-маркетинга и выставочной деятельности.\n\n"
                "Должности: руководитель коммерческой деятельности, менеджер по закупкам и продажам, маркетолог, товаровед, логист, мерчендайзер."
            ),
        },
        {
            "id": "40.02.04", "cat": "service",
            "short": "Юриспруденция",
            "title": "40.02.04 Юриспруденция",
            "qual": "Юрист",
            "term": "Очная форма (на базе 9 классов) — 2 года 10 месяцев",
            "desc": (
                "Основные компетенции и виды профессиональной деятельности:\n"
                "• Правоприменительная деятельность: профессиональное толкование и применение норм права, подготовка юридических документов;\n"
                "• Правоохранительная деятельность: контроль соблюдения законодательства РФ, систематизация нормативных правовых актов;\n"
                "• Обеспечение реализации прав граждан в сфере пенсионного обеспечения и социальной защиты;\n"
                "• Организационное обеспечение деятельности правоохранительных органов и организационно-техническое обеспечение работы судов;\n"
                "• Правовое обеспечение деятельности организаций и оказание юридической помощи гражданам."
            ),
        },
        {
            "id": "43.02.15", "cat": "service",
            "short": "Поварское и кондитерское дело",
            "title": "43.02.15 Поварское и кондитерское дело",
            "qual": "Специалист по поварскому и кондитерскому делу",
            "term": "Очная форма (на базе 9 классов) — 3 года 10 месяцев",
            "desc": (
                "Основные компетенции и виды профессиональной деятельности:\n"
                "• Организация и контроль приготовления и подготовки к продаже полуфабрикатов сложного ассортимента;\n"
                "• Организация и контроль приготовления, оформления и подготовки к продаже горячих и холодных блюд и закусок сложного ассортимента;\n"
                "• Организация и контроль приготовления, оформления и подготовки к продаже холодных и горячих десертов и напитков;\n"
                "• Организация и контроль приготовления и оформления хлебобулочных и мучных кондитерских изделий;\n"
                "• Организация и контроль текущей деятельности подчинённого персонала."
            ),
        },
        {
            "id": "46.02.02", "cat": "service",
            "short": "Цифровая трансформация документов",
            "title": "46.02.02 Обеспечение технологического сопровождения цифровой трансформации документированных сфер деятельности",
            "qual": "Специалист по технологическому сопровождению цифровой трансформации документированных сфер деятельности",
            "term": "Очная форма (на базе 9 классов) — 2 года 10 месяцев",
            "desc": (
                "Область профессиональной деятельности: цифровизация документооборота в различных сферах деятельности (документы и системы документации, системы информационно-документационного обеспечения управления, электронные и архивные документы).\n\n"
                "Основные компетенции и виды деятельности:\n"
                "• Цифровизация и оптимизация документооборота;\n"
                "• Обработка аналитической информации, полезной для бизнес-процессов компании."
            ),
        },
    ]

    def get_specialty_by_id(spec_id):
        for sp in PGT_ALL_SPECIALTIES:
            if sp["id"] == spec_id:
                return sp
        return PGT_ALL_SPECIALTIES[0]

    def compute_career_recommendation():
        """Рассчитывает подходящую игроку специальность ПГТ по реальным результатам всех мини-игр."""
        # 1. ИТ и Веб-разработка (сборка сайта Госвеба + реакция на проходной)
        it_score = max(35, 100 - mg_site.errors * 22)
        if not mg_turnstile.skipped and mg_turnstile.attempts == 1:
            it_score = min(100, it_score + 6)

        # 2. Горное дело (шахтный полигон: минимум попаданий под крыс/взрывы + расчистка породы)
        mine_score = max(35, 96 - mg_mine.hits * 20 + min(8, mg_mine.rocks_broken // 3))
        mine_score = min(100, mine_score)

        # 3. Электроэнергетика (щитовая Теслы: минимум коротких замыканий)
        elec_score = max(35, 100 - mg_wiring.shocks * 18)

        # 4. Сварочное производство (шаблон «ПГТ»: остаток электрода и отсутствие брака)
        weld_score = max(30, int(round(mg_weld.points)) - mg_weld.retries * 18)
        weld_score = min(100, weld_score)

        # 5. Машиностроение и механика (сборка шестерёнчатого редуктора станка)
        if getattr(mg_pipes, "used_help", False):
            mech_score = 48
        else:
            extra_moves = max(0, mg_pipes.moves - 6)
            mech_score = max(42, min(100, 100 - extra_moves * 6))

        # 6. Поварское и кондитерское дело (стелс на кухне + точность и рецептура бутера)
        burger_base = 100 if mg_burger.grade == "perfect" else (78 if mg_burger.grade == "good" else 54)
        cook_pen = mg_kitchen.total_catches * 12 + mg_kitchen.penalties * 18 + mg_burger.mistakes * 10
        cook_score = max(30, min(100, burger_base - cook_pen))

        ranking = [
            {
                "spec_id": "09.02.09",
                "cat": "it",
                "label": "Веб-разработка и ИТ (09.02.09 / 09.02.11)",
                "prof_title": "Разработчик веб-приложений / Программист",
                "score": it_score,
                "reason": "Ты уверенно собрал официальный сайт техникума по стандарту «Госвеб» и быстро разобрался в структуре цифровых сервисов!",
            },
            {
                "spec_id": "21.02.17",
                "cat": "mining",
                "label": "Подземная разработка (21.02.17 ПРМПИ)",
                "prof_title": "Специалист по горным работам",
                "score": mine_score,
                "reason": "Хладнокровие в учебном штреке, точный расчёт зарядов и прорыв сквозь завалы породы выдают в тебе прирождённого горняка Кузбасса!",
            },
            {
                "spec_id": "13.02.13",
                "cat": "energy",
                "label": "Электрооборудование и автоматика (13.02.13)",
                "prof_title": "Техник-электромеханик / Электромонтёр",
                "score": elec_score,
                "reason": "Даже в кромешной темноте с Николой Теслой ты развёл все фазы и ноль по схеме без лишних коротких замыканий!",
            },
            {
                "spec_id": "15.01.05",
                "cat": "mech",
                "label": "Сварочное производство (15.01.05)",
                "prof_title": "Сварщик ручной и механизированной сварки",
                "score": weld_score,
                "reason": "Твёрдая рука и отличный глазомер: ты аккуратно проварил стальной шаблон «ПГТ» под присмотром самого строгого мастера!",
            },
            {
                "spec_id": "15.02.17",
                "cat": "mech",
                "label": "Монтаж и ремонт пром. оборудования (15.02.17)",
                "prof_title": "Техник-механик («Кузница машиностроения»)",
                "score": mech_score,
                "reason": "Инженерное мышление на высоте: ты сходу подобрал передаточные шестерни редуктора и запустил все три узла промышленного станка!",
            },
            {
                "spec_id": "43.02.15",
                "cat": "service",
                "label": "Поварское и кондитерское дело (43.02.15)",
                "prof_title": "Специалист по поварскому и кондитерскому делу",
                "score": cook_score,
                "reason": "Ловкость на кухне, выдержка под взглядом шеф-повара и безупречное соблюдение рецептуры — кулинарный цех ждёт тебя!",
            },
        ]
        ranking.sort(key=lambda item: item["score"], reverse=True)
        best = ranking[0]
        second = ranking[1]
        vocal_bonus = (mg_vocal.mistakes == 0)
        return {
            "best": best,
            "second": second,
            "all": ranking,
            "vocal_star": vocal_bonus,
        }


# Фоновый объект мерцающего Николы Теслы
image bg pgt_blackout_tesla = TeslaDarknessDisplayable()

# Инициализация глобальных объектов игр и справочника
default mg_turnstile = TurnstileGame()
default mg_vocal = VocalGame()
default mg_weld = WeldGame()
default selected_cat = "it"
default selected_specialty = "09.02.09"
default recommended_spec_id = "09.02.09"
default career_summary = None


## ==============================================================================
## ЭКРАНЫ МИНИ-ИГР (ПОЛНОЭКРАННЫЕ 1920x1080, ПОД ПК И МОБИЛКИ)
## ==============================================================================

# ------------------------------------------------------------------------------
# ВСПЛЫВАЮЩЕЕ ОКНО ПЕРЕД МИНИ-ИГРАМИ (МИНИМАЛИЗМ + СТИЛЬ PERSONA 3 RELOAD)
# ------------------------------------------------------------------------------
screen screen_mg_intro(title_txt, desc_txt):
    modal True

    key "dismiss" action Return(True)
    key "K_SPACE" action Return(True)
    key "K_RETURN" action Return(True)

    fixed:
        xsize 1920
        ysize 1080

        button:
            xsize 1920
            ysize 1080
            background Solid("#040c20cc")
            action Return(True)

        add Transform("images/ui/logo_pgt_white.png", size=(116, 116), fit="contain") xpos 28 ypos 20

        frame:
            xalign 0.5
            yalign 0.5
            xsize 760
            background Frame("images/ui/round_outer_bg.png", 28, 28)
            padding (48, 40)

            vbox:
                spacing 24
                xfill True

                text title_txt size 34 color "#7ae8ff" bold True xalign 0.5 text_align 0.5
                text desc_txt size 24 color "#ffffff" xalign 0.5 text_align 0.5 line_spacing 6

                textbutton "Начать":
                    xalign 0.5
                    action Return(True)
                    background Frame("images/ui/round_btn_active.png", 18, 18)
                    hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                    padding (54, 16)
                    text_size 26
                    text_bold True
                    text_color "#ffffff"

# ------------------------------------------------------------------------------
# ЭКРАН 1: ТУРНИКЕТ
# ------------------------------------------------------------------------------
screen screen_minigame_turnstile():
    modal True

    if mg_turnstile.status != "success":
        timer 0.11 action Function(mg_turnstile.update_gauge) repeat True
        key "K_SPACE" action Function(mg_turnstile.swipe)
        key "K_RETURN" action Function(mg_turnstile.swipe)
    else:
        timer 1.5 action Return(True)
        key "K_SPACE" action Return(True)
        key "K_RETURN" action Return(True)

    fixed:
        xsize 1920
        ysize 1080

        add TurnstileDisplayable(mg_turnstile)
        add Transform("images/ui/logo_pgt_white.png", size=(116, 116), fit="contain") xpos 28 ypos 20

        if mg_turnstile.status != "success" and mg_turnstile.attempts >= 3:
            textbutton "Пропустить":
                xalign 0.97
                ypos 28
                action [SetField(mg_turnstile, "skipped", True), SetField(mg_turnstile, "status", "success"), Return(True)]
                background Frame("images/ui/round_btn_idle.png", 18, 18)
                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                text_size 24
                text_bold True
                text_color "#ffffff"
                padding (28, 16)

# ------------------------------------------------------------------------------
# ЭКРАН 3: АКТОВЫЙ ЗАЛ (ОСМЫСЛЕННЫЙ КУПЛЕТ ПЕСНИ + ПЕНАЛЬТИ ЗА ФАЛЬШЬ)
# ------------------------------------------------------------------------------
screen screen_minigame_vocal():
    modal True

    if not mg_vocal.is_finished():
        timer 0.04 action Function(mg_vocal.update_tick) repeat True
    else:
        timer 1.5 action Return(True)

    key "K_LEFT" action Function(mg_vocal.move_player, -0.055)
    key "K_RIGHT" action Function(mg_vocal.move_player, 0.055)
    key "a" action Function(mg_vocal.move_player, -0.055)
    key "d" action Function(mg_vocal.move_player, 0.055)
    key "A" action Function(mg_vocal.move_player, -0.055)
    key "D" action Function(mg_vocal.move_player, 0.055)
    key "ф" action Function(mg_vocal.move_player, -0.055)
    key "в" action Function(mg_vocal.move_player, 0.055)
    key "Ф" action Function(mg_vocal.move_player, -0.055)
    key "В" action Function(mg_vocal.move_player, 0.055)

    fixed:
        xsize 1920
        ysize 1080

        add "images/mg/vocal_stage_bg.png"
        add VocalStageController(mg_vocal, 1920, 1080)

        if not mg_vocal.is_finished():
            for item in mg_vocal.falling_words:
                frame:
                    background Frame("images/ui/round_vocal_word.png", 18, 18)
                    xpos int(item["x"] * 1920)
                    xanchor 0.5
                    ypos int(item["y"] * 855)
                    yanchor 0.5
                    padding (24, 12)
                    text item["word"] size 28 color "#ffffff" bold True

            for pop in mg_vocal.popups:
                text pop["text"] size 32 color "#7ae8ff" bold True xpos int(pop["x"] * 1920) xanchor 0.5 ypos int(pop["y"] * 855)

        $ singer_bob = int(abs(math.sin(mg_vocal.step_phase)) * 10) if not mg_vocal.is_finished() else 0
        add Transform("images/mg/schoolboy_singer.png", size=(184, 260), fit="contain", xzoom=(-1.0 if mg_vocal.facing < 0 else 1.0)):
            xpos int(mg_vocal.player_x * 1920)
            xanchor 0.5
            ypos (880 - singer_bob)
            yanchor 1.0

        add "images/mg/vocal_stage_fg.png"
        add Transform("images/ui/logo_pgt_white.png", size=(116, 116), fit="contain") xpos 28 ypos 20

        # Лаконичный скруглённый телесуфлёр в стиле Persona 3 Reload с общим собранным текстом
        frame:
            xalign 0.5
            ypos 16
            xsize 1320
            background Frame("images/ui/round_vocal_hud.png", 22, 22)
            padding (32, 14)
            vbox:
                spacing 8
                xfill True
                fixed:
                    xfill True
                    ysize 36
                    text "[len(mg_vocal.collected_words)] / [mg_vocal.target_count]" size 25 color "#7ae8ff" bold True xalign 0.0 yalign 0.5
                    if not mg_vocal.is_finished():
                        text ("«" + mg_vocal.current_target_phrase() + "»") size 27 color "#ffffff" bold True xalign 0.5 yalign 0.5
                    text "Штрафы: [mg_vocal.mistakes]" size 24 color "#ffffff" bold True xalign 1.0 yalign 0.5
                text mg_vocal.sung_preview() size 21 color "#b8e6ff" xalign 0.5 text_align 0.5

        # Полупрозрачная табличка посередине экрана по всей ширине (как в сборке сайта)
        if mg_vocal.is_finished():
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
                    text "ГИМН ИСПОЛНЕН УСПЕШНО!" size 46 color "#ffffff" bold True xalign 0.5 yalign 0.5 text_align 0.5
                    add Solid("#00e5ff") xsize 1920 ysize 4 yalign 1.0

            button:
                xsize 1920
                ysize 1080
                background None
                action Return(True)

# ------------------------------------------------------------------------------
# ЭКРАН 4А: СВАРКА ШАБЛОНА «ПГТ» (УЖЕСТОЧЁННАЯ)
# ------------------------------------------------------------------------------
screen screen_minigame_weld():
    modal True

    if not mg_weld.is_all_welded() and not mg_weld.failed:
        timer 0.12 action Function(mg_weld.tick_heat) repeat True

    fixed:
        xsize 1920
        ysize 1080

        if renpy.loadable("images/bg/pgt_welding_workshop.png"):
            add Transform("images/bg/pgt_welding_workshop.png", size=(1920, 1080), fit="cover", matrixcolor=BrightnessMatrix(-0.58))
        else:
            add Solid("#05102a")

        fixed:
            ypos 10
            xpos 40
            xsize 1840
            ysize 84

            hbox:
                xalign 0.0
                yalign 0.5
                spacing 20
                add Transform("images/ui/logo_pgt_white.png", size=(80, 80), fit="contain") yalign 0.5
                frame:
                    yalign 0.5
                    background Frame("images/ui/round_weld_hud.png", 18, 18)
                    padding (26, 12)
                    hbox:
                        spacing 34
                        text "[mg_weld.progress_percent()]%" size 28 color "#7ae8ff" bold True yalign 0.5
                        text "Электрод: [int(mg_weld.points)]%" size 28 color "#ffffff" bold True yalign 0.5

            textbutton "Заново":
                xalign 1.0
                yalign 0.5
                action Function(mg_weld.retry_electrode)
                background Frame("images/ui/round_btn_idle.png", 18, 18)
                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                text_size 25
                text_bold True
                text_color "#ffffff"
                padding (32, 12)

        frame:
            xalign 0.5
            ypos 100
            background Frame("images/ui/round_weld_hud.png", 18, 18)
            padding (8, 8)
            add WeldContourDisplayable(mg_weld)

        # Модальное скруглённое окно брака без лишнего текста
        if mg_weld.failed:
            frame:
                xalign 0.5
                yalign 0.5
                xsize 640
                background Frame("images/ui/round_mg_red_modal.png", 28, 28)
                padding (44, 38)
                vbox:
                    spacing 24
                    xalign 0.5
                    text "ЭЛЕКТРОД СГОРЕЛ" size 38 color "#7ae8ff" bold True xalign 0.5
                    textbutton "Заново":
                        xalign 0.5
                        action Function(mg_weld.retry_electrode)
                        background Frame("images/ui/round_mg_red_btn.png", 18, 18)
                        hover_background Frame("images/ui/round_mg_red_btn_hover.png", 18, 18)
                        text_size 28
                        text_bold True
                        text_color "#ffffff"
                        padding (52, 16)

        if mg_weld.is_all_welded():
            textbutton "ДАЛЕЕ":
                xalign 0.5
                ypos 962
                action Return(True)
                background Frame("images/ui/round_mg_green.png", 20, 20)
                hover_background Frame("images/ui/round_mg_green_hover.png", 20, 20)
                text_size 34
                text_bold True
                text_color "#ffffff"
                padding (68, 18)

# ------------------------------------------------------------------------------
# ЭКРАН 7А: ПРОФОРИЕНТАЦИОННЫЙ ИТОГ ПО РЕЗУЛЬТАТАМ ВСЕХ ИГР
# ------------------------------------------------------------------------------
screen screen_career_result():
    modal True

    $ rec = career_summary if career_summary is not None else compute_career_recommendation()
    $ best = rec["best"]
    $ finish_action = [
        SetVariable("recommended_spec_id", best["spec_id"]),
        SetVariable("selected_cat", best["cat"]),
        SetVariable("selected_specialty", best["spec_id"]),
        Return(True)
    ]

    key "dismiss" action finish_action
    key "K_SPACE" action finish_action
    key "K_RETURN" action finish_action

    fixed:
        xsize 1920
        ysize 1080
        add Solid("#070e14e8")

        frame:
            xalign 0.5
            yalign 0.5
            xsize 1844
            ysize 1004
            background Frame("images/ui/round_outer_bg.png", 32, 32)
            padding (48, 42)

            vbox:
                spacing 28
                xsize 1748
                ysize 920

                # Верхний блок с увеличенной эмблемой техникума, рекомендованным направлением и стикером пасхалки
                frame:
                    xsize 1748
                    ysize 196
                    background Frame("images/ui/round_top_card.png", 26, 26)
                    padding (40, 26)

                    fixed:
                        xsize 1668
                        ysize 144

                        hbox:
                            spacing 34
                            xalign 0.0
                            yalign 0.5
                            add Transform("images/ui/logo_pgt_white.png", size=(140, 140), fit="contain") yalign 0.5
                            vbox:
                                spacing 12
                                yalign 0.5
                                text "Вам подходит направление:" size 32 color "#7ae8ff" bold True
                                text "[best['label']]" size 42 color "#ffffff" bold True

                        # Стикер найденного золотого аттестата (или заблокированный чёрный стикер с замочком)
                        frame:
                            xalign 1.0
                            yalign 0.5
                            xsize 340
                            ysize 140
                            background Frame("images/ui/round_subcard.png", 20, 20)
                            padding (18, 14)

                            hbox:
                                spacing 16
                                xalign 0.5
                                yalign 0.5

                                fixed:
                                    xsize 82
                                    ysize 112
                                    yalign 0.5
                                    if gold_attestat_found:
                                        add Transform("images/mg/true_gold_atestato.png", size=(78, 110), fit="contain") xalign 0.5 yalign 0.5
                                    else:
                                        add Transform("images/mg/true_gold_atestato.png", size=(78, 110), fit="contain", matrixcolor=TintMatrix("#161b24") * BrightnessMatrix(-0.45)) xalign 0.5 yalign 0.5
                                        add Transform("images/ui/lock_icon.png", size=(42, 42), fit="contain") xalign 0.5 yalign 0.5

                                vbox:
                                    spacing 6
                                    yalign 0.5
                                    if gold_attestat_found:
                                        text "ЗОЛОТОЙ АТТЕСТАТ" size 18 color "#ffd858" bold True
                                        text "Найден! +100% к шансам" size 17 color "#ffffff"
                                    else:
                                        text "Аттестат не найден" size 19 color "#9ab0c9" bold True

                # Выровненные строки и скруглённые хот-бары процентов по всем 6 направлениям
                frame:
                    xsize 1748
                    ysize 696
                    background Frame("images/ui/round_panel.png", 26, 26)
                    padding (44, 34)

                    vbox:
                        xsize 1660
                        yalign 0.5
                        spacing 18

                        for item in rec["all"]:
                            $ sc = item["score"]
                            $ is_top = (item["spec_id"] == best["spec_id"])
                            fixed:
                                xsize 1660
                                ysize 86

                                fixed:
                                    xpos 0
                                    yalign 0.5
                                    xsize 660
                                    ysize 86
                                    text item["label"] size 25 bold is_top color ("#7ae8ff" if is_top else "#ffffff") xalign 0.0 yalign 0.5

                                frame:
                                    xpos 680
                                    yalign 0.5
                                    xsize 850
                                    ysize 36
                                    background Frame("images/ui/round_bar_track.png", 18, 18)
                                    padding (2, 2)
                                    frame:
                                        xalign 0.0
                                        yalign 0.5
                                        xsize max(36, int(846 * sc / 100.0))
                                        ysize 32
                                        background Frame("images/ui/round_bar_fill_top.png" if is_top else "images/ui/round_bar_fill_norm.png", 16, 16)

                                fixed:
                                    xpos 1550
                                    yalign 0.5
                                    xsize 110
                                    ysize 86
                                    text "[sc]%" size 28 bold True color ("#7ae8ff" if is_top else "#ffffff") xalign 1.0 yalign 0.5

        # Полноэкранная область клика для перехода дальше без лишней кнопки
        button:
            xsize 1920
            ysize 1080
            background None
            action finish_action

# ------------------------------------------------------------------------------
# ЭКРАН 7Б: ПОЛНЫЙ ИНТЕРАКТИВНЫЙ БУКЛЕТ СПЕЦИАЛЬНОСТЕЙ И ПРОФЕССИЙ ПГТ (23 ШТ.)
# Однородное оформление (Белый-Синий-Голубой), краткие выжимки на 1 страницу без прокрутки
# ------------------------------------------------------------------------------
screen screen_pgt_presentation():
    modal True

    $ cat_specs = [sp for sp in PGT_ALL_SPECIALTIES if sp["cat"] == selected_cat]
    $ cur_spec = get_specialty_by_id(selected_specialty)

    fixed:
        xsize 1920
        ysize 1080
        add Solid("#05102af2")

        frame:
            xalign 0.5
            yalign 0.5
            xsize 1892
            ysize 1056
            background Frame("images/ui/round_outer_bg.png", 32, 32)
            padding (24, 18)

            vbox:
                spacing 14
                xsize 1844
                ysize 1020

                # Верхняя шапка с увеличенной эмблемой техникума
                fixed:
                    xsize 1844
                    ysize 110

                    hbox:
                        xalign 0.0
                        yalign 0.5
                        spacing 24
                        add Transform("images/ui/logo_pgt_white.png", size=(110, 110), fit="contain") yalign 0.5
                        text "ГБПОУ «ПРОКОПЬЕВСКИЙ ГОРНОТЕХНИЧЕСКИЙ ТЕХНИКУМ ИМ. В.П. РОМАНОВА»" size 28 color "#ffffff" bold True yalign 0.5

                    button:
                        xalign 1.0
                        yalign 0.5
                        background Frame("images/ui/round_btn_active.png", 20, 20)
                        hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                        action Return()
                        padding (42, 18)
                        text "Далее" size 28 bold True color "#ffffff" xalign 0.5 yalign 0.5

                # Верхние вкладки направлений: 5 * 360 + 4 * 11 = 1844 px
                hbox:
                    xsize 1844
                    spacing 11
                    for cid, ctitle in PGT_BOOKLET_CATEGORIES:
                        $ is_cat = (selected_cat == cid)
                        $ first_in_cat = [sp["id"] for sp in PGT_ALL_SPECIALTIES if sp["cat"] == cid][0]
                        button:
                            xsize 360
                            ysize 68
                            background Frame("images/ui/round_btn_active.png" if is_cat else "images/ui/round_btn_idle.png", 20, 20)
                            hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                            action [SetVariable("selected_cat", cid), SetVariable("selected_specialty", first_in_cat)]
                            padding (12, 8)
                            text ctitle size 25 bold True color ("#ffffff" if is_cat else "#b8dcff") xalign 0.5 yalign 0.5 text_align 0.5

                # Основная сетка: слева список специальностей (640 px) + отступ (26 px) + текстовое описание справа (1178 px) = 1844 px
                hbox:
                    xsize 1844
                    ysize 814
                    spacing 26

                    vbox:
                        xsize 640
                        ysize 814
                        spacing 12

                        for sp in cat_specs:
                            $ is_active = (selected_specialty == sp["id"])
                            $ is_rec = (recommended_spec_id == sp["id"])
                            button:
                                xsize 640
                                ysize 124
                                background Frame("images/ui/round_btn_active.png" if is_active else ("images/ui/round_btn_rec.png" if is_rec else "images/ui/round_btn_idle.png"), 20, 20)
                                hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                                action SetVariable("selected_specialty", sp["id"])
                                padding (20, 14)

                                vbox:
                                    xsize 600
                                    yalign 0.5
                                    spacing 6
                                    text (sp["short"] + ("  (ВАШ ПРОФИЛЬ)" if is_rec else "")) size 22 bold True color ("#7ae8ff" if is_rec and not is_active else "#ffffff")
                                    text (sp["id"] + "  •  " + sp["qual"][:44]) size 18 color ("#ffffff" if is_active else "#9ac8ff")

                    # Правая панель: сплошной текст без вложенных блоков на 1 страницу
                    frame:
                        background Frame("images/ui/round_panel.png", 26, 26)
                        xsize 1178
                        ysize 814
                        padding (38, 30)

                        vbox:
                            spacing 14
                            xsize 1102

                            text cur_spec["title"] size 30 color "#7ae8ff" bold True line_spacing 4
                            text ("Квалификация: " + cur_spec["qual"]) size 24 color "#ffffff" bold True line_spacing 4
                            text ("Срок и форма обучения: " + cur_spec["term"]) size 22 color "#b8e6ff"
                            null height 4
                            text cur_spec["desc"] size 23 color "#f0f7ff" line_spacing 6

# ------------------------------------------------------------------------------
# ЭКРАН 7В: ОТДЕЛЬНОЕ ОКНО КОНТАКТНЫХ ДАННЫХ И ССЫЛОК ПОСЛЕ БРОШЮРЫ
# ------------------------------------------------------------------------------
screen screen_pgt_contacts():
    modal True

    fixed:
        xsize 1920
        ysize 1080
        add Solid("#05102af2")

        frame:
            xalign 0.5
            yalign 0.5
            xsize 1320
            ysize 720
            background Frame("images/ui/round_outer_bg.png", 32, 32)
            padding (54, 44)

            vbox:
                spacing 28
                xsize 1212
                yfill True

                hbox:
                    spacing 28
                    xalign 0.0
                    add Transform("images/ui/logo_pgt_white.png", size=(132, 132), fit="contain") yalign 0.5
                    text "КОНТАКТЫ" size 82 color "#ffffff" bold True yalign 0.5

                frame:
                    background Frame("images/ui/round_panel.png", 24, 24)
                    xsize 1212
                    padding (42, 30)

                    vbox:
                        spacing 18
                        xsize 1128

                        fixed:
                            xsize 1128
                            ysize 36
                            text "Адрес:" size 26 color "#7ae8ff" bold True xalign 0.0 yalign 0.5
                            text "г. Прокопьевск, ул. Шишкина, д. 26" size 27 color "#ffffff" bold True xalign 1.0 yalign 0.5

                        fixed:
                            xsize 1128
                            ysize 36
                            text "Телефоны:" size 26 color "#7ae8ff" bold True xalign 0.0 yalign 0.5
                            text "+7 (384) 666-80-08  •  Приёмная: 66-80-20" size 26 color "#ffffff" bold True xalign 1.0 yalign 0.5

                        fixed:
                            xsize 1128
                            ysize 36
                            text "Электронная почта:" size 26 color "#7ae8ff" bold True xalign 0.0 yalign 0.5
                            text "pgtkromanov@mail.ru" size 26 color "#d8eeff" bold True xalign 1.0 yalign 0.5

                hbox:
                    xsize 1212
                    spacing 24
                    textbutton "pgt.kemobl.ru":
                        xsize 388
                        action OpenURL("https://pgt.kemobl.ru/")
                        background Frame("images/ui/round_link_idle.png", 18, 18)
                        hover_background Frame("images/ui/round_link_hover.png", 18, 18)
                        padding (24, 18)
                        text_size 25
                        text_color "#ffffff"
                        text_hover_color "#ffffff"
                        text_bold True
                        text_xalign 0.5
                    textbutton "vk.com/pgt_romanov":
                        xsize 388
                        action OpenURL("https://vk.com/pgt_romanov")
                        background Frame("images/ui/round_link_idle.png", 18, 18)
                        hover_background Frame("images/ui/round_link_hover.png", 18, 18)
                        padding (24, 18)
                        text_size 25
                        text_color "#ffffff"
                        text_hover_color "#ffffff"
                        text_bold True
                        text_xalign 0.5
                    textbutton "MAX":
                        xsize 388
                        action OpenURL("https://max.ru/id4223000033_gos")
                        background Frame("images/ui/round_link_idle.png", 18, 18)
                        hover_background Frame("images/ui/round_link_hover.png", 18, 18)
                        padding (24, 18)
                        text_size 25
                        text_color "#ffffff"
                        text_hover_color "#ffffff"
                        text_bold True
                        text_xalign 0.5

                textbutton "Завершить":
                    xsize 1212
                    yalign 1.0
                    action Return(True)
                    background Frame("images/ui/round_btn_active.png", 20, 20)
                    hover_background Frame("images/ui/round_btn_hover.png", 20, 20)
                    padding (64, 20)
                    text_size 30
                    text_bold True
                    text_color "#ffffff"
                    text_xalign 0.5


# ------------------------------------------------------------------------------
# ЧИТ-ПАНЕЛЬ БЫСТРОГО ПЕРЕМЕЩЕНИЯ ПО ИГРЕ (АКТИВАЦИЯ ПО НАЖАТИЮ Q + W + E)
# ------------------------------------------------------------------------------
default cheat_panel_open = False

init python:

    class CheatChordListenerDisplayable(renpy.Displayable):
        """Отслеживает одновременное или быстрое нажатие Q+W+E (Й+Ц+У) поверх любых экранов."""
        def __init__(self, **kwargs):
            super(CheatChordListenerDisplayable, self).__init__(**kwargs)
            self.key_times = {}
            self.last_toggle = -10.0

        def render(self, width, height, st, at):
            return renpy.Render(0, 0)

        def event(self, ev, x, y, st):
            if ev.type != pygame.KEYDOWN:
                return None

            k = getattr(ev, "key", None)
            u = (getattr(ev, "unicode", "") or "").lower()

            slot = None
            if k == pygame.K_q or u in ("q", "й"):
                slot = "q"
            elif k == pygame.K_w or u in ("w", "ц"):
                slot = "w"
            elif k == pygame.K_e or u in ("e", "у"):
                slot = "e"

            if slot is None:
                return None

            self.key_times[slot] = st

            held_all = False
            try:
                pressed = pygame.key.get_pressed()
                held_all = bool(pressed[pygame.K_q] and pressed[pygame.K_w] and pressed[pygame.K_e])
            except Exception:
                held_all = False

            recent_all = (
                len(self.key_times) == 3
                and all((st - t) <= 0.55 for t in self.key_times.values())
            )

            if (held_all or recent_all) and (st - self.last_toggle) >= 0.35:
                self.last_toggle = st
                self.key_times.clear()
                renpy.store.cheat_panel_open = not getattr(renpy.store, "cheat_panel_open", False)
                renpy.restart_interaction()
                raise renpy.IgnoreEvent()

            return None

    def cheat_jump_to(target_label):
        renpy.store.cheat_panel_open = False
        renpy.store.gold_attestat_popup = False
        renpy.hide_screen("screen_gold_attestat_hotspot")
        renpy.hide_screen("screen_info_stand")
        renpy.music.stop(channel="music", fadeout=0.2)
        renpy.music.stop(channel="sound")
        renpy.music.stop(channel="voice")
        if target_label == "after_mg_kitchen":
            if not mg_kitchen.has_all():
                mg_kitchen.collected = ["bun", "patty", "cheese", "lettuce", "tomato", "sauce"]
            mg_kitchen.done = True
        elif target_label in ("after_mg_burger", "after_mg_career"):
            if not getattr(mg_burger, "served", False):
                mg_burger.grade = "perfect"
                mg_burger.served = True
        renpy.jump(target_label)

    if "screen_cheat_overlay" not in config.overlay_screens:
        config.overlay_screens.append("screen_cheat_overlay")


screen screen_cheat_overlay():
    zorder 1500
    modal cheat_panel_open

    add CheatChordListenerDisplayable()

    if cheat_panel_open:
        key "K_ESCAPE" action SetVariable("cheat_panel_open", False)

        fixed:
            xsize 1920
            ysize 1080

            button:
                xsize 1920
                ysize 1080
                background Solid("#030a1cd8")
                action SetVariable("cheat_panel_open", False)

            frame:
                xalign 0.5
                yalign 0.5
                xsize 1280
                background Frame("images/ui/round_outer_bg.png", 32, 32)
                padding (44, 36)

                vbox:
                    spacing 22
                    xsize 1192

                    fixed:
                        xsize 1192
                        ysize 64
                        text "ПАНЕЛЬ ПЕРЕХОДОВ ПО ИГРЕ (Q+W+E)" size 32 color "#7ae8ff" bold True xalign 0.0 yalign 0.5
                        textbutton "Закрыть":
                            xalign 1.0
                            yalign 0.5
                            action SetVariable("cheat_panel_open", False)
                            background Frame("images/ui/round_btn_idle.png", 18, 18)
                            hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                            padding (28, 12)
                            text_size 23
                            text_bold True
                            text_color "#ffffff"

                    hbox:
                        xsize 1192
                        spacing 20

                        vbox:
                            xsize 586
                            spacing 14

                            textbutton "1. После турникета (Проходная)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_turnstile")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "2. После сборки сайта (ИТ-центр)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_site")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "3. После вокала (Актовый зал)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_vocal")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "4. После сварки (Мастерская)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_weld")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "5. После электрики (Никола Тесла)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_wiring")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                        vbox:
                            xsize 586
                            spacing 14

                            textbutton "6. После шахты (2-й корпус)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_mine")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "7. После ремонта станка":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_pipes")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "8. После кулинарного цеха (К бутеру)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_kitchen")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "9. После сборки бутерброда (Финал)":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_burger")
                                background Frame("images/ui/round_btn_idle.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5

                            textbutton "10. Итоги и брошюра специальностей":
                                xsize 586
                                ysize 74
                                action Function(cheat_jump_to, "after_mg_career")
                                background Frame("images/ui/round_btn_active.png", 18, 18)
                                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                                padding (24, 16)
                                text_size 23
                                text_bold True
                                text_color "#ffffff"
                                text_yalign 0.5


# ------------------------------------------------------------------------------
# ПАСХАЛКА: ЗОЛОТОЙ АТТЕСТАТ НА ИНФОРМАЦИОННОМ СТЕНДЕ (В СТИЛЕ TURNIP BOY)
# ------------------------------------------------------------------------------
default gold_attestat_found = False
default gold_attestat_popup = False

transform gold_cert_center_hover:
    subpixel True
    on idle:
        easeout 0.14 zoom 1.0
    on hover:
        easein 0.14 zoom 1.035

transform turnip_popup_zoom_in:
    subpixel True
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    zoom 0.0
    alpha 0.0
    parallel:
        easein 0.14 alpha 1.0
    parallel:
        easein 0.24 zoom 1.07
        easeout 0.12 zoom 1.0

transform turnip_star_spin(xp=205, yp=230):
    subpixel True
    transform_anchor True
    anchor (0.5, 0.5)
    xpos xp
    ypos yp
    rotate 0.0
    linear 8.5 rotate 360.0
    repeat

transform turnip_item_rock(xp=205, yp=230):
    subpixel True
    transform_anchor True
    anchor (0.5, 0.5)
    xpos xp
    ypos yp
    rotate -8.5
    block:
        ease 0.85 rotate 8.5
        ease 0.85 rotate -8.5
        repeat

# Хотспот поверх коридора: кликабелен СТРОГО только полигон золотого аттестата на стенде
screen screen_gold_attestat_hotspot():
    zorder 150

    imagebutton:
        xpos 0
        ypos 0
        idle Solid("#00000000", xsize=1920, ysize=1080)
        hover "images/ui/gold_cert_hover.png"
        focus_mask "images/ui/gold_cert_mask.png"
        action [
            SetVariable("gold_attestat_popup", False),
            Play("sound", "audio/pc_slide.wav"),
            Show("screen_info_stand", transition=Dissolve(0.45)),
        ]

# Полноэкранный информационный стенд (info) с пасхалкой в стиле Turnip Boy
screen screen_info_stand():
    zorder 250
    modal True

    key "K_ESCAPE" action [SetVariable("gold_attestat_popup", False), Hide("screen_info_stand", transition=Dissolve(0.45))]

    fixed:
        xsize 1920
        ysize 1080

        add "images/bg/info_stand.png"
        add Transform("images/ui/logo_pgt_black.png", size=(116, 116), fit="contain") xpos 28 ypos 20

        # Слева под небольшим углом — фото apreshen («Этому Поганцу вход на кухню запрещён»)
        add Transform(Solid("#1a0e0666", xsize=340, ysize=415), rotate=-7.0, subpixel=True):
            xpos 518
            ypos 582
            anchor (0.5, 0.5)
        add Transform("images/mg/apreshen.png", size=(340, 415), fit="contain", rotate=-7.0, subpixel=True):
            xpos 510
            ypos 572
            anchor (0.5, 0.5)

        # Справа на стенде оставлено свободное место под будущее фото (x ~ 1210..1650)

        # Посередине — золотой аттестат без белого фона (кликабелен)
        add Solid("#1a0e0670", xsize=380, ysize=546):
            xpos 968
            ypos 574
            anchor (0.5, 0.5)

        if not gold_attestat_popup:
            imagebutton:
                xpos 960
                ypos 564
                anchor (0.5, 0.5)
                idle Transform("images/mg/true_gold_atestato.png", size=(380, 546), fit="contain")
                hover Transform("images/mg/true_gold_atestato.png", size=(380, 546), fit="contain")
                at gold_cert_center_hover
                action [
                    SetVariable("gold_attestat_found", True),
                    SetVariable("gold_attestat_popup", True),
                    Play("sound", "audio/bun_win.wav"),
                ]

            textbutton "Назад":
                xalign 0.96
                yalign 0.96
                action Hide("screen_info_stand", transition=Dissolve(0.45))
                background Frame("images/ui/round_btn_idle.png", 18, 18)
                hover_background Frame("images/ui/round_btn_hover.png", 18, 18)
                padding (38, 16)
                text_size 26
                text_bold True
                text_color "#ffffff"
        else:
            add Transform("images/mg/true_gold_atestato.png", size=(380, 546), fit="contain"):
                xpos 960
                ypos 564
                anchor (0.5, 0.5)

            # Затемнение заднего плана и закрытие окна по клику
            button:
                xsize 1920
                ysize 1080
                background Solid("#0c070499")
                action [
                    SetVariable("gold_attestat_popup", False),
                    Hide("screen_info_stand", transition=Dissolve(0.45)),
                ]

            key "K_SPACE" action [SetVariable("gold_attestat_popup", False), Hide("screen_info_stand", transition=Dissolve(0.45))]
            key "K_RETURN" action [SetVariable("gold_attestat_popup", False), Hide("screen_info_stand", transition=Dissolve(0.45))]

            # Всплывающая из середины светло-коричневая табличка в стиле Turnip Boy
            fixed at turnip_popup_zoom_in:
                xsize 1280
                ysize 460

                # Светло-коричневая табличка
                add Transform("images/ui/turnip_plaque.png", size=(1120, 314), fit="contain"):
                    xpos 140
                    ypos 73

                # У левого края таблички — кружащаяся жёлтая многоконечная звезда + покачивающийся аттестат
                add Transform("images/ui/turnip_star.png", size=(390, 390), fit="contain") at turnip_star_spin(205, 230)
                add Transform("images/mg/true_gold_atestato.png", size=(182, 261), fit="contain") at turnip_item_rock(205, 230)

                # Текст на табличке справа от звезды
                fixed:
                    xpos 405
                    ypos 93
                    xsize 820
                    ysize 274

                    vbox:
                        spacing 20
                        xalign 0.5
                        yalign 0.5
                        text "Вы нашли золотой аттестат!" size 40 bold True color "#4a2a10" xalign 0.5 text_align 0.5
                        text "Ваши шансы на поступление увеличены на 100%!" size 27 bold True color "#6e421c" xalign 0.5 text_align 0.5
