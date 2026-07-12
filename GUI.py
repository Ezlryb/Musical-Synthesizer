import pygame as py
from numpy import *
from Wave_class import *
from pathlib import *
from matplotlib import pyplot as plt
import cProfile
import pstats


class ADSR_Slider:
    def __init__(self, interactable_area, x1, x2, y1, y2, slider_grip_img):
        self.interactable_area = interactable_area
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.interactable_area = interactable_area
        self.slider_grip_img = slider_grip_img
        self.currect_x = x2
        self.currect_y = y2
        self.is_interacted_with = False
        self.initial_mouse_pos = (0,0)
        

    def initial_click_check(self):
        self.slider_grip_rect = self.slider_grip_img.get_rect()
        if self.interactable_area.collidepoint(py.mouse.get_pos()):
            self.is_interacted_with = True
            self.initial_mouse_pos = py.mouse.get_pos()
            self.initial_slider_pos = (self.currect_x, self.currect_y)
        else:
            self.is_interacted_with = False

    def move1(self):
        if self.is_interacted_with:
            adjusted_mouse_pos_x = py.mouse.get_pos()[0] - self.slider_grip_rect.w/2
            adjusted_mouse_pos_y = py.mouse.get_pos()[1] - self.slider_grip_rect.h/2
            if adjusted_mouse_pos_x != self.initial_mouse_pos[0] and py.mouse.get_pressed()[0]:
                if self.x1 <= adjusted_mouse_pos_x and adjusted_mouse_pos_x <= self.x2:
                    new_x = adjusted_mouse_pos_x
                elif self.x1 >= py.mouse.get_pos()[0]:
                    new_x = self.x1
                else:
                    new_x = self.x2
            else:
                new_x = self.currect_x
            if adjusted_mouse_pos_y != self.initial_mouse_pos[1] and py.mouse.get_pressed()[0]:
                if self.y1 <= adjusted_mouse_pos_y and adjusted_mouse_pos_y <= self.y2:
                    new_y = adjusted_mouse_pos_y
                elif self.y1 >= py.mouse.get_pos()[1]:
                    new_y = self.y1
                else:
                    new_y = self.currect_y
            else:
                new_y = self.currect_y
            self.currect_x = new_x
            self.currect_y = new_y
        screen.blit(self.slider_grip_img, (self.currect_x, self.currect_y))
        if self.is_interacted_with:
            return (self.x2 - self.currect_x, self.y2 - self.currect_y)
            
    
    def move2(self):
        if self.is_interacted_with:
            grip_x = self.currect_x
            grip_y = self.currect_y
            if py.mouse.get_pos()[0] != self.initial_mouse_pos[0]:
                difference_x = self.initial_mouse_pos[0] - py.mouse.get_pos()[0]
                if self.x1 <= self.initial_slider_pos[0] - difference_x and self.initial_slider_pos[0] - difference_x <= self.x2:
                    new_x = self.initial_slider_pos[0] - difference_x
                elif self.x1 >= self.initial_slider_pos[0] - difference_x:
                    new_x = self.x1
                else:
                    new_x = self.x2
            else:
                new_x = grip_x
            if py.mouse.get_pos()[1] != self.initial_mouse_pos[1]:
                difference_y = self.initial_mouse_pos[1] - py.mouse.get_pos()[1]
                if self.y1 <= self.initial_slider_pos[1] - difference_y and self.initial_slider_pos[1] - difference_y <= self.y2:
                    new_y = self.initial_slider_pos[1] - difference_y
                elif self.y1 >= self.initial_slider_pos[1] - difference_y:
                    new_y = self.y1
                else:
                    new_y = self.y2
            else:
                new_y = grip_y
            self.currect_x = new_x
            self.currect_y = new_y
        screen.blit(self.slider_grip_img, (self.currect_x, self.currect_y))
        if self.is_interacted_with:
            return (self.x2 - self.currect_x, self.y2 - self.currect_y)
            


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
        if self.state != 'pressed':
            self.wave.loop = 0
        self.wave.update_loop_wave('sustain')
        total_wave += self.wave.play_wave
        self.state = 'pressed'
        self.currect_img = self.pressed_img
        print('pressed')

    def release_note(self, mouse_over):
        global total_wave
        if self.state == 'pressed':
            self.state = 'releasing'
        if mouse_over:
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
            else:
                total_wave += self.wave.play_wave  
                
def mouse_note_check(w_notes, b_notes, last_notes_over):
    mouse_pos = py.mouse.get_pos()
    note_over = None
    for note in w_notes:
        if note.rect.collidepoint(mouse_pos):
            note_over = note
    for note in b_notes:
        if note.rect.collidepoint(mouse_pos):
            note_over = note
    if py.mouse.get_pressed()[0]:
        if note_over != None and note_over.state != 'pressed':
            note_over.play_note()
    else:
        if note_over != None and note_over.state != 'releasing':
            note_over.release_note(True)
    for note in last_notes_over:
        if note.state != 'releasing' and note != note_over:
            note.release_note(False)
    return note_over
    
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
            screen.blit(up_octave_key_pressed, (35*SCREEN_SCALE, 297*SCREEN_SCALE))
            if lowest_frequency < len(frequencies) - len(notes_wb) - 12*SCREEN_SCALE and event == py.MOUSEBUTTONDOWN:
                lowest_frequency += 12
                transpose(lowest_frequency)
        else:
            screen.blit(up_octave_key_hovered, (35*SCREEN_SCALE, 297*SCREEN_SCALE))
    else:
        screen.blit(up_octave_key_normal, (35*SCREEN_SCALE, 297*SCREEN_SCALE))
    if down_octave_key_rect.collidepoint(py.mouse.get_pos()):
        if py.mouse.get_pressed()[0]:
            screen.blit(down_octave_key_pressed, (35*SCREEN_SCALE, 321*SCREEN_SCALE))
            if lowest_frequency > 12 and event == py.MOUSEBUTTONDOWN:
                lowest_frequency -= 12
                transpose(lowest_frequency)
        else:
            screen.blit(down_octave_key_hovered, (35*SCREEN_SCALE, 321*SCREEN_SCALE))
    else:
        screen.blit(down_octave_key_normal, (35*SCREEN_SCALE, 321*SCREEN_SCALE))

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

def set_up_img(path, x=0, y=0):
    global SCREEN_SCALE
    img = py.image.load(path)
    img = py.transform.scale(img, (img.get_width() * SCREEN_SCALE, img.get_height() * SCREEN_SCALE))
    return img

if __name__ == "__main__":
    SCREEN_SCALE = 2
    KEYBOARD_X = 96
    KEYBOARD_Y = 303
    WHITE_NOTE_SPACING = 24
    BLACK_NOTE_SPACING = 26
    master_volume = 0.5
    lowest_frequency = 40
    last_note_mouse_was_over = []
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
    w_key_pressed_imgs = []
    for i in range(1,8):
        w_key_pressed_imgs.append(py.transform.rotozoom(py.image.load(f'Resources/white_keys/white_key_pressed{i}.png'), 0, SCREEN_SCALE))
    w_key_normal_imgs = []
    for i in range(1,8):
        w_key_normal_imgs.append(py.transform.rotozoom(py.image.load(f'Resources/white_keys/white_key_normal{i}.png'), 0, SCREEN_SCALE))
    w_key_hovered_imgs = []
    for i in range(1,8):
        w_key_hovered_imgs.append(py.transform.rotozoom(py.image.load(f'Resources/white_keys/white_key_hovered{i}.png'), 0, SCREEN_SCALE))

    controls_base = set_up_img('Resources/controls_base.png')
    keyboard_base = set_up_img('Resources/Keyboard_Base.png')
    b_key_pressed = set_up_img('Resources/Black_Key_Pressed.png')
    b_key_hovered = set_up_img('Resources/Black_Key_Hovered.png')
    b_key_normal = set_up_img('Resources/Black_Key_Normal.png')
    up_octave_key_normal = set_up_img('Resources/up_octave_key_normal.png')
    up_octave_key_pressed = set_up_img('Resources/up_octave_key_pressed.png')
    up_octave_key_hovered = set_up_img('Resources/up_octave_key_hovered.png')
    down_octave_key_normal = set_up_img('Resources/down_octave_key_normal.png')
    down_octave_key_pressed = set_up_img('Resources/down_octave_key_pressed.png')
    down_octave_key_hovered = set_up_img('Resources/down_octave_key_hovered.png')
    volume_slider_interactable = set_up_img('Resources/slider_interactable.png')
    volume_slider_interactable.convert_alpha()
    volume_slider_left_path = set_up_img('Resources/slider_path1.png')
    volume_slider_right_path = set_up_img('Resources/slider_path2.png')
    asdr_slider_interactable_img = set_up_img('Resources/ADSR_slider_interactable.png')

    osccilator_one_asdr_sliders = []
    SPACING = 22
    for i in range(4):
        osccilator_one_asdr_sliders.append(ADSR_Slider(py.Rect((215+SPACING*i)*SCREEN_SCALE, 205*SCREEN_SCALE, 16*SCREEN_SCALE, 50*SCREEN_SCALE), (218+SPACING*i)*SCREEN_SCALE, (218+SPACING*i)*SCREEN_SCALE, 207*SCREEN_SCALE, 232*SCREEN_SCALE, asdr_slider_interactable_img))
    

    screen.blit(controls_base, (9*SCREEN_SCALE, 6*SCREEN_SCALE))
    screen.blit(keyboard_base, (9*SCREEN_SCALE, 288*SCREEN_SCALE))
    screen.blit(up_octave_key_normal, (35*SCREEN_SCALE, 297*SCREEN_SCALE))
    screen.blit(down_octave_key_normal, (35*SCREEN_SCALE, 321*SCREEN_SCALE))
    screen.blit(volume_slider_interactable, (584*SCREEN_SCALE, 14*SCREEN_SCALE))
    up_ocatave_key_rect = up_octave_key_normal.get_rect()
    up_ocatave_key_rect.topleft = (35*SCREEN_SCALE, 297*SCREEN_SCALE)
    down_octave_key_rect = down_octave_key_normal.get_rect()
    down_octave_key_rect.topleft = (35*SCREEN_SCALE, 321*SCREEN_SCALE)
    volume_slider_interactable_rect = volume_slider_interactable.get_rect()
    volume_slider_interactable_rect.topleft = (584*SCREEN_SCALE, 14*SCREEN_SCALE)
    n = 0
    for i in range(21):
        if n > len(w_key_hovered_imgs) - 1:
            n = 0
        note = Note(w_key_normal_imgs[n], w_key_hovered_imgs[n], w_key_pressed_imgs[n], ((KEYBOARD_X+i*WHITE_NOTE_SPACING)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, master_volume)
        w_notes.append(note)
        n += 1
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
    profiler = cProfile.Profile()
    clock = py.time.Clock()
    while running:
        clock.tick(30)
        count = 0
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
                elif event.key == py.K_p:
                    profiler.clear()
                    profiler.enable()
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
                elif event.key == py.K_p:
                    profiler.disable()
                    stats = pstats.Stats(profiler)
                    stats.sort_stats('cumtime')
                    stats.print_stats()
                elif event.key == py.K_z:
                    w_notes[0].release_note(False)
                elif event.key == py.K_x:
                    w_notes[1].release_note(False)
                elif event.key == py.K_c:
                    w_notes[2].release_note(False)
                elif event.key == py.K_v:
                    w_notes[3].release_note(False)
                elif event.key == py.K_b:
                    w_notes[4].release_note(False)
                elif event.key == py.K_n:
                    w_notes[5].release_note(False)
                elif event.key == py.K_m:
                    w_notes[6].release_note(False)
                elif event.key == py.K_COMMA:
                    w_notes[7].release_note(False)
                elif event.key == py.K_s:
                    b_notes[0].release_note(False)
                elif event.key == py.K_d:
                    b_notes[1].release_note(False)
                elif event.key == py.K_g:
                    b_notes[2].release_note(False)
                elif event.key == py.K_h:
                    b_notes[3].release_note(False)
                elif event.key == py.K_j:
                    b_notes[4].release_note(False)
            elif event.type == py.MOUSEBUTTONDOWN or event.type == py.MOUSEBUTTONUP or event.type == py.MOUSEMOTION:
                last_note_mouse_was_over.append(mouse_note_check(w_notes, b_notes, last_note_mouse_was_over))
                while None in last_note_mouse_was_over:
                    last_note_mouse_was_over.pop(last_note_mouse_was_over.index(None))
                screen.blit(controls_base, (9*SCREEN_SCALE, 6*SCREEN_SCALE))
                screen.blit(keyboard_base, (9*SCREEN_SCALE, 288*SCREEN_SCALE))
                for note in notes_wb:
                    note.draw()
                mouse_octave_key_check(event.type)
                x = horizontal_slider_check(530*SCREEN_SCALE, 584*SCREEN_SCALE, 14*SCREEN_SCALE, volume_slider_interactable, volume_slider_interactable_rect)
                volume_slider_interactable_rect.topleft = (x, 14*SCREEN_SCALE)
                for item in osccilator_one_asdr_sliders:
                    message = item.move2()
                    if message != None:
                        print(message)
            if event.type == py.MOUSEBUTTONDOWN:
                for item in osccilator_one_asdr_sliders:
                    item.initial_click_check()
            if event.type == py.MOUSEBUTTONUP:
                for item in osccilator_one_asdr_sliders:
                    item.is_interacted_with = False
                set_master_volume(((x-530*SCREEN_SCALE)/(54*SCREEN_SCALE))*0.5)
            if count == 0:
                view.blit(screen, (0, 0))
                py.display.update()
                count += 1

        if not py.mixer.Channel(0).get_busy():
            total_wave[:] = 0
            for note in notes:
                note.loop_note()
            mixed_wave = (master_volume * total_wave * 0.25)
            if round(np.max(total_wave), 5) > 1.0:
                mixed_wave /= np.max(total_wave)
            mixed_wave = np.asarray([32767*mixed_wave, 32767*mixed_wave]).T.astype(np.int16)
            total_note = py.sndarray.make_sound(mixed_wave.copy())
            py.mixer.Channel(0).play(total_note)
        if py.mixer.Channel(0).get_queue() == None:
            total_wave[:] = 0
            for note in notes:
                note.loop_note()
            mixed_wave = (master_volume * total_wave * 0.25)
            if round(np.max(total_wave), 5) > 1.0:
                mixed_wave /= np.max(total_wave)
            mixed_wave = np.asarray([32767*mixed_wave, 32767*mixed_wave]).T.astype(np.int16)
            total_note = py.sndarray.make_sound(mixed_wave.copy())
            py.mixer.Channel(0).queue(total_note)
    profile.disable()
    profile.print_stats(sort='cumtime')
    quit()