from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pygame
import time

app = Ursina()
window.color = color.clear
window.title = 'Ursina žaidimas'
window.fps_counter.enabled = True

# ===================== Pagrindiniai nustatymai =====================
BLOCK_SIZE = 0.5
sound_enabled = True

# ===================== Aplinka =====================
Sky(texture='sky_default')

ground = Entity(
    model='plane',
    scale=(500, 1, 500),
    texture='grass',
    texture_scale=(10, 10),
    collider='box',
    position=(0, 0, 0)
)

player = FirstPersonController()
player.gravity = 0.5
player.jump_height = 1
player.cursor.visible = True
player.position = (0, 1.2, -5)

# ===================== Užduotis =====================
frame_border = Entity(
    parent=camera.ui,
    model='quad',
    color=color.black,
    scale=(0.50, 0.28),
    position=(-0.54, -0.34),
    roundness=0.1
)

frame_task = Entity(
    parent=camera.ui,
    model='quad',
    color=color.yellow,
    scale=(0.48, 0.26),
    position=(-0.54, -0.34),
    roundness=0.1
)


text_task = Text(
    text="Užduotis:\nPastatyk bokštą iš šešių kaladėlių.\n Pasirinkdamas šias spalvas:\nraudona, geltona, žalia",

    origin=(0, 0),
    position=(-0.54, -0.34),
    scale=1.05,
    color=color.black,
    font='assets/fonts/verdana.ttf',
    enabled=False
)

# ===================== Garsai =====================
place_sound = Audio('assets/sounds/drill_sound.wav', autoplay=False)
move_sound = Audio('assets/sounds/click.wav', autoplay=False)

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    sound_button.text = 'Išjungti garsą' if sound_enabled else 'Įjungti garsą'
    place_sound.volume = 1.0 if sound_enabled else 0
    move_sound.volume = 1.0 if sound_enabled else 0

def play_task_audio():
    if not sound_enabled:
        return
    pygame.mixer.init()
    pygame.mixer.music.load("assets/sounds/uzduotis.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

sound_button = Button(
    text='Išjungti garsą',
    color=color.azure,
    text_color=color.white,
    position=Vec2(0.68, -0.45),
    scale=(0.22, 0.06),
    parent=camera.ui,
    on_click=toggle_sound
)

# ===================== Spalvos =====================
colors = [color.red, color.green, color.blue, color.orange, color.violet, color.magenta, color.yellow, color.brown]
color_buttons = []
start_x = -0.23
selected_index = 0
selected_color = colors[selected_index]
last_switch_time = 0
switch_delay = 0.2

selector_icon = Entity(
    model='quad',
    texture='assets/textures/crane.png',
    parent=camera.ui,
    scale=(0.06, 0.06),
    position=Vec2(start_x, -0.395)
)

def select_color(c):
    global selected_color
    selected_color = c
    for i, btn in enumerate(color_buttons):
        if btn.color == c:
            selector_icon.position = btn.position + Vec2(0, 0.06)
            selector_icon.rotation_z = 10
            invoke(setattr, selector_icon, 'rotation_z', 0, delay=0.15)
            if sound_enabled:
                move_sound.play()
            break

for i, c in enumerate(colors):
    def make_callback(color_choice):
        return lambda: select_color(color_choice)
    b = Button(
        color=c,
        scale=(0.05, 0.05),
        position=Vec2(start_x + i * 0.08, -0.45),
        parent=camera.ui,
        on_click=make_callback(c),
        highlight_color=color.clear,
        pressed_color=color.clear
    )
    color_buttons.append(b)

# ===================== Padėties „snapinimas“ =====================
def snap_to_grid(pos):
    return Vec3(
        round(pos.x / BLOCK_SIZE) * BLOCK_SIZE,
        round(pos.y / BLOCK_SIZE) * BLOCK_SIZE,
        round(pos.z / BLOCK_SIZE) * BLOCK_SIZE
    )

# ===================== Valdymas =====================
def input(key):
    global sound_enabled

    if key == 'u':
        text_task.enabled = True
        invoke(play_task_audio, delay=0.05)

    if key == 'up arrow':
        sound_enabled = True
        sound_button.text = 'Išjungti garsą'
        place_sound.volume = 1.0
        move_sound.volume = 1.0

    if key == 'down arrow':
        sound_enabled = False
        sound_button.text = 'Įjungti garsą'
        place_sound.volume = 0
        move_sound.volume = 0

    if key in ('left mouse down', 'right mouse down'):
        hit = raycast(camera.world_position, camera.forward, distance=5, ignore=(player,))
        if hit.hit:
            place_pos = snap_to_grid(hit.world_point + hit.normal * (BLOCK_SIZE / 2))

            if key == 'left mouse down':
                if not any(e.position == place_pos and e.model == 'cube' for e in scene.entities):
                    Entity(
                        model='cube',
                        position=place_pos,
                        scale=Vec3(BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        color=selected_color,
                        texture='white_cube',
                        collider='box'
                    )
                    if sound_enabled:
                        place_sound.play()

            elif key == 'right mouse down' and hit.entity != ground:
                destroy(hit.entity)

# ===================== Spalvų perjungimas rodyklėmis =====================
def update():
    global selected_index, last_switch_time
    now = time.time()

    if held_keys['left arrow'] and now - last_switch_time > switch_delay:
        if selected_index > 0:
            selected_index -= 1
            select_color(colors[selected_index])
            last_switch_time = now

    if held_keys['right arrow'] and now - last_switch_time > switch_delay:
        if selected_index < len(colors) - 1:
            selected_index += 1
            select_color(colors[selected_index])
            last_switch_time = now

# ===================== Paleidimas =====================
app.run()
