from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pygame
import time
import random

app = Ursina()
window.color = color.clear
window.title = 'Ursina žaidimas'
window.fps_counter.enabled = True

BLOCK_SIZE = 0.5
sound_enabled = True

Sky(texture='sky_default')

ground = Entity(
    model='plane',
    texture='grass',
    texture_scale=(10, 10),
    collider='box',
    scale=(100, 1, 100),
    position=(0, 0, 0)
)

player = FirstPersonController()
player.gravity = 0.5
player.jump_height = 1
player.cursor.visible = True
player.position = (0, 1.2, -5)

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
    text="Užduotis:\nPastatyk bokštą iš šešių kaladėlių.\nPasirinkdamas šias spalvas:\nraudona, geltona, žalia",
    origin=(0, 0),
    position=(-0.54, -0.34),
    scale=1.05,
    color=color.black,
    font='assets/fonts/verdana.ttf',
    enabled=False
)

# Viršutinė pranešimų juosta – tokio pat dydžio kaip užduotis apačioje
top_message_container = Entity(
    parent=camera.ui,
    position=(-0.54, 0.30),
    enabled=False
)

frame_top_message_border = Entity(
    parent=top_message_container,
    model='quad',
    color=color.black,
    scale=(0.50, 0.28),  # toks pat kaip užduoties rėmelis
    position=(0, 0)
)

frame_top_message = Entity(
    parent=top_message_container,
    model='quad',
    color=color.white,
    scale=(0.48, 0.26),  # toks pat kaip užduoties fonas
    position=(0, 0)
)

text_top_message = Text(
    parent=top_message_container,
    text='',
    font='assets/fonts/verdana.ttf',
    color=color.black,
    origin=(0, 0),
    position=(0, 0),
    scale=1.0,  # sumažintas, kad telptų
    line_height=1.4,  # tarpų tarp eilučių patogumui

)

def parodyti_top_pranesima(tekstas, spalva=color.white):
    text_top_message.text = tekstas
    frame_top_message.color = spalva
    top_message_container.enabled = True
    invoke(lambda: setattr(top_message_container, 'enabled', False), delay=3)



place_sound = Audio('assets/sounds/drill_sound.wav', autoplay=False)
move_sound = Audio('assets/sounds/click.wav', autoplay=False)

sound_button = Button(
    text='Išjungti garsą',
    color=color.azure,
    text_color=color.black,
    position=Vec2(0.68, -0.45),
    scale=(0.22, 0.06),
    parent=camera.ui
)

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    sound_button.text = 'Išjungti garsą' if sound_enabled else 'Įjungti garsą'
    place_sound.volume = 1.0 if sound_enabled else 0
    move_sound.volume = 1.0 if sound_enabled else 0

sound_button.on_click = toggle_sound

def play_task_audio():
    if not sound_enabled:
        return
    pygame.mixer.init()
    pygame.mixer.music.load("assets/sounds/uzduotis.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

colors = [color.red, color.green, color.blue, color.orange, color.violet, color.magenta, color.yellow, color.brown]
color_buttons = []
start_x = -0.23
selected_index = 0
selected_color = colors[selected_index]
last_switch_time = 0
switch_delay = 0.2

for i, c in enumerate(colors):
    b = Button(
        color=c,
        scale=(0.05, 0.05),
        position=Vec2(start_x + i * 0.08, -0.45),
        parent=camera.ui,
        highlight_color=color.clear,
        pressed_color=color.clear
    )
    color_buttons.append(b)

selector_icon = Entity(
    model='quad',
    texture='assets/textures/crane.png',
    parent=camera.ui,
    scale=(0.06, 0.06),
    position=color_buttons[selected_index].position + Vec2(0, 0.06)
)

def select_color(c):
    global selected_color
    selected_color = c
    for btn in color_buttons:
        if btn.color == c:
            selector_icon.animate_position(btn.position + Vec2(0, 0.06), duration=0.1, curve=curve.in_out_sine)
            selector_icon.animate_rotation_z(10, duration=0.07)
            invoke(setattr, selector_icon, 'rotation_z', 0, delay=0.15)
            if sound_enabled:
                move_sound.play()
            break

placed_blocks = []
required_colors = [color.red, color.yellow, color.green]

def check_task():
    block_colors = [b.color for b in placed_blocks if hasattr(b, 'color') and b.color is not None]

    if len(placed_blocks) < 6:
        parodyti_top_pranesima(f"Per mažai kaladėlių ({len(placed_blocks)}). Reikia 6.", color.orange)
    elif len(placed_blocks) > 6:
        parodyti_top_pranesima(f"Per daug kaladėlių ({len(placed_blocks)}). Reikia 6.", color.orange)
    elif not all(c in block_colors for c in required_colors):
        parodyti_top_pranesima("Trūksta spalvų. Naudok: raudona, geltona, žalia.", color.red)
    else:
        parodyti_top_pranesima(random.choice(["Šaunu!", "Puiku!", "Jėga!"]), color.green)

    for block in placed_blocks:
        destroy(block)
    placed_blocks.clear()

check_button = Button(
    text='Tikrinti užduotį',
    color=color.lime,
    text_color=color.black,
    position=Vec2(0.68, -0.35),
    scale=(0.22, 0.06),
    parent=camera.ui,
    on_click=check_task
)

def snap_to_grid(pos):
    return Vec3(
        round(pos.x / BLOCK_SIZE) * BLOCK_SIZE,
        round(pos.y / BLOCK_SIZE) * BLOCK_SIZE,
        round(pos.z / BLOCK_SIZE) * BLOCK_SIZE
    )

def input(key):
    global sound_enabled, selected_index, selected_color, last_switch_time

    if key == 'u':
        text_task.enabled = True
        invoke(play_task_audio, delay=0.05)

    if key == 't':
        check_task()

    if key == 'up arrow':
        sound_enabled = True
        toggle_sound()

    if key == 'down arrow':
        sound_enabled = False
        toggle_sound()

    if key == 'left mouse down' or key == 'right mouse down':
        hit = raycast(camera.world_position, camera.forward, distance=5, ignore=(player,))
        if hit.hit:
            place_pos = snap_to_grid(hit.world_point + hit.normal * (BLOCK_SIZE / 2))

            if key == 'left mouse down':
                if not any(e.position == place_pos and e.model == 'cube' for e in scene.entities):
                    block = Entity(
                        model='cube',
                        position=place_pos,
                        scale=Vec3(BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        color=selected_color,
                        texture='white_cube',
                        collider='box'
                    )
                    placed_blocks.append(block)
                    if sound_enabled:
                        place_sound.play()

            elif key == 'right mouse down' and hit.entity != ground:
                if hit.entity in placed_blocks:
                    placed_blocks.remove(hit.entity)
                destroy(hit.entity)

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

app.run()
