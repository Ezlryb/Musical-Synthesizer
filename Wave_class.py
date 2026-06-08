import numpy as np
from scipy import signal
from math import *
import pygame as py

class Wave:
    def __init__(self, frequency, wav_type, amplitude, sample_rate=44100, attack=0.1, decay=5, sustain=3, release=0.4):
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
        self.update_wav()

    def update_wav(self):

        self.max_duration = self.attack+self.decay+self.release
        self.frames = self.max_duration*self.sample_rate
        self.time_points = np.linspace(0, self.max_duration, self.frames, False)

        if self.wav_type == 'saw':
            self.wav = signal.sawtooth(2*pi*self.frequency*self.time_points)
        elif self.wav_type == 'squ':
            self.wav = signal.square(2*pi*self.frequency*self.time_points)
        elif self.wav_type == 'tri':
            self.wav = signal.sawtooth(2*pi*self.frequency*self.time_points, width=0.5)
        elif self.wav_type == 'sin':
            self.wav = np.sin(2*pi*self.frequency*self.time_points)
        elif self.wav_type == 'tan':
            self.wav = np.tan(2*pi*self.frequency*self.time_points)

        self.wav *= self.max_amplitude
        self.wav = np.asarray([32767*self.wav, 32767*self.wav]).T.astype(np.int16)

