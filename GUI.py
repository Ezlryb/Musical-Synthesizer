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
        
    def hovered(self):
        self.screen.blit(self.hovered_img, self.location)
    
    def pressed(self):
        self.screen.blit(self.pressed_img, self.location)

    def released(self, pos):
        if self.rect.collidepoint(pos):
            self.screen.blit(self.hovered_img, self.location)
        else:
            self.screen.blit(self.normal_img, self.location)



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
        key_normal = py.image.load('Resources/White_Key_Normal.png')
        key_pressed = py.image.load('Resources/White_Key_Pressed.png')
        key_hovered = py.image.load('Resources/White_Key_Hovered.png')
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
                if event.key == py.K_1:
                    sound_1 = py.sndarray.make_sound(Wave(600,'squ',0.5,44100,1,1,1,1).wav.copy())
                    sound_1.play()
                if event.key == py.K_2:
                    sound_2 = py.sndarray.make_sound(Wave(650,'sin',0.5,44100,1,1,1,1).wav.copy())
                    sound_2.play()
            elif event.type == py.KEYUP:
                if event.key == py.K_1:
                    sound_1.stop()
                if event.key == py.K_2:
                    sound_2.stop()
            elif event.type == py.MOUSEBUTTONDOWN:
                for note in notes:
                    if note.rect.collidepoint(py.mouse.get_pos()):
                        sound_3 = py.sndarray.make_sound(Wave(note.base_frequency,'saw',0.5,44100,1,1,1,1).wav.copy())
                        sound_3.play()
                        note.pressed()
                        note_clicked = True
            elif event.type == py.MOUSEBUTTONUP:
                if note_clicked:
                    note.released(py.mouse.get_pos())
                    note_clicked = False 
                    sound_3.fadeout(50)
                
        py.display.flip()
    quit()