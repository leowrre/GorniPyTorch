## ==============================================================================
## ГЛАВНЫЙ СЦЕНАРИЙ: ГОРНЫЙ ТЕХНИКУМ (ГБПОУ ПГТ ИМ. В.П. РОМАНОВА)
## ==============================================================================

# ------------------------------------------------------------------------------
# ФОНОВЫЕ ИЗОБРАЖЕНИЯ (ОПТИМИЗИРОВАННЫЕ WEBP БЕЗ ПОТЕРИ КАЧЕСТВА)
# ------------------------------------------------------------------------------
image bg pgt_entrance = "images/bg/pgt_outside_2.webp"                  # Вход и очищенный фасад главного корпуса ПГТ
image bg pgt_checkpoint = "images/bg/pgt_checkpoint.webp"               # Проходная с турникетом и рамками
image bg pgt_hall_floor2 = "images/bg/pgt_inside.webp"                  # Главный холл и арка к лестнице
image bg pgt_it_entrance = "images/bg/pgt_it_entrance.webp"             # Стеклянный вход в мастерские ИКТ (2-й этаж)
image bg pgt_it_corridor = "images/bg/koridor_it.webp"                  # Коридор ИТ-центра
image bg pgt_it_maki = "images/bg/maki.webp"                            # Кабинет с iMac (Маки)
image bg pgt_it_center = "images/bg/sait_sloman.webp"                   # Компьютерный центр (сломанный сайт)
image bg pgt_web_dev = "images/bg/veb_rozrabo.webp"                     # Схема шаблонов веб-разработки на доске
image bg pgt_interactive_display = "images/bg/otovyi_ekran.webp"        # Зал с интерактивным сенсорным дисплеем (готовый экран)
image bg pgt_hallway_3 = "images/bg/pgt_hallway_3.webp"                 # Подъём по лестнице на 3-й этаж
image bg pgt_assembly_hall = "images/bg/actoviy.webp"                   # Актовый зал
image bg pgt_corridor_long = "images/bg/pgt_corridor_long.webp"         # Длинный коридор мастерских
image bg pgt_workshop_corridor = "images/bg/pgt_workshop_corridor.webp" # Коридор у двери мастерской «Электрослесарь подземный»
image bg pgt_workshop = "images/bg/pgt_welding_workshop.webp"           # Сварочная мастерская (5-й корпус)
image bg pgt_blackout_room = Transform("images/bg/mep_main.webp", matrixcolor=TintMatrix("#8cb8ff") * BrightnessMatrix(-0.62))
image bg pgt_mine_polygon = "images/bg/pgt_mine_polygon.webp"           # Открытый вход на учебный подземный полигон
image bg pgt_mine_entry = "images/bg/pgt_mine_entry.webp"
image bg pgt_mine_tunnel = "images/bg/poligon.webp"
image bg pgt_mine_drill = "images/bg/poligon.webp"
image bg pgt_mine_breakthrough = "images/bg/poligon.webp"
image bg pgt_toilet_exit = "images/bg/koridor_vichust_center.webp"      # Коридор вычислительного центра во 2-м корпусе
image bg pgt_novii_koridor = "images/bg/novii_koridor.webp"             # Коридор со стендом и золотым аттестатом
image bg pgt_stairs_2 = "images/bg/dver_povarov.webp"                   # Дверь у поваров во 2-м корпусе
image bg pgt_culinary_hall = "images/bg/stolovaya.webp"                 # Учебная лаборатория поварского дела
image bg pgt_finish = "images/bg/pgt_outside_2.webp"                    # Финальный двор у входа (первое фото)

# Спрайты персонажей (заранее отмасштабированы в WebP под целевую высоту экрана)
image prep = "images/chars/prep.webp"
image act panic = "images/chars/act_panic.webp"
image act ask   = "images/chars/act_ask.webp"
image act happy = "images/chars/act_happy.webp"
image master = "images/chars/master.webp"
image master_hand = "images/chars/master_hand.webp"
image master_hand_fist = "images/chars/master_hand_fist.webp"
image tesla = "images/chars/tesla.webp"
image chef = "images/chars/chef.webp"
image brig = "images/chars/dyayda_yura_shecter_svet.webp"
image worker = "images/chars/Muzhik_So_stankom.webp"
image worker point = "images/chars/Muzhik_so_stankom_ukazyvaet.webp"

# Спрайты Семёна (Старшак — заранее отмасштабированы в WebP с прозрачным фоном)
image sem default = "images/chars/sem_default.webp"
image sem hello   = "images/chars/sem_hello.webp"
image sem explain = "images/chars/sem_explain.webp"
image sem proud   = "images/chars/sem_proud.webp"
image sem smirk   = "images/chars/sem_smirk.webp"
image sem shrug   = "images/chars/sem_shrug.webp"
image sem epic    = "images/chars/sem_epic.webp"
image sem whisper = "images/chars/sem_whisper.webp"
image sem coat    = "images/chars/sem_coat.webp"
image sem present = "images/chars/sem_present.webp"
image sem laugh   = "images/chars/sem_laugh.webp"
image sem thumbs  = "images/chars/sem_thumbs.webp"
image sem point   = "images/chars/sem_point.webp"
image sem think   = "images/chars/sem_think.webp"
image sem shock   = "images/chars/sem_shock.webp"

# ------------------------------------------------------------------------------
# ПЕРСОНАЖИ
# ------------------------------------------------------------------------------
define gg = Character("Школьник", color="#66ccff")
define sem = Character("Семён (Старшак)", image="sem", color="#a3e066")
define prep = Character("Преподаватель ИСП", color="#33ddcc")
define act = Character("Активист студсовета", image="act", color="#ff99cc")
define dima = Character("Дима (Студент-сварщик)", color="#ffcc66")
define master = Character("Мастер производственного обучения", color="#ff8844")
define tesla = Character("Никола Тесла", color="#00ffff")
define brig = Character("Бригадир дядя Юра", color="#ff5533")
define worker = Character("Мускулистый работяга", color="#ff7744")
define cook = Character("Шеф-повар", color="#ffaa55")

# Эффект яркой вспышки света при включении рубильника
define flash = Fade(0.1, 0.0, 0.4, color="#ffffff")

# Плейсхолдер-музыка из DDLC с бесшовными точками зацикливания (только инструментал без слов)
define audio.ddlc_ohayou    = "<loop 4.499>audio/bgm/ddlc_2.ogg"
define audio.ddlc_club      = "<loop 4.618>audio/bgm/ddlc_3.ogg"
define audio.ddlc_dreams    = "<loop 19.451>audio/bgm/ddlc_4.ogg"
define audio.ddlc_okay      = "<loop 4.444>audio/bgm/ddlc_5.ogg"
define audio.ddlc_play      = "<loop 10.893>audio/bgm/ddlc_6.ogg"
define audio.ddlc_panic     = "<loop 2.291>audio/bgm/ddlc_7.ogg"
define audio.ddlc_warm      = "<loop 9.938>audio/bgm/ddlc_8.ogg"
define audio.toreador_march = "<loop 0.0>audio/toreador_musicbox.wav"

# Позиции и появления Семёна на экране
transform sem_center:
    subpixel True
    xalign 0.5 yalign 1.0

transform sem_left:
    subpixel True
    xalign 0.22 yalign 1.0

transform sem_right:
    subpixel True
    xalign 0.78 yalign 1.0

transform sem_walk_in:
    subpixel True
    xalign 0.85 yalign 1.0 alpha 0.0
    easeout 0.35 xalign 0.5 alpha 1.0

# Анимации руки мастера-сварщика (вылет ладони, сжатие в кулак и рывок в дверь)
transform hand_grab_in:
    subpixel True
    xanchor 1.0 yanchor 0.5
    xpos 1.75 ypos 440 zoom 1.08
    easeout 0.18 xpos 1.0

transform hand_clench_fist:
    subpixel True
    xanchor 1.0 yanchor 0.5
    xpos 1.0 ypos 440 zoom 1.08
    easeout 0.05 zoom 1.13 ypos 428
    easein 0.07 zoom 1.08 ypos 440

transform hand_yank_out:
    subpixel True
    xanchor 1.0 yanchor 0.5
    xpos 1.0 ypos 440 zoom 1.08
    easein 0.28 xpos 1.75 ypos 460 zoom 1.22

transform bg_yanked_to_door:
    subpixel True
    xalign 0.5 yalign 0.5 zoom 1.0
    easein 0.28 zoom 1.38 xalign 1.0

# ------------------------------------------------------------------------------
# ПРОПУСК ГЛАВНОГО МЕНЮ (ИГРА ЗАПУСКАЕТСЯ СРАЗУ СО СЛАЙДОВ)
# ------------------------------------------------------------------------------
label main_menu:
    return

# ------------------------------------------------------------------------------
# СТАРТ ИГРЫ
# ------------------------------------------------------------------------------
label start:
    # Нормализация уровней микшера (тихая фоновая музыка + громкая чёткая озвучка) и отключение нижней панели
    $ quick_menu = False
    $ _preferences.volumes['music'] = 0.50
    $ _preferences.volumes['sfx'] = 0.65
    $ _preferences.volumes['voice'] = 1.0
    $ _preferences.afm_enable = True
    $ _preferences.afm_time = 4
    $ _preferences.afm_after_click = True

    # Инициализация всех мини-игр
    $ mg_turnstile.reset()
    $ mg_site.reset()
    $ mg_vocal.reset()
    $ mg_weld.reset(True)
    $ mg_wiring.reset()
    $ mg_mine.reset()
    $ mg_pipes.reset()
    $ mg_kitchen.reset(True)
    $ mg_burger.setup([])
    $ gold_attestat_popup = False

    scene bg pgt_entrance
    with fade
    play music audio.ddlc_ohayou fadein 0.8 volume 0.24

    voice "audio/voice/gg/gg01.mp3"
    gg "Эх, я живу напротив техникума, но всё равно умудрился опоздать."
    voice "audio/voice/gg/gg02.mp3"
    gg "Там уже всё закончилось, и что делать?"

    show sem hello at sem_walk_in

    voice "audio/voice/semen/semen01.mp3"
    sem "Привет, ты чего стоишь перед дверьми, ждёшь кого-то?"

    voice "audio/voice/gg/gg03.mp3"
    gg "Я шёл на день открытых дверей... но не дошёл..."

    show sem proud
    voice "audio/voice/semen/semen02.mp3"
    sem "Думаю, из официальных мероприятий ты техникум не поймёшь! Пошли со мной."

    # --------------------------------------------------------------------------
    # СЦЕНА 1: ТУРНИКЕТ (МИНИ-ИГРА 1)
    # --------------------------------------------------------------------------
    scene bg pgt_checkpoint
    with dissolve

    show sem explain at sem_right with dissolve

    show sem thumbs
    voice "audio/voice/semen/semen04.mp3"
    sem "Турникет — штука такая, капризная. Нужно нажать точно в момент, иначе ты не зайдёшь."

    hide sem with dissolve

    # Вызов экрана мини-игры 1
    call screen screen_mg_intro("ПРОХОДНАЯ", "Нажмите на экран или пробел в момент, когда индикатор турникета загорится зелёным светом.")
    call screen screen_minigame_turnstile

label after_mg_turnstile:
    scene bg pgt_checkpoint
    play music audio.ddlc_ohayou fadein 0.5 volume 0.24 if_changed
    show sem thumbs at sem_center with dissolve

    voice "audio/voice/semen/semen05.mp3"
    sem "Молодец! Первое испытание позади! Добро пожаловать в Прокопьевский горнотехнический техникум имени В.П. Романова!"

    # --------------------------------------------------------------------------
    # СЦЕНА 2: КОМПЬЮТЕРНЫЙ ЦЕНТР — СБОРКА САЙТА (МИНИ-ИГРА 2)
    # --------------------------------------------------------------------------
    scene bg pgt_it_entrance
    with fade
    play music audio.ddlc_dreams fadeout 0.6 fadein 0.6 volume 0.28

    show sem present at sem_right with dissolve

    voice "audio/voice/semen/semen06.mp3"
    sem "Первое, что видит человек на втором этаже — это компьютерный центр!"

    scene bg pgt_it_corridor
    with dissolve

    show sem present at sem_right with dissolve

    voice "audio/voice/semen/semen07.mp3"
    sem "Там учатся все айтишники нашего техникума: разработчики сайтов, разработчики видеоигр, сисадмины."

    scene bg pgt_it_maki
    with dissolve

    show sem explain at sem_right with dissolve

    voice "audio/voice/semen/semen08.mp3"
    sem "Направлений целых шесть: всё — от веб-разработки до сетей и VR!"

    # Крупный план со студентами у монитора — без перекрытия людей спрайтом
    scene bg pgt_it_center
    with dissolve

    voice "audio/voice/semen/semen09.mp3"
    sem "Видимо, на сайте нарушилось оформление. Кажется, я знаю, кто пересоберёт его. Выдвигаю твою кандидатуру на роль спасителя. Поздравляю, это твоё боевое крещение!"

    voice "audio/voice/gg/gg04.mp3"
    gg "Но я сайты даже ни разу не делал!"

    voice "audio/voice/semen/semen11.mp3"
    sem "У всех что-то всегда бывает в первый раз! Только мигающие ретро-гифки и счётчики из двухтысячных не тащи — ГОСТ такое оформление не пропустит."

    # Кадр у интерактивной доски со студентами — без перекрытия людей спрайтом
    scene bg pgt_web_dev
    with dissolve

    voice "audio/voice/semen/semen13.mp3"
    sem "Нужно вставить шаблоны, чтобы всё было аккуратно и по ГОСТам, понимаешь?"

    # Вызов экрана мини-игры 2
    call screen screen_mg_intro("СБОРКА САЙТА", "Перетащите подходящие блоки слева в пустые ячейки макета по образцу и нажмите «Собрать сайт».")
    call screen screen_minigame_site

label after_mg_site:
    # Сначала показываем восстановленный экран со студентами без перекрытия спрайтами
    scene bg pgt_interactive_display
    with dissolve
    play music audio.ddlc_club fadeout 0.5 fadein 0.5 volume 0.26 if_changed
    pause 1.1

    # Диалог с преподавателем и Семёном в свободном от людей ракурсе кабинета ИТ
    scene bg pgt_it_maki
    with dissolve

    show prep at sem_left with dissolve
    voice "audio/voice/prep/prep01.mp3"
    prep "Фантастика! Сайт снова живой, и даже блоки какие надо — все на месте! Спасибо за помощь!"
    hide prep with dissolve

    show sem proud at sem_right with dissolve

    voice "audio/voice/semen/semen14.mp3"
    sem "Не за что, я всегда готов помочь!"

    voice "audio/voice/gg/gg05.mp3"
    gg "Эй, вообще-то это я сайт собирал..."

    show sem smirk
    voice "audio/voice/semen/semen15.mp3"
    sem "Мы же команда: один трудится, второй руководит. Не благодари, пошли на третий этаж!"

    # --------------------------------------------------------------------------
    # СЦЕНА 3: АКТОВЫЙ ЗАЛ (МИНИ-ИГРА 3)
    # --------------------------------------------------------------------------
    scene bg pgt_hallway_3
    with fade
    play music audio.ddlc_okay fadeout 0.6 fadein 0.6 volume 0.26

    show sem default at sem_center with dissolve

    voice "audio/voice/semen/semen16.mp3"
    sem "Пойдём на третий этаж, мы тут не только учимся, но и «культурно и творчески развиваемся»!"

    scene bg pgt_assembly_hall
    with dissolve
    play music audio.ddlc_panic fadeout 0.4 fadein 0.4 volume 0.24

    show act panic at sem_center with dissolve
    voice "audio/voice/act/act01.mp3"
    act "Катастрофа! Через полчаса выступление для гостей Дня открытых дверей, а вокалиста для финальной репетиции нет!"

    show act ask at sem_right with dissolve
    voice "audio/voice/act/act02.mp3"
    act "Семён! Ты кого с собой привёл? А он петь-то умеет?"

    show sem epic at sem_left with dissolve

    voice "audio/voice/semen/semen17.mp3"
    sem "Конечно, умеет! В душе он рок-звезда!"
    voice "audio/voice/gg/gg06.mp3"
    gg "Да я только в ду́ше подпеваю!.."

    hide sem with dissolve
    show act happy at sem_center with dissolve

    voice "audio/voice/act/act03.mp3"
    act "Отлично, держи микрофон, двигайся по сцене и лови сверху правильные строчки студенческого гимна техникума по телесуфлёру!"

    hide act with dissolve

    # Вызов экрана мини-игры 3
    call screen screen_mg_intro("АКТОВЫЙ ЗАЛ", "Двигайтесь по сцене, ловите нужные строчки гимна по порядку и уворачивайтесь от лишних фраз.")
    call screen screen_minigame_vocal

label after_mg_vocal:
    scene bg pgt_assembly_hall
    play music audio.ddlc_club fadeout 0.5 fadein 0.5 volume 0.26 if_changed
    if mg_vocal.mistakes == 0:
        show act happy at sem_center with dissolve
        voice "audio/voice/act/act04.mp3"
        act "Браво! Ни единой заминки в тексте — стопроцентное попадание в гимн!"
        hide act with dissolve
        show sem thumbs at sem_center with dissolve
        voice "audio/voice/semen/semen18.mp3"
        sem "Это, конечно, хорошо, но пение всё равно не твоё."
    else:
        show act happy at sem_center with dissolve
        voice "audio/voice/act/act05.mp3"
        act "Браво! Пару раз сфальшивил, но упустим — финал вытянул хорошо! Спасибо, выручил!"
        hide act with dissolve
        show sem whisper at sem_center with dissolve
        voice "audio/voice/semen/semen19.mp3"
        sem "Не, пение совершенно точно не твоё."

    # --------------------------------------------------------------------------
    # СЦЕНА 4: СВАРОЧНАЯ МАСТЕРСКАЯ И НИКОЛА ТЕСЛА (МИНИ-ИГРЫ 4А И 4Б)
    # --------------------------------------------------------------------------
    scene bg pgt_corridor_long
    with fade
    play music audio.ddlc_play fadeout 0.6 fadein 0.6 volume 0.24

    show sem present at sem_left with dissolve

    voice "audio/voice/semen/semen20.mp3"
    sem "Здесь у нас учатся будущие мастера своего дела: сварщики, слесари и шахтёры."

    scene bg pgt_workshop_corridor
    with dissolve
    play music audio.ddlc_panic fadeout 0.3 fadein 0.3 volume 0.24

    voice "audio/voice/dima/dima01.mp3"
    dima "НО У МЕНЯ НИЧЕГО НЕ ПОЛУЧАЕТСЯ!"

    voice "audio/voice/master/master01.mp3"
    master "ДА Я СЕЙЧАС В КОРИДОРЕ НАЙДУ ЧЕЛОВЕКА, КОТОРЫЙ РАБОТАЕТ ЛУЧШЕ ТЕБЯ!"

    scene bg pgt_corridor_long
    with dissolve

    #show sem whisper at sem_left with dissolve

    voice "audio/voice/semen/semen21.mp3"
    sem "Уходим, уходим, ухо..."

    hide sem
    play sound "audio/stealth_spotted.wav"
    show master_hand at hand_grab_in
    with hpunch

    play sound "audio/burger_drop.wav"
    hide master_hand
    show master_hand_fist at hand_clench_fist
    with vpunch

    voice "audio/voice/gg/gg07.mp3"
    gg "Э-э-эй! Вы чего?!"

    play sound "audio/pc_slide.wav"
    show bg pgt_corridor_long at bg_yanked_to_door
    show master_hand_fist at hand_yank_out
    pause 0.28

    scene bg pgt_workshop
    with hpunch

    show master at center with dissolve

    voice "audio/voice/master/master02.mp3"
    master "Дима, отойди: сейчас этот парень покажет тебе настоящий сварочный шов! Гораздо лучше, чем твоё Аль Денте."
    voice "audio/voice/master/master03.mp3"
    master "Бери маску и держатель. Провари на сварочном столе контрольный стальной шаблон «ПГТ» — строго по контуру букв, без обрывов дуги и прожогов."

    # Вызов экрана мини-игры сварки по шаблону ПГТ
    call screen screen_mg_intro("СВАРКА ШВА «ПГТ»", "Зажгите дугу в жёлтом кольце и плавно ведите электрод по контуру букв без остановок и рывков.")
    call screen screen_minigame_weld

label after_mg_weld:
    scene bg pgt_workshop
    play music audio.ddlc_club fadeout 0.5 fadein 0.5 volume 0.26 if_changed
    show master at center
    if mg_weld.get_grade() == "perfect":
        voice "audio/voice/master/master04.mp3"
        master "А ты неплох, такой шов не у каждого мастера выходит. Учись, Дима!"
    elif mg_weld.get_grade() == "good":
        voice "audio/voice/master/master05.mp3"
        master "Для первого раза неплохо. Всё ещё лучше Диминых швов."
    else:
        voice "audio/voice/master/master06.mp3"
        master "Ну ты, конечно, делов наделал, до Димы тебе ещё далеко."

    scene bg pgt_workshop_corridor
    with dissolve

    if mg_weld.get_grade() == "perfect":
        show sem thumbs at sem_center with dissolve
        voice "audio/voice/semen/semen22.mp3"
        sem "Так хорошо даже Химик не варил!"
    elif mg_weld.get_grade() == "good":
        show sem default at sem_center with dissolve
        voice "audio/voice/semen/semen23.mp3"
        sem "Эти студенты по сравнению с тобой напрашиваются на отчисление."
    else:
        show sem laugh at sem_center with dissolve
        voice "audio/voice/semen/semen24.mp3"
        sem "Ох, зря ты это сделал."

    show sem point
    voice "audio/voice/semen/semen25.mp3"
    sem "А сейчас!.."

    stop music fadeout 0.2
    play sound "audio/fnaf_powerdown.wav"
    scene bg pgt_blackout_tesla
    with vpunch
    play music audio.toreador_march fadein 0.4 volume 0.42

    voice "audio/voice/tesla/tesla01.mp3"
    tesla "Я тут немного напакостничал с проводами... мне нужна ваша помощь, хе-хе."

    scene bg pgt_blackout_room
    show tesla at center
    with dissolve

    voice "audio/voice/gg/gg08.mp3"
    gg "Подождите, а меня что, ударит током?!"

    # Вызов экрана мини-игры с проводкой без пересечений
    call screen screen_mg_intro("ЭЛЕКТРОЩИТОВАЯ", "Распишитесь в журнале и соедините одноимённые клеммы через свои ромбы без пересечения проводов.")
    call screen screen_minigame_wiring

label after_mg_wiring:
    scene bg pgt_blackout_room
    play music audio.toreador_march fadein 0.3 volume 0.42 if_changed
    show tesla at center
    if mg_wiring.shocks == 0:
        voice "audio/voice/tesla/tesla02.mp3"
        tesla "Ни одного удара током, хорошо справились, хе-хе."
    else:
        voice "audio/voice/tesla/tesla03.mp3"
        tesla "Всего [mg_wiring.shocks] раз ударило током. Если током ударило, значит, ток есть, хе-хе."

    stop music fadeout 0.3
    scene bg pgt_workshop_corridor
    with flash

    voice "audio/voice/gg/gg09.mp3"
    gg "Э-э-э, это что только что было?.."

    show sem smirk at sem_center with dissolve
    voice "audio/voice/semen/semen26.mp3"
    sem "Э... лектрик?"

    # --------------------------------------------------------------------------
    # СЦЕНА 5: ШАХТНЫЙ ПОЛИГОН — ЗАВАЛЫ И КРЫСЫ (МИНИ-ИГРА 5)
    # --------------------------------------------------------------------------
    scene bg pgt_mine_polygon
    with fade
    play music audio.ddlc_club fadeout 0.6 fadein 0.6 volume 0.26

    show sem point at sem_right with dissolve

    voice "audio/voice/semen/semen27.mp3"
    sem "О, смотри! Открытый полигон! Пока всё равно никого нет, так что можно и прогуляться."

    scene bg pgt_mine_entry
    with dissolve

    show sem present at sem_right with dissolve

    voice "audio/voice/semen/semen28.mp3"
    sem "Этот полигон — гордость техникума. Только представь: учишься здесь, а прямо под нами — настоящая шахта!"

    scene bg pgt_mine_tunnel
    with dissolve
    play music audio.ddlc_dreams fadeout 0.5 fadein 0.5 volume 0.28

    show sem explain at sem_left with dissolve
    show brig at sem_right with dissolve

    voice "audio/voice/brig/brig01.mp3"
    brig "Где твой инструмент, парень?"

    show sem shock
    voice "audio/voice/semen/semen29.mp3"
    sem "Нуу..."

    voice "audio/voice/brig/brig02.mp3"
    brig "Возьми, твой бур пронзит небеса, Семён!"
    voice "audio/voice/semen/semen30.mp3"
    sem "Ох, спина..."

    hide sem with dissolve
    show brig
    voice "audio/voice/brig/brig03.mp3"
    brig "А ты бери заряды."
    voice "audio/voice/gg/gg10.mp3"
    gg "Я что, теперь подрывник?!"

    voice "audio/voice/brig/brig04.mp3"
    brig "Бомбу кинь и беги."

    hide brig with dissolve

    # Вызов экрана мини-игры 5
    call screen screen_mg_intro("ШАХТНЫЙ ПОЛИГОН", "Ставьте заряды кнопкой B, расчищайте завалы угля, берегитесь крыс и доберитесь до выхода.")
    call screen screen_minigame_mine

label after_mg_mine:
    #scene bg pgt_mine_drill
    #with hpunch

    #show sem epic at sem_right with hpunch

    #gg "Что за...?"
    #sem "«МОЙ БУР ПРОНЗИЛ НЕБЕСА-А-А-А!»"

    #scene bg pgt_mine_breakthrough
    #with vpunch

    # --------------------------------------------------------------------------
    # СЦЕНА 6: ВТОРОЙ КОРПУС, РАБОТЯГИ СО СТАНКОМ, КУХНЯ И БУТЕР ДЛЯ СЕМЁНА
    # --------------------------------------------------------------------------
    scene black
    with fade

    pause 0.6

    scene bg pgt_novii_koridor
    with dissolve
    play music audio.ddlc_okay fadeout 0.6 fadein 0.6 volume 0.26

    voice "audio/voice/gg/gg11.mp3"
    gg "Погоди... мы что, вышли во втором корпусе?"

    show sem default at sem_center with dissolve

    voice "audio/voice/semen/semen31.mp3"
    sem "Ага, вот и сократили дорогу, кстати, да!.."

    hide sem with dissolve
    show worker at center with dissolve
    pause 0.8

    show worker point at center with dissolve
    $ _preferences.afm_enable = False
    show screen screen_gold_attestat_hotspot
    voice "audio/voice/worker/worker01.mp3"
    worker "Я чувствую твой потенциал... Ты достоин починить станок! Мы не можем из-за наших огромных пальцев починить его!"
    hide screen screen_gold_attestat_hotspot
    hide screen screen_info_stand
    $ _preferences.afm_enable = True

    show worker at center with dissolve
    voice "audio/voice/worker/worker02.mp3"
    worker "Нужно пересобрать этот станок."
    play music audio.ddlc_play fadeout 0.4 fadein 0.4 volume 0.24
    hide worker with dissolve

    # Вызов экрана мини-игры с шестерёнками станка
    call screen screen_mg_intro("РЕМОНТ СТАНКА", "Расставьте шестерни разных размеров на оси редуктора, чтобы запустить все три узла станка.")
    call screen screen_minigame_pipes

label after_mg_pipes:
    scene bg pgt_novii_koridor
    play music audio.ddlc_okay fadeout 0.5 fadein 0.5 volume 0.26 if_changed
    show worker at center with dissolve
    voice "audio/voice/worker/worker03.mp3"
    worker "Неплохо, этот станок проработает ещё 2000 лет."

    hide worker with dissolve

    show sem laugh at sem_center with dissolve

    voice "audio/voice/semen/semen32.mp3"
    sem "Слушай, механик из тебя отличный! Но теперь..."

    stop sound fadeout 1.0
    scene bg pgt_stairs_2
    with dissolve

    show sem default at sem_center with dissolve

    voice "audio/voice/semen/semen33.mp3"
    sem "Экскурсию я тебе провёл и в благородство играть не буду: соберёшь мне бутерброд — и мы в расчёте."
    show sem smirk with dissolve

    voice "audio/voice/gg/gg12.mp3"
    gg "А продукты где взять?"

    show sem whisper
    voice "audio/voice/semen/semen34.mp3"
    sem "У поваров, естественно! Только не попадись им, а то мало не покажется!"

    scene bg pgt_culinary_hall
    with dissolve
    play music audio.ddlc_panic fadeout 0.4 fadein 0.4 volume 0.24

    voice "audio/voice/gg/gg13.mp3"
    gg "Пора раздобыть пару ингредиентов для бутерброда!"

    # Вызов экрана мини-игры 6А: кража ингредиентов в реальном времени (со штрафами)
    call screen screen_mg_intro("КУЛИНАРНЫЙ ЦЕХ", "Соберите все продукты из списка, не попадаясь на глаза поварам, и вернитесь к двери.")
    call screen screen_minigame_kitchen

label after_mg_kitchen:
    scene bg pgt_culinary_hall
    play music audio.ddlc_dreams fadeout 0.4 fadein 0.4 volume 0.28 if_changed
    # Вызов экрана мини-игры 6Б: сборка бутера из украденного (с пенальти за промахи и порядок)
    $ mg_burger.setup(mg_kitchen.collected)
    call screen screen_mg_intro("СБОРКА БУТЕРБРОДА", "Выбирайте ингредиенты справа строго по рецепту и вовремя сбрасывайте их ровно на тарелку.")
    call screen screen_minigame_burger

label after_mg_burger:
    # --------------------------------------------------------------------------
    # СЦЕНА 7: ФИНАЛ, ПЕРЕДАЧА БУТЕРА И ПОДБОР ПРОФЕССИИ ПО ИТОГАМ ИГР
    # --------------------------------------------------------------------------
    scene bg pgt_finish
    with fade
    play music audio.ddlc_warm fadeout 0.8 fadein 0.8 volume 0.28

    show sem default at sem_center with dissolve

    if mg_burger.grade == "perfect":
        show sem thumbs
        voice "audio/voice/semen/semen35.mp3"
        sem "Хороший бутерброд получился, может, тебе стоит быть поваром? И, кстати, теперь мы в расчёте."
    elif mg_burger.grade == "good":
        show sem proud
        voice "audio/voice/semen/semen36.mp3"
        sem "Не идеальный, но получилось неплохо."
    else:
        show sem shrug
        voice "audio/voice/semen/semen37.mp3"
        sem "Ну-у, для перекуса пойдёт, спасибо."

    $ career_summary = compute_career_recommendation()
    $ recommended_spec_id = career_summary["best"]["spec_id"]
    $ selected_cat = career_summary["best"]["cat"]
    $ selected_specialty = recommended_spec_id

    show sem shrug
    voice "audio/voice/semen/semen38.mp3"
    sem "Ну что, скажи честно: разве на профориентации тебе такое бы показали?"
    show sem think
    voice "audio/voice/semen/semen40.mp3"
    sem "Я тут прикинул твои результаты..."
    show sem point
    voice "audio/voice/semen/semen41.mp3"
    sem "Слушай, тебе больше всего подходит направление «[career_summary['best']['label']]» — будешь крутым специалистом по квалификации «[career_summary['best']['prof_title']]»!"

    # Экран индивидуального профориентационного итога по результатам всех мини-игр
label after_mg_career:
    play music audio.ddlc_warm fadein 0.6 volume 0.28 if_changed
    $ career_summary = compute_career_recommendation()
    $ recommended_spec_id = career_summary["best"]["spec_id"]
    $ selected_cat = career_summary["best"]["cat"]
    $ selected_specialty = recommended_spec_id
    call screen screen_career_result

    voice "audio/voice/gg/gg15.mp3"
    gg "Кажется, я знаю, куда я буду поступать..."

    # --------------------------------------------------------------------------
    # СЦЕНА 8: ИНТЕРАКТИВНЫЙ БУКЛЕТ ВСЕХ 23 ПРОФЕССИЙ И СПЕЦИАЛЬНОСТЕЙ ПГТ
    # --------------------------------------------------------------------------

    # Интерактивный презентационный буклет специальностей (23 направления)
    call screen screen_pgt_presentation

    # Отдельное окно с контактными данными и официальными ссылками приёмной комиссии ПГТ
    call screen screen_pgt_contacts

    if renpy.variant("web"):
        $ renpy.full_restart()
    else:
        $ renpy.quit()
    return
