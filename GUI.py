import pygame as py
from numpy import *
from Wave_class import *
from pathlib import *
from matplotlib import pyplot as plt
import cProfile
import pstats


class ADSR_Slider:
    def __init__(self, interactable_area, x1, x2, y1, y2, slider_grip_img, x_track_boundaries, y_track_boundaries, track_imgs):
        self.interactable_area = interactable_area
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.interactable_area = interactable_area
        self.slider_grip_img = slider_grip_img
        self.currect_x = x2
        self.currect_y = y2
        self.track_imgs = track_imgs
        self.x_track_boundaries = x_track_boundaries
        self.y_track_boundaries = y_track_boundaries
        self.currect_track_img = track_imgs[0]
        self.is_interacted_with = False
        self.initial_mouse_pos = (0,0)
        self.track_check()


    def initial_click_check(self):
        if self.interactable_area.collidepoint(py.mouse.get_pos()):
            self.is_interacted_with = True
            self.initial_mouse_pos = py.mouse.get_pos()
            self.initial_slider_pos = (self.currect_x, self.currect_y)
        else:
            self.is_interacted_with = False

    def track_check(self):
        for i, n in enumerate(self.y_track_boundaries):
            if n >= self.currect_y:
                self.currect_track_img = self.track_imgs[i]
        for i, n in enumerate(self.x_track_boundaries):
            if n <= self.currect_x:
                self.currect_track_img = self.track_imgs[i]
        

    def move1(self):
        if self.is_interacted_with:
            adjusted_mouse_pos_x = py.mouse.get_pos()[0]
            adjusted_mouse_pos_y = py.mouse.get_pos()[1]
            if py.mouse.get_pressed()[0]:
                if self.x1 <= adjusted_mouse_pos_x <= self.x2:
                    new_x = adjusted_mouse_pos_x
                elif self.x1 > adjusted_mouse_pos_x:
                    new_x = self.x1
                else:
                    new_x = self.x2
            else:
                new_x = self.currect_x
            if py.mouse.get_pressed()[0]:
                if self.y1 <= adjusted_mouse_pos_y <= self.y2:
                    new_y = adjusted_mouse_pos_y
                elif self.y1 > adjusted_mouse_pos_y:
                    new_y = self.y1
                else:
                    new_y = self.currect_y
            else:
                new_y = self.currect_y
            self.currect_x = new_x
            self.currect_y = new_y
        self.track_check()
        return ((self.x1 - self.currect_x + 0.0001) / (self.x1 - self.x2 + 0.0001), (self.y2 - self.currect_y + 0.0001) / (self.y2 - self.y1 + 0.0001))
            
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
            self.track_check()
        return ((self.x1 - self.currect_x + 0.0001) / (self.x1 - self.x2 + 0.0001), (self.y2 - self.currect_y + 0.0001) / (self.y2 - self.y1 + 0.0001))
        
    def draw(self):
        global screen
        screen.blit(self.currect_track_img, (self.x1, self.y1))
        if self.slider_grip_img != None:
            screen.blit(self.slider_grip_img, (self.currect_x, self.currect_y))



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
        self.pressed_by = []
        self.current_img = normal_img
        self.volume = volume
        self.index = 0
        self.form = 'saw'
        self.wave = Wave3([1,1,1])
        self.wave.update_total_wave()
        screen.blit(normal_img, location)

    def play_note(self, pressed_by = 'keyboard'):
        global total_wave
        self.pressed_by.append(pressed_by)
        if self.state != 'pressed':
            self.wave.loop = 0
        self.wave.update_loop_wave('sustain')
        total_wave += self.wave.play_wave[0] + self.wave.play_wave[1] + self.wave.play_wave[2]
        self.state = 'pressed'
        self.current_img = self.pressed_img

    def release_note(self, released_by):
        global total_wave
        if released_by in self.pressed_by:
            self.pressed_by.remove(released_by)
            
    def draw(self):
        if self.current_img != self.normal_img:
            self.screen.blit(self.current_img, self.location)
        
    def loop_note(self):
        global total_wave
        if self.pressed_by == [] and self.state == 'pressed':
            self.state = 'releasing'
            if self.rect.collidepoint(py.mouse.get_pos()):
                self.current_img = self.hovered_img
            else:
                self.current_img = self.normal_img
        if self.state == 'pressed':
            self.wave.update_loop_wave('sustain')
            total_wave += self.wave.play_wave[0] + self.wave.play_wave[1] + self.wave.play_wave[2]
        if self.state == 'releasing':
            bool_list = self.wave.update_loop_wave('release')
            if False not in bool_list:
                self.state = 'normal'
            else:
                for i, is_released in enumerate(bool_list):
                    if not is_released: 
                        total_wave += self.wave.play_wave[i]


class Button:
    def __init__(self, interactable_area, normal_img, hovered_img, pressed_img, x, y, button_type, initial_state, initial_value = 0, step = 0, max_value = 0, min_value = 0):
        self.interactable_area = interactable_area
        self.normal_img = normal_img
        self.hovered_img = hovered_img
        self.pressed_img = pressed_img
        self.x = x
        self.y = y
        self.button_type = button_type
        self.state = initial_state
        self.current_img = normal_img
        self.value = initial_value
        self.step = step
        self.max_value = max_value
        self.min_value = min_value
    
    def check(self, event = None):
        if self.button_type == 'scale':
            global lowest_frequency
        if self.state != 'disabled':
            if self.interactable_area.collidepoint(py.mouse.get_pos()) and py.mouse.get_pressed()[0]:
                if self.button_type == 'toggle':
                    if self.state == 'normal':
                        self.state = 'pressed'
                    elif self.state == 'pressed':
                        self.state = 'normal'
                elif self.button_type == 'scale':
                    if event.type == py.MOUSEBUTTONDOWN:
                        if lowest_frequency + self.step <= self.max_value and lowest_frequency + self.step >= self.min_value:
                            lowest_frequency += self.step
                            self.state = 'pressed'
                        return True
                elif self.button_type == 'radio':
                        return True
        if self.button_type == 'scale' and not py.mouse.get_pressed()[0]:
            if lowest_frequency + self.step <= self.max_value and lowest_frequency + self.step >= self.min_value:
                self.state = 'normal'
            else:
                self.state = 'disabled'
        return False

    def draw(self):
        global screen
        if self.state == 'normal' and self.interactable_area.collidepoint(py.mouse.get_pos()):
            self.current_img = self.hovered_img
        elif self.state == 'normal' and not self.interactable_area.collidepoint(py.mouse.get_pos()):
            self.current_img = self.normal_img
        elif self.state == 'pressed' or self.state == 'disabled':
            self.current_img = self.pressed_img
        screen.blit(self.current_img, (self.x, self.y))


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
            note_over.play_note('mouse')
    else:
        if note_over != None and note_over.state != 'releasing':
            note_over.release_note('mouse')
    for note in last_notes_over:
        if note.state != 'releasing' and note != note_over:
            note.release_note('mouse')
    return note_over
        

def update_notes():
    for i, note in enumerate(x_note_id.keys()): 
        note.state = 'normal'
        for n in range(3):
            note.wave.attack[n] = (slider_values_lists[n][0] * 2) ** 2
            note.wave.decay[n] = (slider_values_lists[n][1] * 2) ** 2
            note.wave.sustain[n] = slider_values_lists[n][2] ** 2
            note.wave.release[n] = (slider_values_lists[n][3] * 2) ** 2
            note.wave.lushness[n] = 1 + int(round(10*knob_values_lists[n][4]))
            note.wave.spread[n] = (knob_values_lists[n][2] * 0.5) ** 3
            note.wave.frequency[n] = frequencies[i+lowest_frequency + int((knob_values_lists[n][3] - 0.5) * 12)]
            note.index = i+1
            note.wave.wave_form[n] = form[n]
            note.wave.amplitude[n] = volume * knob_values_lists[n][0]
            note.wave.update_total_wave()



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
    OSCCILATOR_SPACING = 75
    volume = 0.125
    form = [0, 0, 0]
    lowest_frequency = 48
    last_note_mouse_was_over = []
    py.mixer.pre_init(44100, -16, 2, 2048)
    py.mixer.init()
    py.mixer.set_num_channels(1)
    py.init()
    view = py.display.set_mode((640*SCREEN_SCALE,416*SCREEN_SCALE))
    screen = py.Surface((640*SCREEN_SCALE,416*SCREEN_SCALE))
    screen.fill('#02002c')
    py.display.set_caption('Synthesiser')
    total_wave = Wave3([0, 0, 0])
    total_wave.update_total_wave()
    total_wave.update_loop_wave('sustain')
    total_wave = total_wave.play_wave[0] + total_wave.play_wave[1] + total_wave.play_wave[2]
    mixed_wave = np.asarray([32767*total_wave, 32767*total_wave]).T.astype(np.int16)
    mixed_wave = py.sndarray.make_sound(mixed_wave.copy())
    frequencies = 27.5 * 2 ** (np.arange(176) / 12)
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
    up_octave_btn = Button(py.Rect(35*SCREEN_SCALE, 297*SCREEN_SCALE, 33*SCREEN_SCALE, 21*SCREEN_SCALE), up_octave_key_normal, up_octave_key_hovered, up_octave_key_pressed, 35*SCREEN_SCALE, 297*SCREEN_SCALE, 'scale', 'normal', 48, 12, len(frequencies) - 21 - 15, 0)
    down_octave_btn = Button(py.Rect(35*SCREEN_SCALE, 321*SCREEN_SCALE, 33*SCREEN_SCALE, 21*SCREEN_SCALE), down_octave_key_normal, down_octave_key_hovered, down_octave_key_pressed, 35*SCREEN_SCALE, 321*SCREEN_SCALE, 'scale', 'normal', 48, -12, len(frequencies) - 21 -15, 0)
    wave_form_button_imgs = [
    [set_up_img('Resources/wave_form_buttons/sin1.png'),
    set_up_img('Resources/wave_form_buttons/sin2.png'),
    set_up_img('Resources/wave_form_buttons/sin3.png')],
    [set_up_img('Resources/wave_form_buttons/tri1.png'),
    set_up_img('Resources/wave_form_buttons/tri2.png'),
    set_up_img('Resources/wave_form_buttons/tri3.png')],
    [set_up_img('Resources/wave_form_buttons/squ1.png'),
    set_up_img('Resources/wave_form_buttons/squ2.png'),
    set_up_img('Resources/wave_form_buttons/squ3.png')],
    [set_up_img('Resources/wave_form_buttons/saw1.png'),
    set_up_img('Resources/wave_form_buttons/saw2.png'),
    set_up_img('Resources/wave_form_buttons/saw3.png')]]
    adjustment_knob_imgs = []
    for i in range(1, 14):
        adjustment_knob_imgs.append(set_up_img(f'Resources/adjustment_knobs/adjustment_knob{i}.png'))
    adjustment_knobs_lists = []
    for n in range(3):
        adjustment_knobs = []
        count = 0
        for i in range(3):
            for j in range(2):
                adjustment_knobs.append(ADSR_Slider(py.Rect((121+i*24)*SCREEN_SCALE, (204+j*25-n*OSCCILATOR_SPACING)*SCREEN_SCALE, 18*SCREEN_SCALE, 18*SCREEN_SCALE), (123+i*24)*SCREEN_SCALE, (123+i*24)*SCREEN_SCALE, (206+j*25-n*OSCCILATOR_SPACING)*SCREEN_SCALE, (232+j*25-n*OSCCILATOR_SPACING)*SCREEN_SCALE, None, [], range(int((232+j*25-n*OSCCILATOR_SPACING)*SCREEN_SCALE), int((206+j*25-n*OSCCILATOR_SPACING)*SCREEN_SCALE), int(-2*SCREEN_SCALE)), adjustment_knob_imgs))
                count += 1
        adjustment_knobs_lists.append(adjustment_knobs)
    osccilator_radio_buttons_lists = []
    for n in range(3):
        osccilator_radio_buttons = []
        count = 0
        for i in range(2):
            for j in range(2):
                osccilator_radio_buttons.append(Button(py.Rect((56+i*33)*SCREEN_SCALE, (208+21*j-n*OSCCILATOR_SPACING)*SCREEN_SCALE, 28*SCREEN_SCALE, 18*SCREEN_SCALE), wave_form_button_imgs[count][0], wave_form_button_imgs[count][1], wave_form_button_imgs[count][2], (57+i*32)*SCREEN_SCALE, (209+20*j-n*OSCCILATOR_SPACING)*SCREEN_SCALE, 'radio', 'normal', count, count))
                count += 1
        osccilator_radio_buttons[0].state = 'pressed'
        osccilator_radio_buttons_lists.append(osccilator_radio_buttons)
    volume_slider_interactable = set_up_img('Resources/slider_interactable.png')
    volume_slider_paths = []
    for i in range(1,9):
        volume_slider_paths.append(set_up_img(f'Resources/volume_slider_track{i}.png'))
    volume_slider = ADSR_Slider(py.Rect(500*SCREEN_SCALE, 10*SCREEN_SCALE, 94*SCREEN_SCALE, 15*SCREEN_SCALE), 528*SCREEN_SCALE, 584*SCREEN_SCALE, 14*SCREEN_SCALE, 14*SCREEN_SCALE, volume_slider_interactable, range(int(525*SCREEN_SCALE), int(590*SCREEN_SCALE), int(8*SCREEN_SCALE)), [], volume_slider_paths)
    asdr_slider_interactable = set_up_img('Resources/ADSR_slider_interactable.png')
    asdr_track1 = set_up_img('Resources/asdr_track1.png')
    asdr_track2 = set_up_img('Resources/asdr_track2.png')
    asdr_track3 = set_up_img('Resources/asdr_track3.png')
    osccilator_bases = set_up_img('Resources/osccilator_bases.png')
    SPACING = 22
    osccilator_asdr_sliders_lists = []
    for n in range(3):
        osccilator_asdr_sliders = []
        for i in range(4):
            osccilator_asdr_sliders.append(ADSR_Slider(py.Rect((215+SPACING*i)*SCREEN_SCALE, (205-n*OSCCILATOR_SPACING)*SCREEN_SCALE, 16*SCREEN_SCALE, 50*SCREEN_SCALE), (218+SPACING*i)*SCREEN_SCALE, (218+SPACING*i)*SCREEN_SCALE, (207-n*OSCCILATOR_SPACING)*SCREEN_SCALE, (232-n*OSCCILATOR_SPACING)*SCREEN_SCALE, asdr_slider_interactable, [], [(232-n*OSCCILATOR_SPACING)*SCREEN_SCALE, (222-n*OSCCILATOR_SPACING)*SCREEN_SCALE, (212-n*OSCCILATOR_SPACING)*SCREEN_SCALE], [asdr_track1, asdr_track2, asdr_track3]))
        osccilator_asdr_sliders_lists.append(osccilator_asdr_sliders)
    bases = py.Surface((640*SCREEN_SCALE,416*SCREEN_SCALE))
    bases.blit(controls_base, (9*SCREEN_SCALE, 6*SCREEN_SCALE))
    bases.blit(keyboard_base, (9*SCREEN_SCALE, 288*SCREEN_SCALE))
    bases.blit(osccilator_bases, (47*SCREEN_SCALE, 38*SCREEN_SCALE))
    screen.blit(bases, (0,0))
    n = 0
    for i in range(21):
        if n > len(w_key_hovered_imgs) - 1:
            n = 0
        note = Note(w_key_normal_imgs[n], w_key_hovered_imgs[n], w_key_pressed_imgs[n], ((KEYBOARD_X+i*WHITE_NOTE_SPACING)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, volume)
        w_notes.append(note)
        n += 1
    for j in range(3):
        for i in range (0, 2):
            note = Note(b_key_normal, b_key_hovered, b_key_pressed, ((KEYBOARD_X+i*BLACK_NOTE_SPACING+16+168*j)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, volume)
            b_notes.append(note)
        for i in range(0, 3):
            note = Note(b_key_normal, b_key_hovered, b_key_pressed, ((KEYBOARD_X+i*BLACK_NOTE_SPACING+87+168*j)*SCREEN_SCALE, KEYBOARD_Y*SCREEN_SCALE), screen, volume)
            b_notes.append(note)
    notes = b_notes + w_notes
    notes_wb = w_notes + b_notes
    for note in notes_wb:
        bases.blit(note.current_img, note.location)
    x_note_id = {}
    for note in notes_wb:
        x_note_id[note] = note.location[0]
    x_note_id = dict(sorted(x_note_id.items(), key=lambda x: x[1]))
    slider_values_lists = [[0.01, 0.01, 0.01, 0.01],
                    [0.01, 0.01, 0.01, 0.01],
                    [0.01, 0.01, 0.01, 0.01]]
    knob_values_lists = [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]
    update_notes()
    initial_mouse_pos = (0,0)
    profiler = cProfile.Profile()
    clock = py.time.Clock()
    while running:
        should_update_notes = False
        clock.tick(60)
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
                elif event.key == py.K_z:
                    w_notes[0].play_note('z')
                elif event.key == py.K_x:
                    w_notes[1].play_note('x')
                elif event.key == py.K_c:
                    w_notes[2].play_note('c')
                elif event.key == py.K_v:
                    w_notes[3].play_note('v')
                elif event.key == py.K_b:
                    w_notes[4].play_note('b')
                elif event.key == py.K_n:
                    w_notes[5].play_note('n')
                elif event.key == py.K_m:
                    w_notes[6].play_note('m')
                elif event.key == py.K_COMMA:
                    w_notes[7].play_note(',')
                elif event.key == py.K_s:
                    b_notes[0].play_note('s')
                elif event.key == py.K_d:
                    b_notes[1].play_note('d')
                elif event.key == py.K_g:
                    b_notes[2].play_note('g')
                elif event.key == py.K_h:
                    b_notes[3].play_note('h')
                elif event.key == py.K_j:
                    b_notes[4].play_note('j')
            elif event.type == py.KEYUP:
                if event.key == py.K_q:
                    pass
                    '''plt.plot(total_wave)
                    plt.show()'''
                elif event.key == py.K_p:
                    profiler.disable()
                    stats = pstats.Stats(profiler)
                    stats.sort_stats('cumtime')
                    stats.print_stats()
                elif event.key == py.K_z:
                    w_notes[0].release_note('z')
                elif event.key == py.K_x:
                    w_notes[1].release_note('x')
                elif event.key == py.K_c:
                    w_notes[2].release_note('c')
                elif event.key == py.K_v:
                    w_notes[3].release_note('v')
                elif event.key == py.K_b:
                    w_notes[4].release_note('b')
                elif event.key == py.K_n:
                    w_notes[5].release_note('n')
                elif event.key == py.K_m:
                    w_notes[6].release_note('m')
                elif event.key == py.K_COMMA:
                    w_notes[7].release_note(',')
                elif event.key == py.K_s:
                    b_notes[0].release_note('s')
                elif event.key == py.K_d:
                    b_notes[1].release_note('d')
                elif event.key == py.K_g:
                    b_notes[2].release_note('g')
                elif event.key == py.K_h:
                    b_notes[3].release_note('h')
                elif event.key == py.K_j:
                    b_notes[4].release_note('j')
            elif event.type == py.MOUSEBUTTONDOWN or event.type == py.MOUSEBUTTONUP or event.type == py.MOUSEMOTION:
                last_note_mouse_was_over.append(mouse_note_check(w_notes, b_notes, last_note_mouse_was_over))
                while None in last_note_mouse_was_over:
                    last_note_mouse_was_over.pop(last_note_mouse_was_over.index(None))
                up_octave_btn.check(event) 
                down_octave_btn.check(event)
                for i, osccilator_radio_buttons_sublist in enumerate(osccilator_radio_buttons_lists):
                    for button in osccilator_radio_buttons_sublist:
                        if event.type == py.MOUSEBUTTONDOWN:
                            if button.check():
                                for other in osccilator_radio_buttons_sublist:
                                    other.state = 'normal'
                                button.state = 'pressed'
                                form[i] = button.value
                volume = volume_slider.move1()
                volume = volume[0] / ((volume_slider.x2 - volume_slider.x1))
                knob_values_lists = []
                for adjustment_knobs_sublist in adjustment_knobs_lists:
                    knob_values = []
                    for knob in adjustment_knobs_sublist:
                        knob_values.append(knob.move2()[1])
                    knob_values_lists.append(knob_values)
                slider_values_lists = []
                for osccilator_asdr_sliders_sublist in osccilator_asdr_sliders_lists:
                    slider_values = []
                    for slider in osccilator_asdr_sliders_sublist:
                        slider_values.append(slider.move2()[1])
                    slider_values_lists.append(slider_values)
            if event.type == py.MOUSEBUTTONDOWN:
                initial_mouse_pos = py.mouse.get_pos()
                volume_slider.initial_click_check()
                for adjustment_knobs_sublist in adjustment_knobs_lists:
                    for knob in adjustment_knobs_sublist:
                        knob.initial_click_check()
                for osccilator_asdr_sliders_sublist in osccilator_asdr_sliders_lists:
                    for slider in osccilator_asdr_sliders_sublist:
                        slider.initial_click_check()
            if event.type == py.MOUSEBUTTONUP:
                volume_slider.is_interacted_with = False
                for adjustment_knobs_sublist in adjustment_knobs_lists:
                    for knob in adjustment_knobs_sublist:
                        knob.is_interacted_with = False
                for osccilator_asdr_sliders_sublist in osccilator_asdr_sliders_lists:
                    for slider in osccilator_asdr_sliders_sublist:
                        slider.is_interacted_with = False
                should_update_notes = True
            if count == 0:
                if should_update_notes:
                    update_notes()
                screen.blit(bases, (0,0))
                up_octave_btn.draw()
                down_octave_btn.draw()
                volume_slider.draw()
                for adjustment_knobs_sublist in adjustment_knobs_lists:
                    for knob in adjustment_knobs_sublist:
                        knob.draw()
                for osccilator_radio_buttons_sublist in osccilator_radio_buttons_lists:
                    for button in osccilator_radio_buttons_sublist:
                        button.draw()
                for osccilator_asdr_sliders_sublist in osccilator_asdr_sliders_lists:
                    for slider in osccilator_asdr_sliders_sublist:
                        slider.draw()
                for note in notes_wb:
                    note.draw()
                view.blit(screen, (0, 0))
                py.display.update()
                count += 1
        
        if not py.mixer.Channel(0).get_busy():
            total_wave[:] = 0
            for note in notes:
                note.loop_note()
            mixed_wave = total_wave
            if round(np.max(mixed_wave), 5) > 1.0:
                mixed_wave /= np.max(mixed_wave)
            mixed_wave = np.asarray([32767*mixed_wave, 32767*mixed_wave]).T.astype(np.int16)
            total_note = py.sndarray.make_sound(mixed_wave.copy())
            py.mixer.Channel(0).play(total_note)
        if py.mixer.Channel(0).get_queue() == None:
            total_wave[:] = 0
            for note in notes:
                note.loop_note()
            mixed_wave = total_wave
            if round(np.max(mixed_wave), 5) > 1.0:
                mixed_wave /= np.max(mixed_wave)
            mixed_wave = np.asarray([32767*mixed_wave, 32767*mixed_wave]).T.astype(np.int16)
            total_note = py.sndarray.make_sound(mixed_wave.copy())
            py.mixer.Channel(0).queue(total_note)
    profile.disable()
    profile.print_stats(sort='cumtime')
    quit()