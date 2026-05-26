import pygame as py
from numpy import *
from Wave_class import *
from pathlib import *

class Note:
    def __init__(self, normal_img, hovered_img, pressed_img, base_frequency, location, screen):
        self.screen = screen
        self.normal_img = normal_img
        self.hovered_img = hovered_img
        self.pressed_img = pressed_img
        self.base_frequency = base_frequency
        self.rect = normal_img.get_rect()
        self.location = location
        self.rect.topleft = location
        self.state = 'normal'
        self.currect_img = normal_img
        self.note = py.sndarray.make_sound(Wave(base_frequency,'sin',0.5,44100,1,1,1,1).wav.copy())
        screen.blit(normal_img, location)

    def play_note(self):
        self.note = py.sndarray.make_sound(Wave(self.base_frequency,'sin',0.5,44100,1,1,1,1).wav.copy())
        self.note.play()
        self.state = 'pressed'
        self.currect_img = self.pressed_img
    def release_note(self, mouse_pos):
        self.note.fadeout(1000)
        self.state = 'normal'
        if self.rect.collidepoint(mouse_pos):
            self.currect_img = self.hovered_img
        else:
            self.currect_img = self.normal_img
    def draw(self):
        self.screen.blit(self.currect_img, self.location)


def mouse_note_check(w_notes, b_notes):
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
                note.release_note(mouse_pos)

    if py.mouse.get_pressed()[0]:
        if over_b_key:
            if key.state == 'normal':
                key.play_note()

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

    for note in w_notes+b_notes:
        note.draw()




if __name__ == "__main__":
    TWELVE_TONE_EQUAL_TEMP_FREQUENCIES = []
    KEYBOARD_X = 96
    KEYBOARD_Y = 303
    for i in range(149):
        TWELVE_TONE_EQUAL_TEMP_FREQUENCIES.append(440*2**((i-69)/12))
    py.mixer.pre_init(44100, -16, 2, 2048)
    py.init()
    view = py.display.set_mode((640,416))
    screen = py.Surface((640,416))
    screen.fill('#02002c')
    py.display.set_caption('Synthesiser')
    running = True
    w_notes = []
    b_notes = []
    keyboard_base = py.image.load('Resources/Keyboard_Base.png')
    w_key_pressed = py.image.load('Resources/White_Key_Pressed.png')
    w_key_hovered = py.image.load('Resources/White_Key_Hovered.png')
    w_key_normal = py.image.load('Resources/White_Key_Normal.png')
    b_key_pressed = py.image.load('Resources/Black_Key_Pressed.png')
    b_key_hovered = py.image.load('Resources/Black_Key_Hovered.png')
    b_key_normal = py.image.load('Resources/Black_Key_Normal.png')
    screen.blit(keyboard_base, (20, 289))
    for i in range(0, 21):
        note = Note(w_key_normal, w_key_hovered, w_key_pressed, TWELVE_TONE_EQUAL_TEMP_FREQUENCIES[i+45], (KEYBOARD_X+i*24, KEYBOARD_Y), screen)
        w_notes.append(note)
    for i in range (0, 2):
        note = Note(b_key_normal, b_key_hovered, b_key_pressed, TWELVE_TONE_EQUAL_TEMP_FREQUENCIES[i+45], (KEYBOARD_X+i*26+15, KEYBOARD_Y), screen)
        b_notes.append(note)
    for i in range(0, 3):
        note = Note(b_key_normal, b_key_hovered, b_key_pressed, TWELVE_TONE_EQUAL_TEMP_FREQUENCIES[i+45], (KEYBOARD_X+i*26+85, KEYBOARD_Y), screen)
        b_notes.append(note)
    notes = b_notes + w_notes
    notes_wb = w_notes + b_notes
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
            elif event.type == py.MOUSEBUTTONDOWN:
                mouse_note_check(w_notes, b_notes)
            elif event.type == py.MOUSEBUTTONUP:
                mouse_note_check(w_notes, b_notes)
            elif event.type == py.MOUSEMOTION:
                mouse_note_check(w_notes, b_notes) 
        view.blit(screen, (0, 0))     
        py.display.update()
    quit()