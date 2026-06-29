import pygame as py
from numpy import *
from Wave_class import *
from pathlib import *
from matplotlib import pyplot as plt


class ADSR_Slider:
    def __init__(self, interactable_area, x1, x2, y1, y2, slider_grip_img):
        self.interactable_area = interactable_area
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.slider_grip_img = slider_grip_img

    def initial_click_check(self):
        if self.slider_grip_img.collide_point(py.mouse.get_pos()):
            self.is_interacted_with = True
            self.initial_mouse_pos = py.mouse.get_pos()
        else:
            self.is_interacted_with = False

    def move1(self):
        if py.mouse.get_pos()[0] != self.initial_mouse_pos[0]:
            if self.x1 <= py.mouse.get_pos()[0] and py.mouse.get_pos()[0] <= self.x2:
                new_x = py.mouse.get_pos()[0]
            elif self.x1 >= py.mouse.get_pos()[0]:
                new_x = self.x1
            else:
                new_x = self.x2
        elif py.mouse.get_pos()[1] != self.initial_mouse_pos[1]:
            if self.y1 <= py.mouse.get_pos()[1] and py.mouse.get_pos()[1] <= self.y2:
                new_y = py.mouse.get_pos()[1]
            elif self.y1 >= py.mouse.get_pos()[1]:
                new_y = self.y1
            else:
                new_y = self.y2
        else:
            new_x = py.mouse.get_pos()[0]
            new_y = py.mouse.get_pos()[1]
        screen.blit(self.slider_grip_img, (new_x, new_y))
        return [new_x, new_y]
            
    
    def move2(self):
        grip_x = self.slider_grip_img.get_pos()[0]
        grip_y = self.slider_grip_img.get_pos()[1]
        if py.mouse.get_pos()[0] != self.initial_mouse_pos[0]:
            difference_x = self.initial_mouse_pos[0] - py.mouse.get_pos()[0]
            if self.x1 <= grip_x + difference_x and grip_x + difference_x <= self.x2:
                new_x = grip_x + difference_x
            elif self.x1 >= grip_x + difference_x:
                new_x = self.x1
            else:
                new_x = self.x2
        elif py.mouse.get_pos()[1] != self.initial_mouse_pos[1]:
            difference_y = self.initial_mouse_pos[1] - py.mouse.get_pos()[1]
            if self.y1 <= grip_y + difference_y and grip_y + difference_y <= self.y2:
                new_y = grip_y + difference_y
            elif self.y1 >= grip_y + difference_y:
                new_y = self.y1
            else:
                new_y = self.y2
        else:
            new_x = grip_x
            new_y = grip_y
        return [new_x, new_y]
            


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
        self.form = 'saw'
        self.wave = Wave3(440)
        self.wave.update_total_wave()
        screen.blit(normal_img, location)

    def play_note(self):
        global total_wave
        global number_of_notes_playing
        self.wave.update_loop_wave('sustain')
        total_wave += self.wave.play_wave
        number_of_notes_playing += 1
        self.state = 'pressed'
        self.currect_img = self.pressed_img

    def release_note(self, mouse_pos):
        global total_wave
        global number_of_notes_playing
        if self.state == 'pressed':
            number_of_notes_playing -= 1
            self.state = 'releasing'
        if self.rect.collidepoint(mouse_pos):
            self.currect_img = self.hovered_img
        else:
            self.currect_img = self.normal_img

    def draw(self):
        self.screen.blit(self.currect_img, self.location)
        
    def loop_note(self):
        global total_wave
        if self.state == 'pressed':
            self.wave.update_loop_wave('sustain')
            total_wave += self.wave.play_wave
        if self.state == 'releasing':
            if self.wave.update_loop_wave('release'):
                self.state = 'normal'
                self.wave.loop = 0
            else:
                total_wave += self.wave.play_wave  
                
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
                note.release_note((0, 0))
    if py.mouse.get_pressed()[0]:
        if over_b_key:
            if key.state == 'normal' or key.state == 'releasing':
                key.play_note()
                for note in w_notes:
                    note.release_note((0, 0))
        elif over_w_key:
            if key.rect.collidepoint(mouse_pos) and (key.state == 'normal' or key.state == 'releasing'):
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
    
def transpose(semitones):
    global frequencies
    global x_note_id
    for i, note in enumerate(x_note_id.keys()):
        note.wave.frequency = frequencies[i+semitones]
        note.index = i+1
        note.wave.update_total_wave()

def set_master_volume(volume):
    global x_note_id
    for note in x_note_id.keys():
        note.wave.amplitude = volume
        note.wave.update_total_wave()

def set_wave_form(form):
    for note in x_note_id.keys():
        note.wave.wave_form = form
        note.wave.update_total_wave()

def mouse_octave_key_check(event):
    global lowest_frequency
    global frequencies
    global notes_wb
    global SCREEN_SCALE
    if up_ocatave_key_rect.collidepoint(py.mouse.get_pos()):
        if py.mouse.get_pressed()[0]:
            screen.blit(up_octave_key_pressed, (40*SCREEN_SCALE, 298*SCREEN_SCALE))
            if lowest_frequency < len(frequencies) - len(notes_wb) - 12*SCREEN_SCALE and event == py.MOUSEBUTTONDOWN:
                lowest_frequency += 12
                transpose(lowest_frequency)
        else:
            screen.blit(up_octave_key_hovered, (40*SCREEN_SCALE, 298*SCREEN_SCALE))
    else:
        screen.blit(up_octave_key_normal, (40*SCREEN_SCALE, 298*SCREEN_SCALE))
    if down_octave_key_rect.collidepoint(py.mouse.get_pos()):
        if py.mouse.get_pressed()[0]:
            screen.blit(down_octave_key_pressed, (40*SCREEN_SCALE, 322*SCREEN_SCALE))
            if lowest_frequency > 12 and event == py.MOUSEBUTTONDOWN:
                lowest_frequency -= 12
                transpose(lowest_frequency)
        else:
            screen.blit(down_octave_key_hovered, (40*SCREEN_SCALE, 322*SCREEN_SCALE))
    else:
        screen.blit(down_octave_key_normal, (40*SCREEN_SCALE, 322*SCREEN_SCALE))

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
    SCREEN_SCALE = 2
    KEYBOARD_X = 96
    KEYBOARD_Y = 303
    WHITE_NOTE_SPACING = 24
    BLACK_NOTE_SPACING = 26
    number_of_notes_playing = 1
    master_volume = 0.5
    lowest_frequency = 40
    py.mixer.pre_init(44100, -16, 2, 2048)
    py.mixer.init()
    py.mixer.set_num_channels(1)
    py.init()
    view = py.display.set_mode((640*SCREEN_SCALE,416*SCREEN_SCALE))
    screen = py.Surface((640*SCREEN_SCALE,416*SCREEN_SCALE))
    screen.fill('#02002c')
    py.display.set_caption('Synthesiser')
    total_wave = Wave3(0)
    total_wave.update_total_wave()
    total_wave.update_loop_wave('sustain')
    total_wave = total_wave.play_wave
    mixed_wave = np.asarray([32767*total_wave, 32767*total_wave]).T.astype(np.int16)
    mixed_wave = py.sndarray.make_sound(mixed_wave.copy())
    frequencies = 27.5 * 2 ** (np.arange(88) / 12)
    running = True
    w_notes = []
    b_notes = []
    controls_base_img = py.image.load('Resources/controls_base.png')
    controls_base = py.transform.smoothscale(py.image.load('Resources/controls_base.png'), (controls_base_img.get_width() * SCREEN_SCALE, controls_base_img.get_height() * SCREEN_SCALE))
    keyboard_base = py.transform.rotozoom(py.image.load('Resources/Keyboard_Base.png'), 0, SCREEN_SCALE)
    w_key_pressed = py.transform.rotozoom(py.image.load('Resources/White_Key_Pressed.png'), 0, SCREEN_SCALE)
    w_key_hovered = py.transform.rotozoom(py.image.load('Resources/White_Key_Hovered.png'), 0, SCREEN_SCALE)
    w_key_normal = py.transform.rotozoom(py.image.load('Resources/White_Key_Normal.png'), 0, SCREEN_SCALE)
    b_key_pressed = py.transform.rotozoom(py.image.load('Resources/Black_Key_Pressed.png'), 0, SCREEN_SCALE)
    b_key_hovered = py.transform.rotozoom(py.image.load('Resources/Black_Key_Hovered.png'), 0, SCREEN_SCALE)
    b_key_normal = py.transform.rotozoom(py.image.load('Resources/Black_Key_Normal.png'), 0, SCREEN_SCALE)
    up_octave_key_normal = py.transform.rotozoom(py.image.load('Resources/up_octave_key_normal.png'), 0, SCREEN_SCALE)
    up_octave_key_pressed = py.transform.rotozoom(py.image.load('Resources/up_octave_key_pressed.png'), 0, SCREEN_SCALE)
    up_octave_key_hovered = py.transform.rotozoom(py.image.load('Resources/up_octave_key_hovered.png'), 0, SCREEN_SCALE)
    down_octave_key_normal = py.transform.rotozoom(py.image.load('Resources/down_octave_key_normal.png'), 0, SCREEN_SCALE)
    down_octave_key_pressed = py.transform.rotozoom(py.image.load('Resources/down_octave_key_pressed.png'), 0, SCREEN_SCALE)
    down_octave_key_hovered = py.transform.rotozoom(py.image.load('Resources/down_octave_key_hovered.png'), 0, SCREEN_SCALE)
    volume_slider_interactable = py.transform.rotozoom(py.image.load('Resources/slider_interactable.png'), 0, SCREEN_SCALE)
    volume_slider_interactable.convert_alpha()
    volume_slider_left_path = py.transform.rotozoom(py.image.load('Resources/slider_path1.png'), 0, SCREEN_SCALE)
    volume_slider_right_path = py.transform.rotozoom(py.image.load('Resources/slider_path2.png'), 0, SCREEN_SCALE)
    adsr_slider_interactable = py.transform.rotozoom(py.image.load('Resources/ADSR_slider_interactable.png'), 0, SCREEN_SCALE/4)
    attack_slider = ADSR_Slider(py.Rect(224, 205, 10, 40), 229, 229, 238, 211, adsr_slider_interactable)
    screen.blit(controls_base, (9*SCREEN_SCALE, 6*SCREEN_SCALE))
    screen.blit(keyboard_base, (20*SCREEN_SCALE, 289*SCREEN_SCALE))
    screen.blit(up_octave_key_normal, (40*SCREEN_SCALE, 298*SCREEN_SCALE))
    screen.blit(down_octave_key_normal, (40*SCREEN_SCALE, 322*SCREEN_SCALE))
    screen.blit(volume_slider_interactable, (584*SCREEN_SCALE, 14*SCREEN_SCALE))
    up_ocatave_key_rect = up_octave_key_normal.get_rect()
    up_ocatave_key_rect.topleft = (40*SCREEN_SCALE, 298*SCREEN_SCALE)
    down_octave_key_rect = down_octave_key_normal.get_rect()
    down_octave_key_rect.topleft = (40*SCREEN_SCALE, 322*SCREEN_SCALE)
    volume_slider_interactable_rect = volume_slider_interactable.get_rect()
    volume_slider_interactable_rect.topleft = (584*SCREEN_SCALE, 14*SCREEN_SCALE)
    
    for i in range(0, 21):
        note = Note(w_key_normal, w_key_hovered, w_key_pressed, ((KEYBOARD_X+i*WHITE_NOTE_SPACING)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, master_volume)
        w_notes.append(note)
    for j in range(3):
        for i in range (0, 2):
            note = Note(b_key_normal, b_key_hovered, b_key_pressed, ((KEYBOARD_X+i*BLACK_NOTE_SPACING+16+168*j)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, master_volume)
            b_notes.append(note)
        for i in range(0, 3):
            note = Note(b_key_normal, b_key_hovered, b_key_pressed, ((KEYBOARD_X+i*BLACK_NOTE_SPACING+87+168*j)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, master_volume)
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
                elif event.key == py.K_EQUALS:
                    if lowest_frequency + len(notes) < len(frequencies):
                        lowest_frequency += 1
                        transpose(lowest_frequency)
                elif event.key == py.K_MINUS:
                    if lowest_frequency > 1:
                        lowest_frequency -= 1
                        transpose(lowest_frequency)
                elif event.key == py.K_1:
                    set_wave_form(0)
                elif event.key == py.K_2:
                    set_wave_form(1)
                elif event.key == py.K_3:
                    set_wave_form(2)
                elif event.key == py.K_z:
                    w_notes[0].play_note()
                elif event.key == py.K_x:
                    w_notes[1].play_note()
                elif event.key == py.K_c:
                    w_notes[2].play_note()
                elif event.key == py.K_v:
                    w_notes[3].play_note()
                elif event.key == py.K_b:
                    w_notes[4].play_note()
                elif event.key == py.K_n:
                    w_notes[5].play_note()
                elif event.key == py.K_m:
                    w_notes[6].play_note()
                elif event.key == py.K_COMMA:
                    w_notes[7].play_note()
                elif event.key == py.K_s:
                    b_notes[0].play_note()
                elif event.key == py.K_d:
                    b_notes[1].play_note()
                elif event.key == py.K_g:
                    b_notes[2].play_note()
                elif event.key == py.K_h:
                    b_notes[3].play_note()
                elif event.key == py.K_j:
                    b_notes[4].play_note()

            elif event.type == py.KEYUP:
                if event.key == py.K_q:
                    plt.plot(mixed_wave)
                    plt.show()
                elif event.key == py.K_z:
                    w_notes[0].release_note(py.mouse.get_pos())
                elif event.key == py.K_x:
                    w_notes[1].release_note(py.mouse.get_pos())
                elif event.key == py.K_c:
                    w_notes[2].release_note(py.mouse.get_pos())
                elif event.key == py.K_v:
                    w_notes[3].release_note(py.mouse.get_pos())
                elif event.key == py.K_b:
                    w_notes[4].release_note(py.mouse.get_pos())
                elif event.key == py.K_n:
                    w_notes[5].release_note(py.mouse.get_pos())
                elif event.key == py.K_m:
                    w_notes[6].release_note(py.mouse.get_pos())
                elif event.key == py.K_COMMA:
                    w_notes[7].release_note(py.mouse.get_pos())
                elif event.key == py.K_s:
                    b_notes[0].release_note(py.mouse.get_pos())
                elif event.key == py.K_d:
                    b_notes[1].release_note(py.mouse.get_pos())
                elif event.key == py.K_g:
                    b_notes[2].release_note(py.mouse.get_pos())
                elif event.key == py.K_h:
                    b_notes[3].release_note(py.mouse.get_pos())
                elif event.key == py.K_j:
                    b_notes[4].release_note(py.mouse.get_pos()) 
            elif event.type == py.MOUSEBUTTONDOWN or event.type == py.MOUSEBUTTONUP or event.type == py.MOUSEMOTION:
                screen.blit(controls_base, (9*SCREEN_SCALE, 6*SCREEN_SCALE))
                mouse_note_check(w_notes, b_notes)
                mouse_octave_key_check(event.type)
                x = horizontal_slider_check(530*SCREEN_SCALE, 584*SCREEN_SCALE, 14*SCREEN_SCALE, volume_slider_interactable, volume_slider_interactable_rect)
                volume_slider_interactable_rect.topleft = (x, 14*SCREEN_SCALE)
                attack_slider.move1
                if event.type == py.MOUSEBUTTONUP:
                    set_master_volume(((x-530*SCREEN_SCALE)/(54*SCREEN_SCALE))*0.5)
                
                


        if not py.mixer.Channel(0).get_busy():
            total_wave[:] = 0
            for note in notes:
                note.loop_note()
            mixed_wave = (master_volume * total_wave)
            if round(np.max(total_wave), 5) >= 1.0:
                mixed_wave /= np.max(total_wave)
            mixed_wave = np.asarray([32767*mixed_wave, 32767*mixed_wave]).T.astype(np.int16)
            total_note = py.sndarray.make_sound(mixed_wave.copy())
            py.mixer.Channel(0).play(total_note)
        if py.mixer.Channel(0).get_queue() == None:
            total_wave[:] = 0
            for note in notes:
                note.loop_note()
            mixed_wave = (master_volume * total_wave)
            if round(np.max(total_wave), 5) >= 1.0:
                mixed_wave /= np.max(total_wave)
            mixed_wave = np.asarray([32767*mixed_wave, 32767*mixed_wave]).T.astype(np.int16)
            total_note = py.sndarray.make_sound(mixed_wave.copy())
            py.mixer.Channel(0).queue(total_note)
        view.blit(screen, (0, 0))
        py.display.update()
    quit()