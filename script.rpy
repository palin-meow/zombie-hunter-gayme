# ==========================================================
#  ZOMBIE SHOOTER - Ren'Py
#  Pick Leon or Ada -> pick an area -> shoot the zombies!
#  Images live in game/images
# ==========================================================

# ---------- Crosshair mouse ----------
define config.mouse = { "default" : [ ("images/crosshair.png", 32, 32) ] }

# ---------- Characters (story text) ----------
define h = Character("[hero_name]", color="#4da6ff")

# ---------- Game variables ----------
default hero = "leon"
default hero_name = "Leon"
default hero_img = "leon.png"
default dmg = 2                # damage per bullet
default mag_size = 8           # bullets per magazine
default hero_reserve = 40      # extra bullets
default reload_time = 1.5      # seconds

default area = "village"
default area_bg = "bg_village.png"
default zombie_hp = 2
default zombie_speed = 3
default zombie_total = 8
default spawn_gap = 1.6

default ammo = 8
default reserve = 40
default reload_left = 0.0
default player_hp = 5
default kills = 0
default spawned = 0
default spawn_cd = 1.0
default zombies = []
default message = ""

# ---------- Game logic ----------
init python:

    def setup_battle():
        global ammo, reserve, reload_left, player_hp, kills
        global spawned, spawn_cd, zombies, message
        ammo = mag_size
        reserve = hero_reserve
        reload_left = 0.0
        player_hp = 5
        kills = 0
        spawned = 0
        spawn_cd = 1.0
        zombies = []
        message = ""

    def fire(z=None):
        """Called when you click. If z is a zombie, it gets hit."""
        global ammo, kills, message
        if reload_left > 0:
            return
        if ammo <= 0:
            message = "Empty! Press R to reload"
            return
        ammo -= 1
        message = ""
        # renpy.sound.play("gunshot.ogg")   # <- add your own sound file here
        if z is not None and z in zombies:
            z["hp"] -= dmg
            if z["hp"] <= 0:
                zombies.remove(z)
                kills += 1

    def start_reload():
        global reload_left, message
        if reload_left > 0 or ammo >= mag_size or reserve <= 0:
            return
        reload_left = reload_time
        message = "Reloading..."

    def update_game():
        """Runs 20 times per second while shooting."""
        global reload_left, ammo, reserve, spawned, spawn_cd
        global player_hp, message
        dt = 0.05

        # finish reloading
        if reload_left > 0:
            reload_left -= dt
            if reload_left <= 0:
                reload_left = 0
                take = min(mag_size - ammo, reserve)
                ammo += take
                reserve -= take
                message = ""

        # spawn zombies
        spawn_cd -= dt
        if spawned < zombie_total and spawn_cd <= 0:
            zombies.append({
                "x": 1900,
                "y": renpy.random.randint(430, 640),
                "hp": zombie_hp,
                "speed": zombie_speed + renpy.random.random() * 1.5,
            })
            spawned += 1
            spawn_cd = spawn_gap

        # move zombies; they bite you if they reach you
        for z in list(zombies):
            z["x"] -= z["speed"]
            if z["x"] < 260:
                zombies.remove(z)
                player_hp -= 1

        # check end of battle
        if player_hp <= 0:
            return "lose"
        if spawned >= zombie_total and len(zombies) == 0:
            return "win"
        if ammo == 0 and reserve == 0 and reload_left == 0:
            return "noammo"
        return None

# ---------- Screens ----------
screen choose_character():
    add "bg_title.png"
    text "CHOOSE YOUR CHARACTER":
        size 70
        xalign 0.5
        ypos 50
        color "#ffffff"
        outlines [ (3, "#000000", 0, 0) ]

    hbox:
        xalign 0.5
        yalign 0.6
        spacing 250

        vbox:
            spacing 10
            imagebutton:
                idle im.Scale("leon.png", 300, 540)
                hover im.MatrixColor(im.Scale("leon.png", 300, 540), im.matrix.brightness(0.2))
                action Return("leon")
            textbutton "LEON" action Return("leon") xalign 0.5 text_size 50
            text "Strong gun, small magazine" xalign 0.5 size 28 color "#ffffff"

        vbox:
            spacing 10
            imagebutton:
                idle im.Scale("ada.png", 300, 540)
                hover im.MatrixColor(im.Scale("ada.png", 300, 540), im.matrix.brightness(0.2))
                action Return("ada")
            textbutton "ADA" action Return("ada") xalign 0.5 text_size 50
            text "Fast reload, big magazine" xalign 0.5 size 28 color "#ffffff"

screen choose_area():
    add "bg_title.png"
    text "CHOOSE AN AREA":
        size 70
        xalign 0.5
        ypos 50
        color "#ffffff"
        outlines [ (3, "#000000", 0, 0) ]

    hbox:
        xalign 0.5
        yalign 0.55
        spacing 60

        vbox:
            spacing 10
            imagebutton:
                idle im.Scale("bg_village.png", 520, 292)
                hover im.MatrixColor(im.Scale("bg_village.png", 520, 292), im.matrix.brightness(0.2))
                action Return("village")
            textbutton "VILLAGE" action Return("village") xalign 0.5 text_size 46

        vbox:
            spacing 10
            imagebutton:
                idle im.Scale("bg_lab.png", 520, 292)
                hover im.MatrixColor(im.Scale("bg_lab.png", 520, 292), im.matrix.brightness(0.2))
                action Return("lab")
            textbutton "LAB" action Return("lab") xalign 0.5 text_size 46


        vbox:
            spacing 10
            imagebutton:
                idle im.Scale("bg_base.png", 520, 292)
                hover im.MatrixColor(im.Scale("bg_base.png", 520, 292), im.matrix.brightness(0.2))
                action Return("base")
            textbutton "MILITARY BASE" action Return("base") xalign 0.5 text_size 46

screen shooting():
    add area_bg
    add im.Scale(hero_img, 220, 396) xpos 40 ypos 520

    timer 0.05 repeat True action Function(update_game)
    key "r" action Function(start_reload)
    key "R" action Function(start_reload)

    # clicking empty space = a missed shot
    button:
        xysize (1920, 1080)
        action Function(fire)

    # zombies (click them to shoot)
    for z in zombies:
        imagebutton:
            idle im.Scale("zombie.png", 180, 324)
            xpos int(z["x"])
            ypos int(z["y"])
            action Function(fire, z)
        text "HP " + str(max(z["hp"], 0)):
            xpos int(z["x"]) + 60
            ypos int(z["y"]) - 30
            size 30
            color "#ff4444"
            outlines [ (2, "#000000", 0, 0) ]

    # HUD
    frame:
        xpos 20
        ypos 20
        background "#000000aa"
        padding (20, 12)
        vbox:
            spacing 4
            text "[hero_name]    Health: [player_hp]" size 36 color "#ffffff"
            text "Ammo: [ammo] / [mag_size]    Reserve: [reserve]" size 36 color "#ffd966"
            text "Zombies killed: [kills] / [zombie_total]" size 36 color "#ff8888"

    if message != "":
        text "[message]":
            xalign 0.5
            ypos 120
            size 50
            color "#ffffff"
            outlines [ (3, "#000000", 0, 0) ]

    textbutton "RELOAD (R)":
        xalign 0.98
        ypos 20
        text_size 40
        action Function(start_reload)

# ---------- The game ----------
label start:

    scene black
    call screen choose_character
    $ hero = _return

    if hero == "leon":
        $ hero_name = "Leon"
        $ hero_img = "leon.png"
        $ dmg = 2
        $ mag_size = 8
        $ hero_reserve = 40
        $ reload_time = 1.5
    else:
        $ hero_name = "Ada"
        $ hero_img = "ada.png"
        $ dmg = 1
        $ mag_size = 15
        $ hero_reserve = 60
        $ reload_time = 0.9

    call screen choose_area
    $ area = _return

    if area == "village":
        $ area_bg = "bg_village.png"
        $ zombie_hp = 2
        $ zombie_speed = 3
        $ zombie_total = 8
        $ spawn_gap = 1.8
    elif area == "lab":
        $ area_bg = "bg_lab.png"
        $ zombie_hp = 3
        $ zombie_speed = 3.5
        $ zombie_total = 10
        $ spawn_gap = 1.5
    else:
        $ area_bg = "bg_base.png"
        $ zombie_hp = 4
        $ zombie_speed = 4
        $ zombie_total = 14
        $ spawn_gap = 1.2

    scene expression area_bg with fade

    if area == "village":
        h "The village is quiet... too quiet."
    elif area == "lab":
        h "The lab lights are flickering. Something escaped in here."
    else:
        h "The base fell hours ago. Stay sharp."

    h "I found a gun. Time to use it."
    "Click the zombies to shoot them. Press R to reload. Don't let them reach you!"

    $ setup_battle()
    call screen shooting
    $ result = _return

    scene expression area_bg

    if result == "win":
        h "That's the last of them. We survived!"
        "YOU WIN!"
    elif result == "noammo":
        h "I'm out of bullets... they're closing in."
        "GAME OVER - Out of ammo."
    else:
        h "They got me..."
        "GAME OVER - The zombies got you."

    menu:
        "Play again":
            jump start
        "Quit":
            return
