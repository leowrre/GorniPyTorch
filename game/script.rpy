## ==============================================================================
## ГЛАВНЫЙ СЦЕНАРИЙ: ГОРНЫЙ ТЕХНИКУМ (ГБПОУ ПГТ ИМ. В.П. РОМАНОВА)
## ==============================================================================

# ------------------------------------------------------------------------------
# ФОНОВЫЕ ИЗОБРАЖЕНИЯ (РЕАЛЬНЫЕ ФОТО ПГТ + СТИЛИЗОВАННЫЕ ФОНЫ СПЕЦЛОКАЦИЙ)
# ------------------------------------------------------------------------------
image bg pgt_entrance = "images/bg/pgt_outside_2.png"                   # Вход и очищенный фасад главного корпуса ПГТ
image bg pgt_checkpoint = "images/bg/pgt_checkpoint.png"                # Проходная с турникетом и рамками
image bg pgt_hall_floor2 = "images/bg/pgt_inside.png"                   # Главный холл и арка к лестнице
image bg pgt_it_entrance = "images/bg/pgt_it_entrance.png"              # Стеклянный вход в мастерские ИКТ (2-й этаж)
image bg pgt_it_corridor = "images/bg/koridor_it.png"                   # Коридор ИТ-центра
image bg pgt_it_maki = "images/bg/maki.png"                             # Кабинет с iMac (Маки)
image bg pgt_it_center = "images/bg/sait_sloman.png"                    # Компьютерный центр (сломанный сайт)
image bg pgt_web_dev = "images/bg/veb_rozrabo.png"                      # Схема шаблонов веб-разработки на доске
image bg pgt_interactive_display = "images/bg/otovyi_ekran.png"         # Зал с интерактивным сенсорным дисплеем (готовый экран)
image bg pgt_hallway_3 = "images/bg/pgt_hallway_3.png"                  # Подъём по лестнице на 3-й этаж
image bg pgt_assembly_hall = "images/bg/actoviy.png"                    # Актовый зал
image bg pgt_corridor_long = "images/bg/pgt_corridor_long.png"          # Длинный коридор мастерских
image bg pgt_workshop_corridor = "images/bg/pgt_workshop_corridor.png"  # Коридор у двери мастерской «Электрослесарь подземный»
image bg pgt_workshop = "images/bg/pgt_welding_workshop.png"            # Сварочная мастерская (5-й корпус)
image bg pgt_blackout_room = Transform("images/bg/mep_main.png", matrixcolor=TintMatrix("#8cb8ff") * BrightnessMatrix(-0.62))
image bg pgt_mine_polygon = "images/bg/pgt_mine_polygon.png"            # Открытый вход на учебный подземный полигон
image bg pgt_mine_entry = Transform("images/bg/pgt_mine_entry.png", matrixcolor=ContrastMatrix(1.06) * BrightnessMatrix(0.05))
image bg pgt_mine_tunnel = Transform("images/bg/poligon.png", matrixcolor=ContrastMatrix(1.06) * BrightnessMatrix(0.05))
image bg pgt_mine_drill = Transform("images/bg/poligon.png", matrixcolor=ContrastMatrix(1.06) * BrightnessMatrix(0.05))
image bg pgt_mine_breakthrough = Transform("images/bg/poligon.png", matrixcolor=ContrastMatrix(1.06) * BrightnessMatrix(0.05))
image bg pgt_toilet_exit = "images/bg/koridor_vichust_center.png"       # Коридор вычислительного центра во 2-м корпусе
image bg pgt_stairs_2 = "images/bg/dver_povarov.png"                    # Дверь у поваров во 2-м корпусе
image bg pgt_culinary_hall = "images/bg/stolovaya.png"                  # Учебная лаборатория поварского дела
image bg pgt_finish = "images/bg/pgt_outside_2.png"                     # Финальный двор у входа (первое фото)

# Спрайты персонажей
image master = "images/chars/master.png"
image master_hand = "images/chars/master_hand.png"
image master_hand_fist = "images/chars/master_hand_fist.png"
image tesla = "images/chars/tesla.png"
image chef = "images/chars/chef.png"
image brig = "images/chars/dyayda_yura_shecter_svet.png"
image worker = "images/chars/Muzhik_So_stankom.png"
image worker point = "images/chars/Muzhik_so_stankom_ukazyvaet.png"

# Спрайты Семёна (Старшак — все эмоции с прозрачным фоном)
image sem default = Transform("images/chars/sem_default.png", ysize=960, fit="contain")
image sem hello   = Transform("images/chars/sem_hello.png",   ysize=985, fit="contain")
image sem explain = Transform("images/chars/sem_explain.png", ysize=980, fit="contain")
image sem proud   = Transform("images/chars/sem_proud.png",   ysize=980, fit="contain")
image sem smirk   = Transform("images/chars/sem_smirk.png",   ysize=965, fit="contain")
image sem shrug   = Transform("images/chars/sem_shrug.png",   ysize=970, fit="contain")
image sem epic    = Transform("images/chars/sem_epic.png",    ysize=1020, fit="contain")
image sem whisper = Transform("images/chars/sem_whisper.png", ysize=960, fit="contain")
image sem coat    = Transform("images/chars/sem_coat.png",    ysize=980, fit="contain")
image sem present = Transform("images/chars/sem_present.png", ysize=1000, fit="contain")
image sem laugh   = Transform("images/chars/sem_laugh.png",   ysize=970, fit="contain")
image sem thumbs  = Transform("images/chars/sem_thumbs.png",  ysize=980, fit="contain")
image sem point   = Transform("images/chars/sem_point.png",   ysize=970, fit="contain")
image sem think   = Transform("images/chars/sem_think.png",   ysize=970, fit="contain")
image sem shock   = Transform("images/chars/sem_shock.png",   ysize=965, fit="contain")

# ------------------------------------------------------------------------------
# ПЕРСОНАЖИ
# ------------------------------------------------------------------------------
define gg = Character("Школьник", color="#66ccff")
define sem = Character("Семён (Старшак)", image="sem", color="#a3e066")
define prep = Character("Преподаватель ИСП", color="#33ddcc")
define act = Character("Активист студсовета", color="#ff99cc")
define dima = Character("Дима (Студент-сварщик)", color="#ffcc66")
define master = Character("Мастер производственного обучения", color="#ff8844")
define tesla = Character("Никола Тесла", color="#00ffff")
define brig = Character("Бригадир дядя Юра", color="#ff5533")
define worker = Character("Мускулистый работяга", color="#ff7744")
define cook = Character("Шеф-повар", color="#ffaa55")

# Эффект яркой вспышки света при включении рубильника
define flash = Fade(0.1, 0.0, 0.4, color="#ffffff")

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
# СТАРТ ИГРЫ
# ------------------------------------------------------------------------------
label start:
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

    scene bg pgt_entrance
    with fade

    gg "Чёрт, я живу напротив техникума, но всё равно умудрился опоздать."
    gg "Там уже всё закончилось, и что делать?"

    show sem hello at sem_walk_in

    sem "Привет, ты чего стоишь перед дверьми, ждёшь кого-то?"

    gg "Я шёл на день открытых дверей... но не дошёл..."

    show sem proud
    sem "Забей на эти официальные мероприятия, из них ты техникум не поймёшь!"
    #show sem explain
    sem "Я тебе покажу техникум изнутри, ты это нигде не увидишь."

    # --------------------------------------------------------------------------
    # СЦЕНА 1: ТУРНИКЕТ (МИНИ-ИГРА 1)
    # --------------------------------------------------------------------------
    scene bg pgt_checkpoint
    with dissolve

    show sem explain at sem_right with dissolve

    show sem thumbs
    sem "Турникет — штука такая, капризная. Нужно нажать точно в момент, иначе ты никуда не зайдёшь."

    hide sem with dissolve

    # Вызов экрана мини-игры 1
    call screen screen_minigame_turnstile

    show sem thumbs at sem_center with dissolve

    sem "Красава! Первая пара уже, считай, сдана. Добро пожаловать в Прокопьевский горнотехнический техникум имени В.П. Романова!"

    # --------------------------------------------------------------------------
    # СЦЕНА 2: КОМПЬЮТЕРНЫЙ ЦЕНТР — СБОРКА САЙТА (МИНИ-ИГРА 2)
    # --------------------------------------------------------------------------
    scene bg pgt_it_entrance
    with fade

    show sem present at sem_right with dissolve

    sem "Первое, что видит человек на втором этаже, — это компьютерный центр!"

    scene bg pgt_it_corridor
    with dissolve

    show sem present at sem_right with dissolve

    sem "Там учатся все айтишники нашего техникума: разработчики сайтов, разработчики видеоигр, сисадмины."

    scene bg pgt_it_maki
    with dissolve

    show sem explain at sem_right with dissolve

    sem "Направлений целых шесть: всё — от веб-разработки до сетей и VR!"

    scene bg pgt_it_center
    with dissolve

    show sem shock at sem_left with dissolve

    sem "Видимо, на сайте слетело оформление. Кажется, я знаю, кто починит его."
    show sem point
    sem "Выдвигаю твою кандидатуру на роль спасителя, и даже не отговаривайся, это твоё боевое крещение!"

    gg "Но я сайты даже ни разу не делал!"

    show sem explain
    sem "У всех что-то всегда бывает в первый раз!"
    show sem thumbs
    sem "Только мигающие ретро-гифки и счётчики из двухтысячных не тащи — госконтроль такой дизайн не пропустит."

    scene bg pgt_web_dev
    with dissolve

    show sem explain at sem_left with dissolve

    sem "Нужно вставить шаблоны, чтобы всё было аккуратно, по красоте и по ГОСТам, понимаешь?"

    hide sem with dissolve

    # Вызов экрана мини-игры 2
    call screen screen_minigame_site

    scene bg pgt_interactive_display
    with dissolve

    prep "Фантастика! Сайт снова живой, и даже блоки какие надо — все на месте! Спасибо за помощь!"

    show sem proud at sem_right with dissolve

    sem "Не за что, я всегда готов помочь!"

    gg "Эй, вообще-то это я сайт собирал..."

    show sem smirk
    sem "Мы же одна команда, малой! Погнали выше, на третий этаж!"

    # --------------------------------------------------------------------------
    # СЦЕНА 3: АКТОВЫЙ ЗАЛ (МИНИ-ИГРА 3)
    # --------------------------------------------------------------------------
    scene bg pgt_hallway_3
    with fade

    show sem default at sem_center with dissolve

    sem "Пойдём на третий этаж, мы тут не только учимся, но и «культурно и творчески развиваемся»!"

    scene bg pgt_assembly_hall
    with dissolve

    act "Катастрофа! Через полчаса выступление для гостей Дня открытых дверей, а вокалиста для финальной репетиции нет!"

    act "Семён! Ты кого с собой привёл? Он петь умеет?"

    show sem epic at sem_left with dissolve

    sem "Конечно, умеет, в душе он Фредди Меркюри, Стивен Тайлер и Крис Корнелл в одном человеке."
    gg "Да я только в ду́ше подпеваю!.."

    hide sem with dissolve

    act "Отлично, держи микрофон, двигайся по сцене и лови сверху правильные строчки студенческого гимна ПГТ по телесуфлёру!"

    # Вызов экрана мини-игры 3
    call screen screen_minigame_vocal

    if mg_vocal.mistakes == 0:
        act "Браво! Ни единой заминки в тексте — стопроцентное попадание в гимн!"
        show sem thumbs at sem_center with dissolve
        sem "Это, конечно, хорошо, но пение всё равно не твоё."
    else:
        act "Браво! Пара оговорок была, но упустим — финал вытянул хорошо! Спасибо, выручил!"
        show sem whisper at sem_center with dissolve
        sem "Не, пение совершенно точно не твоё."

    # --------------------------------------------------------------------------
    # СЦЕНА 4: СВАРОЧНАЯ МАСТЕРСКАЯ И НИКОЛА ТЕСЛА (МИНИ-ИГРЫ 4А И 4Б)
    # --------------------------------------------------------------------------
    scene bg pgt_corridor_long
    with fade

    show sem present at sem_left with dissolve

    sem "Здесь у нас учатся будущие мастера своего дела: сварщики, слесари и шахтёры."

    scene bg pgt_workshop_corridor
    with dissolve

    dima "НО У МЕНЯ НИЧЕГО НЕ ПОЛУЧАЕТСЯ!"

    master "ДА Я ЩАС В КОРИДОРЕ НАЙДУ ЧЕЛОВЕКА, КОТОРЫЙ РАБОТАЕТ ЛУЧШЕ ТЕБЯ!"

    scene bg pgt_corridor_long
    with dissolve

    #show sem whisper at sem_left with dissolve

    sem "Уходим, уходим, ухо..."

    hide sem
    play sound "audio/stealth_spotted.wav"
    show master_hand at hand_grab_in
    with hpunch

    play sound "audio/burger_drop.wav"
    hide master_hand
    show master_hand_fist at hand_clench_fist
    with vpunch

    gg "Э-э-эй! Вы чего?!"

    play sound "audio/pc_slide.wav"
    show bg pgt_corridor_long at bg_yanked_to_door
    show master_hand_fist at hand_yank_out
    pause 0.28

    scene bg pgt_workshop
    with hpunch

    show master at center with dissolve

    master "Дима, этот шкет сейчас сварит шов лучше, чем твоё Аль Денте."
    master "Держи маску и держатель, малец. Провари на верстаке контрольный стальной шаблон «ПГТ» — строго по контуру букв, без обрывов дуги и прожогов."

    # Вызов экрана мини-игры сварки по шаблону ПГТ
    call screen screen_minigame_weld

    if mg_weld.get_grade() == "perfect":
        master "А ты неплох, малец, такой шов не у каждого работяги выходит. Учись, Дима!"
    elif mg_weld.get_grade() == "good":
        master "Для первого раза неплохо, малец, всё ещё лучше Диминых швов."
    else:
        master "Ну ты, конечно, наводил, малец, до Димы тебе, конечно, ещё далеко."

    scene bg pgt_workshop_corridor
    with dissolve

    if mg_weld.get_grade() == "perfect":
        show sem thumbs at sem_center with dissolve
        sem "Так хорошо даже Химик не варил!"
    elif mg_weld.get_grade() == "good":
        show sem default at sem_center with dissolve
        sem "Эти студенты по сравнению с тобой отчисления просят."
    else:
        show sem laugh at sem_center with dissolve
        sem "Ох, зря ты сварил."

    show sem point
    sem "А сейчас!.."

    play sound "audio/fnaf_powerdown.wav"
    scene bg pgt_blackout_tesla
    with vpunch

    play music "audio/toreador_musicbox.wav"

    tesla "Я-я тут немного... хе-хе... напакостничал с проводами... мне нужна ваша помощь, хе-хе."

    scene bg pgt_blackout_room
    show tesla at center
    with dissolve

    gg "Подождите, а меня что, ударит током?!"

    # Вызов экрана мини-игры с проводкой без пересечений
    call screen screen_minigame_wiring

    if mg_wiring.shocks == 0:
        tesla "Ни одного удара током, хе-хе... хорошо справились, ребятули, хе-хе."
    else:
        tesla "Всего [mg_wiring.shocks] раз ударило током. Если током ударило, значит, ток есть, хе-хе."

    stop music fadeout 0.3
    scene bg pgt_workshop_corridor
    with flash

    gg "Э-э-э, это что только что было?.."

    if mg_wiring.shocks > 0:
        show sem smirk at sem_center with dissolve
        sem "Э... лектрик?"

    # --------------------------------------------------------------------------
    # СЦЕНА 5: ШАХТНЫЙ ПОЛИГОН — ЗАВАЛЫ И КРЫСЫ (МИНИ-ИГРА 5)
    # --------------------------------------------------------------------------
    scene bg pgt_mine_polygon
    with fade

    show sem point at sem_right with dissolve

    sem "О, чекай — открытый полигон! Пока всё равно никого нет, так что можно и прогуляться."

    scene bg pgt_mine_entry
    with dissolve

    show sem present at sem_right with dissolve

    sem "Этот полигон — гордость техникума. Прикинь, насколько круто, когда ты учишься на шахтёра и у тебя прямо под техникумом шахта!"

    scene bg pgt_mine_tunnel
    with dissolve

    show sem explain at sem_left with dissolve
    show brig at sem_right with dissolve

    brig "Где твой инструмент, малёк?"

    show sem shock
    sem "Э-э-э... м-мы тут... это самое... ну да..."

    brig "Возьми, твой бур пронзит небеса, Семён!"
    sem "Ох, спина..."

    hide sem with dissolve
    show brig
    brig "А ты бери заряды."
    gg "Я что, теперь бомбовый чувак?!"

    brig "Бомбу кинь и беги, малёк."

    hide brig with dissolve

    # Вызов экрана мини-игры 5
    call screen screen_minigame_mine

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

    scene bg pgt_toilet_exit
    with dissolve

    gg "Погоди... мы что, вылезли во 2 корпусе?"

    show sem default at sem_center with dissolve

    sem "Ага, вот и сократили дорогу, кстати, да!.."

    hide sem with dissolve
    play music "audio/coffin_dance.wav"
    show worker at center with dissolve
    pause 0.8

    show worker point at center with dissolve
    worker "Я чувствую твой потенциал... Ты достоин починить станок! Мы не можем из-за наших мускулистых пальцев починить его!"

    show worker at center with dissolve
    worker "Нужно пересобрать этот станок."
    stop music fadeout 0.5
    hide worker with dissolve

    # Вызов экрана мини-игры с шестерёнками станка
    call screen screen_minigame_pipes

    show worker at center with dissolve
    worker "Неплохо, малец, этот станок проработает ещё 2000 лет."

    play sound "audio/coffin_dance.wav"
    hide worker with dissolve

    show sem laugh at sem_center with dissolve

    sem "Не, ну ты, конечно, механик станков, а теперь..."

    stop sound fadeout 1.0
    scene bg pgt_stairs_2
    with dissolve

    show sem coat at sem_center with dissolve

    sem "Экскурсию я тебе провёл и в благородство играть не буду: соберёшь мне бутер — и мы в расчёте."
    show sem smirk with dissolve

    gg "А продукты где взять?"

    show sem whisper
    sem "У поваров, конечно, ты только им не попадись, а то делов, конечно, тебе будет."

    scene bg pgt_culinary_hall
    with dissolve

    gg "Пора стащить тут парочку ингредиентов."

    # Вызов экрана мини-игры 6А: кража ингредиентов в реальном времени (со штрафами)
    call screen screen_minigame_kitchen

    # Вызов экрана мини-игры 6Б: сборка бутера из украденного (с пенальти за промахи и порядок)
    $ mg_burger.setup(mg_kitchen.collected)
    call screen screen_minigame_burger

    # --------------------------------------------------------------------------
    # СЦЕНА 7: ФИНАЛ, ПЕРЕДАЧА БУТЕРА И ПОДБОР ПРОФЕССИИ ПО ИТОГАМ ИГР
    # --------------------------------------------------------------------------
    scene bg pgt_finish
    with fade

    show sem default at sem_center with dissolve

    gg "Держи свой бутер."

    if mg_burger.grade == "perfect":
        show sem thumbs
        sem "Хороший бутерброд вышел, может, тебе стоит быть поваром? И, кстати, теперь мы в расчёте."
    elif mg_burger.grade == "good":
        show sem proud
        sem "Не идеальный, но получился неплохой."
    else:
        show sem shrug
        sem "Ну-у, для перекуса пойдёт, спасибо."

    $ career_summary = compute_career_recommendation()
    $ recommended_spec_id = career_summary["best"]["spec_id"]
    $ selected_cat = career_summary["best"]["cat"]
    $ selected_specialty = recommended_spec_id

    show sem shrug
    sem "Ну что, скажи честно: разве на профориентации тебе такое бы показали?"
    show sem explain
    sem "Сегодня прямо приключение: и сайт починили, и песню исполнили, и шов сварили, и в шахте побыли, и даже станок починили!"
    show sem think
    sem "Я тут прикинул твои результаты..."
    show sem point
    sem "Слушай, тебе больше всего подходит направление «[career_summary['best']['label']]» — будешь крутым спецом по квалификации «[career_summary['best']['prof_title']]»!"

    # Экран индивидуального профориентационного итога по результатам всех мини-игр
    call screen screen_career_result

    gg "Кажется, я знаю, куда я буду поступать..."

    # --------------------------------------------------------------------------
    # СЦЕНА 8: ИНТЕРАКТИВНЫЙ БУКЛЕТ ВСЕХ 23 ПРОФЕССИЙ И СПЕЦИАЛЬНОСТЕЙ ПГТ
    # --------------------------------------------------------------------------

    # Интерактивный презентационный буклет специальностей (23 направления)
    call screen screen_pgt_presentation

    return
