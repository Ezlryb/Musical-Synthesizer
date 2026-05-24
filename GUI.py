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
        self.note = py.sndarray.make_sound(Wave(base_frequency,'squ',0.5,44100,1,1,1,1).wav.copy())

    def play_note(self):
        self.note = py.sndarray.make_sound(Wave(self.base_frequency,'squ',0.5,44100,1,1,1,1).wav.copy())
        self.note.play()
        self.state = 'pressed'
        self.screen.blit(self.pressed_img, self.location)

    def release_note(self, mouse_pos):
        self.note.fadeout(20)
        self.state = 'normal'
        if self.rect.collidepoint(mouse_pos):
            self.screen.blit(self.hovered_img, self.location)
        else:
            self.screen.blit(self.normal_img, self.location)

def mouse_note_check(notes):
    mouse_pos = py.mouse.get_pos()
    if py.mouse.get_pressed()[0]:
        for note in notes:
            if note.rect.collidepoint(mouse_pos) and note.state == 'normal':
                note.play_note()
            elif note.state == 'pressed' and not note.rect.collidepoint(mouse_pos):
                note.release_note(mouse_pos)
    else:
        for note in notes:
            note.release_note(mouse_pos)


if __name__ == "__main__":
    TWELVE_TONE_EQUAL_TEMP_FREQUENCIES = []
    KEYBOARD_X = 96
    KEYBOARD_Y = 303
    for i in range(149):
        TWELVE_TONE_EQUAL_TEMP_FREQUENCIES.append(440*2**((i-69)/12))
    py.init()
    py.mixer.init()
    screen = py.display.set_mode((640,416))
    py.display.set_caption('Synthesiser')
    running = True
    notes = []
    for i in range(1, 22):
        key_pressed = py.image.load('Resources/White_Key_Pressed.png')
        key_hovered = py.image.load('Resources/White_Key_Hovered.png')
        key_normal = py.image.load('Resources/White_Key_Normal.png')
        screen.blit(key_hovered, (KEYBOARD_X+i*24, KEYBOARD_Y))
        print(TWELVE_TONE_EQUAL_TEMP_FREQUENCIES[i+40])
        note = Note(key_normal, key_hovered, key_pressed, TWELVE_TONE_EQUAL_TEMP_FREQUENCIES[i+40], (KEYBOARD_X+i*24, KEYBOARD_Y), screen)
        notes.append(note)
        note_clicked = False 
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
            elif event.type == py.MOUSEBUTTONDOWN:
                mouse_note_check(notes)
            elif event.type == py.MOUSEBUTTONUP:
                mouse_note_check(notes)
            elif event.type == py.MOUSEMOTION:
                mouse_note_check(notes)       
        py.display.flip()
    quit()