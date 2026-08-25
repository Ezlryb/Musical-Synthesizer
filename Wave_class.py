import numpy as np
from scipy import signal
from math import *
import pygame as py
from matplotlib import pyplot as plt
import cProfile
import sys
profile = cProfile.Profile()

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
    def __init__(self, frequency = 440, wave_form = 0, amplitude = 1, attack = 3, decay = 3, sustain = 0.5, release = 1.0, spread = 0, loop_duration = 0.1, sample_rate = 44100):
        self.frequency = frequency
        self.wave_form = wave_form
        self.amplitude = amplitude
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.spread = spread
        self.loop_duration = loop_duration
        self.sample_rate = sample_rate
        
    def update_total_wave(self):
        self.loop = 0
        self.time_when_released = 0
        if self.wave_form == 0:
            self.wave = lambda x: self.amplitude * np.sin(2 * np.pi * self.frequency * x)
        elif self.wave_form == 1:
            self.wave = lambda x: self.amplitude * signal.sawtooth(2 * np.pi * self.frequency * x, width=0.5)
        elif self.wave_form == 2:
            self.wave = lambda x: self.amplitude * signal.sawtooth(2 * np.pi * self.frequency * x)
        elif self.wave_form == 3:
            self.wave = lambda x: self.amplitude * signal.square(self.frequency * x)
        x1 = np.linspace(0, self.attack, int(self.attack * self.sample_rate), False)
        x2 = np.linspace(self.attack, self.attack + self.decay, int(self.decay * self.sample_rate), False)
        x3 = np.linspace(self.attack + self.decay + self.loop, self.attack + self.decay + self.loop + self.loop_duration, int(self.loop_duration * self.sample_rate), False)
        self.x = np.concatenate([x1,x2,x3])
        attack_wave = lambda x: ((0-1) / (0 - self.attack)) * x * self.wave(x)
        decay_wave = lambda x: self.wave(x) * (((self.sustain - 1) / self.decay) * (x - self.attack - self.decay) + self.sustain)
        self.sustain_wave = lambda x: self.sustain * self.wave(x)
        self.release_wave = lambda x, loop: self.wave(x) * ((-self.sustain / self.release) * (x - self.attack - self.decay - loop) + self.sustain)
        self.total_wave = np.concatenate([attack_wave(x1), decay_wave(x2), self.sustain_wave(x3)])
        if (int((self.loop + self.loop_duration) * self.sample_rate) - int(self.loop * self.sample_rate))/self.sample_rate < self.loop_duration:
            self.play_wave = self.total_wave[int(self.loop * self.sample_rate):int((self.loop + self.loop_duration) * self.sample_rate) + 1]
        elif (int((self.loop + self.loop_duration) * self.sample_rate) - int(self.loop * self.sample_rate))/self.sample_rate > self.loop_duration:
            self.play_wave = self.total_wave[int(self.loop * self.sample_rate):int((self.loop + self.loop_duration) * self.sample_rate) - 1]
        else:
            self.play_wave = self.total_wave[int(self.loop * self.sample_rate):int((self.loop + self.loop_duration) * self.sample_rate)]
        

    def update_loop_wave(self, mode):
        if mode == 'sustain':
            if (self.loop + self.loop_duration) * self.sample_rate <= np.shape(self.total_wave)[0]:
                if (int((self.loop + self.loop_duration) * self.sample_rate) - int(self.loop * self.sample_rate))/self.sample_rate < self.loop_duration:
                    self.play_wave = self.total_wave[int(self.loop * self.sample_rate):int((self.loop + self.loop_duration) * self.sample_rate) + 1]
                elif (int((self.loop + self.loop_duration) * self.sample_rate) - int(self.loop * self.sample_rate))/self.sample_rate > self.loop_duration:
                    self.play_wave = self.total_wave[int(self.loop * self.sample_rate):int((self.loop + self.loop_duration) * self.sample_rate) - 1]
                else:
                    self.play_wave = self.total_wave[int(self.loop * self.sample_rate):int((self.loop + self.loop_duration) * self.sample_rate)]
            else:
                x = np.linspace(self.attack + self.decay + self.loop, self.attack + self.decay + self.loop + self.loop_duration, int(self.loop_duration * self.sample_rate), False)
                self.play_wave = self.sustain_wave(x)
            self.time_when_released = self.loop
            
        elif mode == 'release':
            if self.loop < self.time_when_released + self.release:
                x = np.linspace(self.attack + self.decay + self.loop , self.attack + self.decay + self.loop + self.loop_duration, int(self.loop_duration * self.sample_rate), False)
                self.play_wave = self.release_wave(x, self.time_when_released)
            else:
                return False


        self.loop += self.loop_duration
        return True
    

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
        self.play_form = []
        self.play_wave = []
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

