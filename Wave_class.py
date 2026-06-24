import numpy as np
from scipy import signal
from math import *
import pygame as py
from matplotlib import pyplot as plt

class Wave:
    def __init__(self, frequency, wav_type, amplitude, sample_rate=44100, attack=0, decay=0, sustain=0, release=0):
        self.frequency = frequency
        self.wav_type = wav_type
        self.max_amplitude = amplitude
        self.sample_rate = sample_rate
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.max_duration = 0
        self.frames = 0
        self.time_points = 0
        self.wav = 0
        self.phase = 0
        self.loop = 0
        self.attack_start = 0
        self.attack_end = self.attack
        self.decay_start = self.attack_end
        self.decay_end = self.attack_end + self.decay
        self.sustain_start = self.decay_end + self.sustain * self.loop
        self.sustain_end = self.sustain_start + self.sustain
        self.update_wav()

    def update_wav(self):
        if self.loop == 0:
            self.attack_time_points = np.linspace(self.attack_start, self.attack_end, int(self.attack*self.sample_rate), False)
            self.decay_time_points = np.linspace(self.decay_start, self.decay_end, int((self.decay_end-self.decay_start)*self.sample_rate), False)
            self.sustain_time_points = np.linspace(self.sustain_start, self.sustain_end, int((self.sustain_end-self.sustain_start)*self.sample_rate), False)
            self.time_points = np.linspace(0, self.attack+self.decay+self.sustain, int((self.attack+self.decay+self.sustain)*self.sample_rate), False)
        elif self.sustain > 0:
            self.sustain_start = self.decay_end + self.sustain * self.loop
            self.sustain_end = self.sustain_start + self.sustain
            self.sustain_time_points = np.linspace(self.sustain_start, self.sustain_end, int((self.sustain_end-self.sustain_start)*self.sample_rate), False)
            self.time_points = self.sustain_time_points
        else:
            self.time_points = self.time_points = np.linspace(self.loop, self.attack+self.decay+self.sustain + self.loop, int((self.attack+self.decay+self.sustain)*self.sample_rate), False)

        x = 2 * pi * self.frequency * self.time_points
        if self.wav_type == 'saw':
            self.wav = signal.sawtooth(x)
        elif self.wav_type == 'squ':
            self.wav = signal.square(x)
        elif self.wav_type == 'tri':
            self.wav = signal.sawtooth(x, width=self.max_amplitude)
        elif self.wav_type == 'sin':
            self.wav = np.sin(x)
        elif self.wav_type == 'tan':
            self.wav = np.tan(x)
        elif self.wav_type == 'revsaw':
            self.wav = signal.sawtooth(x)
            np.flip(self.wav)
        elif self.wav_type == 'thicsaw':
            self.wav = signal.sawtooth(x)
            waves = 1
            for i in range(0, 5, 1):
                self.wav += signal.sawtooth(x*(1+i/100))
                waves += 1
            self.wav /= waves
        elif self.wav_type == 'thicsqu':
            self.wav = signal.square(x)
            waves = 1
            for i in range(0, 5, 1):
                self.wav += signal.square(x*(1+i/100))
                waves += 1
            self.wav /= waves
        self.wav *= self.max_amplitude

        self.loop += 1
        

class Wave2:
    def __init__(self, frequency = 440, wave_form = 0, amplitude = 1, attack = 1, decay = 1, sustain = 0.8, spread = 0, sample_rate = 44100):
        self.frequency = frequency
        self.wave_form = wave_form
        self.amplitude = amplitude
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.spread = spread
        self.loop_duration = attack + decay
        self.sample_rate = sample_rate
        
    def update_play_wave(self):
        self.loop = 0
        if self.wave_form == 0:
            self.wave = lambda x: self.amplitude * np.sin(self.frequency * x)
        elif self.wave_form == 1:
            self.wave = lambda x: self.amplitude * np.tri(self.frequency * x)
        elif self.wave_form == 2:
            self.wave = lambda x: self.amplitude * signal.sawtooth(self.frequency * x)
        elif self.wave_form == 3:
            self.wave = lambda x: self.amplitude * np.tan(self.frequency * x)
        x1 = np.linspace(0, self.attack, self.attack * self.sample_rate, False)
        x2 = np.linspace(self.attack, self.attack + self.decay, self.decay * self.sample_rate, False)
        attack_wave = lambda x: ((0-1) / (0 - self.attack)) * x * self.wave(x)
        decay_wave = lambda x: self.wave(x) * (((self.sustain - 1) / self.decay) * (x - self.attack - self.decay) + self.sustain)
        self.play_wave = np.concatenate([attack_wave(x1), decay_wave(x2)])
    
    def update_loop_wave(self):
        sustain_wave = lambda x: self.sustain * self.wave(x)
        self.x = np.linspace(self.attack + self.decay + self.loop, self.attack + self.decay + self.loop + self.loop_duration, self.loop_duration * self.sample_rate, False)
        self.loop_wave = sustain_wave(self.x)
        self.loop += self.loop_duration




