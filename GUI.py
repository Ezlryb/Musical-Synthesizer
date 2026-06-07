import pygame as py
from numpy import *
from Wave_class import *
from pathlib import *

class Note:
    def __init__(self, normal_img, hovered_img, pressed_img, location, screen, volume):
        self.screen = screen
        self.normal_img = normal_img
        self.hovered_img = hovered_img
        self.pressed_img = pressed_img
        self.base_frequency = 440
        self.rect = normal_img.get_rect()
        self.location = location
        self.rect.topleft = location
        self.state = 'normal'
        self.currect_img = normal_img
        self.volume = volume
        self.index = 0
        self.note = py.sndarray.make_sound(Wave(self.base_frequency,'sin',volume,44100,1,1,1,1).wav.copy())
        screen.blit(normal_img, location)

    def play_note(self):
        for i in range(5):
            if not py.mixer.Channel(self.index*5-i).get_busy():
                self.channel = py.mixer.Channel(self.index*5-i)
        self.note = py.sndarray.make_sound(Wave(self.base_frequency,'sin',self.volume,44100,1,1,1,1).wav.copy())
        self.channel.play(self.note)
        self.state = 'pressed'
        self.currect_img = self.pressed_img

    def release_note(self, mouse_pos):
        self.note.fadeout(20)
        self.state = 'normal'
        if self.rect.collidepoint(mouse_pos):
            self.currect_img = self.hovered_img
        else:
            self.currect_img = self.normal_img
    def draw(self):
        self.screen.blit(self.currect_img, self.location)


def mouse_note_check(w_notes, b_notes):
    global number_of_notes_playing
    mouse_pos = py.mouse.get_pos()
    over_w_key = False
    over_b_key = False
    key = ''
    for note in b_notes:
        if note.rect.collidepoint(mouse_pos):
            over_b_key = True
            key = note
        else:
            note.release_note(mouse_pos)
    if not over_b_key:
        for note in w_notes:
            if note.rect.collidepoint(mouse_pos):
                over_w_key = True
                key = note
            else:
                note.release_note((0, 0))
    if py.mouse.get_pressed()[0]:
        if over_b_key:
            if key.state == 'normal':
                key.play_note()
                for note in w_notes:
                    note.release_note((0, 0))
        elif over_w_key:
            if key.rect.collidepoint(mouse_pos) and key.state == 'normal':
                key.play_note()
            elif key.state == 'pressed' and not key.rect.collidepoint(mouse_pos):
                key.release_note(mouse_pos)
            for note in b_notes:
                note.release_note(mouse_pos)
    else:
        for note in w_notes+b_notes:
            note.release_note(mouse_pos)
    
    number_of_notes_playing = 0
    for i in range(len(notes_wb)):
        if py.mixer.Channel(i).get_busy():
            number_of_notes_playing += py.mixer.Channel(i).get_busy()
    if number_of_notes_playing == 0:
            number_of_notes_playing = 1
    for note in w_notes+b_notes:
        note.draw()
        note.note.set_volume(1-0.05*number_of_notes_playing)
    
def transpose(semitones):
    global TWELVE_TONE_EQUAL_TEMP_FREQUENCIES
    global x_note_id
    for i, note in enumerate(x_note_id.keys()):
        note.base_frequency = TWELVE_TONE_EQUAL_TEMP_FREQUENCIES[i+semitones]
        note.index = i+1

def change_master_volume(volume):
    for i, note in enumerate(x_note_id.keys()):
        note.volume = volume


def mouse_octave_key_check(event):
    global lowest_frequency
    global TWELVE_TONE_EQUAL_TEMP_FREQUENCIES
    global notes_wb
    if up_ocatave_key_rect.collidepoint(py.mouse.get_pos()):
        if py.mouse.get_pressed()[0]:
            screen.blit(up_octave_key_pressed, (40, 298))
            if lowest_frequency < len(TWELVE_TONE_EQUAL_TEMP_FREQUENCIES) - len(notes_wb) - 12 and event == py.MOUSEBUTTONDOWN:
                lowest_frequency += 12
                transpose(lowest_frequency)
        else:
            screen.blit(up_octave_key_hovered, (40, 298))
    else:
        screen.blit(up_octave_key_normal, (40, 298))
    if down_octave_key_rect.collidepoint(py.mouse.get_pos()):
        if py.mouse.get_pressed()[0]:
            screen.blit(down_octave_key_pressed, (40, 322))
            if lowest_frequency > 12 and event == py.MOUSEBUTTONDOWN:
                lowest_frequency -= 12
                transpose(lowest_frequency)
        else:
            screen.blit(down_octave_key_hovered, (40, 322))
    else:
        screen.blit(down_octave_key_normal, (40, 322))

def horizontal_slider_check(x1, x2, y, img, rect):
    if py.mouse.get_pressed()[0]:
        if rect.collidepoint(py.mouse.get_pos()):
            if x1 > py.mouse.get_pos()[0] - rect.width//2:
                x = x1
            elif py.mouse.get_pos()[0] - rect.width//2 > x2:
                x = x2 
            else:
                x = py.mouse.get_pos()[0] - rect.width//2
        else:
            x = rect.topleft[0]
    else:
        x = rect.topleft[0]
    screen.blit(img, (x, y))
    return x
 

if __name__ == "__main__":
    TWELVE_TONE_EQUAL_TEMP_FREQUENCIES = []
    KEYBOARD_X = 96
    KEYBOARD_Y = 303
    for i in range(149):
        TWELVE_TONE_EQUAL_TEMP_FREQUENCIES.append(440*2**((i-69)/12))
    number_of_notes_playing = 0
    master_volume = 0.5
    lowest_frequency = 40
    py.mixer.pre_init(44100, -16, 2, 2048)
    py.mixer.init()
    py.mixer.set_num_channels(1080)
    py.init()
    view = py.display.set_mode((640,416))
    screen = py.Surface((640,416))
    screen.fill('#02002c')
    py.display.set_caption('Synthesiser')
    running = True
    w_notes = []
    b_notes = []
    controls_base = py.image.load('Resources/controls_base.png')
    keyboard_base = py.image.load('Resources/Keyboard_Base.png')
    w_key_pressed = py.image.load('Resources/White_Key_Pressed.png')
    w_key_hovered = py.image.load('Resources/White_Key_Hovered.png')
    w_key_normal = py.image.load('Resources/White_Key_Normal.png')
    b_key_pressed = py.image.load('Resources/Black_Key_Pressed.png')
    b_key_hovered = py.image.load('Resources/Black_Key_Hovered.png')
    b_key_normal = py.image.load('Resources/Black_Key_Normal.png')
    up_octave_key_normal = py.image.load('Resources/up_octave_key_normal.png')
    up_octave_key_pressed = py.image.load('Resources/up_octave_key_pressed.png')
    up_octave_key_hovered = py.image.load('Resources/up_octave_key_hovered.png')
    down_octave_key_normal = py.image.load('Resources/down_octave_key_normal.png')
    down_octave_key_pressed = py.image.load('Resources/down_octave_key_pressed.png')
    down_octave_key_hovered = py.image.load('Resources/down_octave_key_hovered.png')
    volume_slider_interactable = py.image.load('Resources/slider_interactable.png')
    volume_slider_left_path = py.image.load('Resources/slider_path1.png')
    volume_slider_right_path = py.image.load('Resources/slider_path2.png')
    screen.blit(controls_base, (9, 6))
    screen.blit(keyboard_base, (20, 289))
    screen.blit(up_octave_key_normal, (40, 298))
    screen.blit(down_octave_key_normal, (40, 322))
    screen.blit(volume_slider_interactable, (584, 14))
    up_ocatave_key_rect = up_octave_key_normal.get_rect()
    up_ocatave_key_rect.topleft = (40, 298)
    down_octave_key_rect = down_octave_key_normal.get_rect()
    down_octave_key_rect.topleft = (40, 322)
    volume_slider_interactable_rect = volume_slider_interactable.get_rect()
    volume_slider_interactable_rect.topleft = (584, 14)
    for i in range(0, 21):
        note = Note(w_key_normal, w_key_hovered, w_key_pressed, (KEYBOARD_X+i*24, KEYBOARD_Y), screen, master_volume)
        w_notes.append(note)
    for j in range(3):
        for i in range (0, 2):
            note = Note(b_key_normal, b_key_hovered, b_key_pressed, (KEYBOARD_X+i*26+16+168*j, KEYBOARD_Y), screen, master_volume)
            b_notes.append(note)
        for i in range(0, 3):
            note = Note(b_key_normal, b_key_hovered, b_key_pressed, (KEYBOARD_X+i*26+87+168*j, KEYBOARD_Y), screen, master_volume)
            b_notes.append(note)
    notes = b_notes + w_notes
    notes_wb = w_notes + b_notes
    x_note_id = {}
    for note in notes_wb:
        x_note_id[note] = note.location[0]
    x_note_id = dict(sorted(x_note_id.items(), key=lambda x: x[1]))
    transpose(lowest_frequency)
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
                elif event.key == py.K_q:
                    notes[0].play_note()

            elif event.type == py.KEYUP:
                if event.key == py.K_q:
                    notes[0].release_note(py.mouse.get_pos())
                    
            elif event.type == py.MOUSEBUTTONDOWN or event.type == py.MOUSEBUTTONUP or event.type == py.MOUSEMOTION:
                screen.blit(controls_base, (9, 6))
                mouse_note_check(w_notes, b_notes)
                mouse_octave_key_check(event.type)
                x = horizontal_slider_check(530, 584, 14, volume_slider_interactable, volume_slider_interactable_rect)
                volume_slider_interactable_rect.topleft = (x, 14)
                change_master_volume((x-530)/54)
        view.blit(screen, (0, 0))
        py.display.update()
    quit()