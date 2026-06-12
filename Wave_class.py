import numpy as np
from scipy import signal
from math import *
import pygame as py

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
        self.loop = -1
        self.update_wav()

    def update_wav(self):
        self.loop += 1
        self.max_duration = self.attack+self.decay+self.release
        self.frames = self.max_duration*self.sample_rate
        self.phase = self.max_duration
        self.time_points = np.linspace(self.phase*self.loop, self.max_duration+self.phase*self.loop, self.frames, False)
        x = 2 * pi * self.frequency * self.time_points
        if self.wav_type == 'saw':
            self.wav = signal.sawtooth(x)
        elif self.wav_type == 'squ':
            self.wav = signal.square(x)
        elif self.wav_type == 'tri':
            self.wav = signal.sawtooth(x, width=self.max_amplitude)
        elif self.wav_type == 'sin':
            self.wav = np.cos(x)
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
        

