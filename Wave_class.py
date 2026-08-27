import numpy as np
from scipy import signal
from math import *
import pygame as py
from matplotlib import pyplot as plt
import cProfile
import sys
profile = cProfile.Profile()   

class Wave3:
    def __init__(self, frequency = [440, 440, 440], wave_form = [0,0,0], amplitude = [1,1,1], attack = [0.5,0.5,0.5], decay = [3,3,3], sustain = [0.5,0.5,0.5], release = [1, 1, 1], spread = [0.0002, 0.0002, 0.0002], lushness = [1,1,1], loop_duration = 0.05, sample_rate = 44100):
        self.frequency = frequency
        self.wave_form = wave_form
        self.amplitude = amplitude
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.spread = spread
        self.lushness = lushness
        self.loop_duration = loop_duration
        self.sample_rate = sample_rate
        global profile 
        profile.disable()
        profile.enable()
        self.loop = 0
        self.time_when_released = 0
        
    def update_total_wave(self):
        x1 = []
        x2 = []
        self.x = []
        attack_form = []
        decay_form = []
        self.form = []
        for i in range(3):
            x1.append(np.linspace(0, self.attack[i], int(round(self.attack[i] * self.sample_rate)), False))
            x2.append(np.linspace(self.attack[i], self.attack[i] + self.decay[i], int(round(self.decay[i] * self.sample_rate)), False))
            self.x.append(np.concatenate([x1[i],x2[i]]))
            attack_form.append(lambda x: ((0-1) / (0 - self.attack[i])) * x)
            decay_form.append(lambda x: (((self.sustain[i] - 1) / self.decay[i]) * (x - self.attack[i] - self.decay[i]) + self.sustain[i]))
            self.form.append(np.concatenate([attack_form[i](x1[i]), decay_form[i](x2[i])]))

    def update_loop_wave(self, mode):
        self.play_wave = []
        self.play_form = []
        start = round(self.loop * self.sample_rate)
        end = start + round(self.loop_duration * self.sample_rate)
        time = self.loop + np.arange(self.loop_duration * self.sample_rate) / self.sample_rate
        if end - start < self.sample_rate * self.loop_duration:
            end += 1
        elif end - start > self.sample_rate * self.loop_duration:
            end -= 1
        for n in range(3):
            if mode == 'sustain':
                if end <= np.shape(self.x[n])[0]:
                    self.play_form.append(self.form[n][start:end])
                else:
                    self.play_form.append(self.sustain[n])
                self.time_when_released = self.loop
            elif mode == 'release':
                self.play_form.append(self.sustain[n] * (1 - np.clip((self.loop-self.time_when_released)/self.release[n], 0, 1)))
            self.play_wave.append(np.zeros(int(round(self.loop_duration*self.sample_rate))))

            
            for i in range(0, self.lushness[n], 1):
                if self.wave_form[n] == 0:
                    self.play_wave[n] += (1 / (i + 1)) * self.play_form[n] * self.amplitude[n] * np.sin(2 * np.pi * (self.frequency[n] * (1 + self.spread[n] * i / (self.lushness[n]))) * time)
                elif self.wave_form[n] == 1:
                    self.play_wave[n] += (1 / (i + 1)) * self.play_form[n] * self.amplitude[n] * signal.sawtooth(2 * np.pi * (self.frequency[n] * (1 + self.spread[n] * i / (self.lushness[n]))) * time, width=0.5)
                elif self.wave_form[n] == 2:
                    self.play_wave[n] += (1 / (i + 1)) * self.play_form[n] * self.amplitude[n] * signal.square(2 * np.pi * (self.frequency[n] * (1 + self.spread[n] * i / (self.lushness[n]))) * time)
                elif self.wave_form[n] == 3:
                    self.play_wave[n] += (1 / (i + 1)) * self.play_form[n] * self.amplitude[n] * signal.sawtooth(2 * np.pi * (self.frequency[n] * (1 + self.spread[n] * i / (self.lushness[n]))) * time)
            

        self.loop = round(self.loop + self.loop_duration, 8)
        return [self.loop >= self.time_when_released + self.release[0], self.loop >= self.time_when_released + self.release[1], self.loop >= self.time_when_released + self.release[2]]

