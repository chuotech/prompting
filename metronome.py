import time
import sys
import simpleaudio
import keyboard
import threading

class Metronome:
    def __init__(self, bpm, time_signature): 
        self.bpm = bpm
        self.time_signature = time_signature
        self.playing = False
        self.accentedtick = simpleaudio.WaveObject.from_wave_file("sounds/accentedtick_1.wav")
        self.tick = simpleaudio.WaveObject.from_wave_file("sounds/tick.wav")
    def play_metronome(self):
        beat = 1
        # self.playing = True
        print("Started Metronome")
        while self.playing:
            interval = 60 / self.bpm
            if beat == 1:
                self.accentedtick.play() 
                print("On Beat")
            else:
                self.tick.play()
                print("Tick")
            time.sleep(interval)
            beat += 1
            if (beat > self.time_signature):
                beat = 1
        
    def start_metronome(self):
        if not self.playing:
            self.playing = True
            self.thread = threading.Thread(target=self.play_metronome, daemon = True)
            self.thread.start()
        # interval = 60 / self.bpm
        # beat = 1
        # self.playing = True
        # print("Started Metronome")
        # try:
        #     while self.playing:
        #         if beat == 1:
        #             self.accentedtick.play()
        #             print("On Beat")
        #         else:
        #             self.tick.play()
        #             print("Tick")
        #         time.sleep(interval)
        #         beat += 1
        #         if (beat > self.time_signature):
        #             beat = 1
        # except KeyboardInterrupt:
        #     self.stop_metronome
    def stop_metronome(self):
        if self.playing:
            self.playing = False
            if self.thread:
                self.thread.join(timeout=0.1)
            print("Stopped Metronome")

    def set_bpm(self): 
        if not self.playing:
            try:
                new_bpm = int(input("Set new BPM: "))
                self.bpm = new_bpm
                self.interval = 60 / self.bpm
                self.print_details()
            except ValueError:
                print("Invalid BPM. Please enter a number.")
    
    def set_time_signature(self):
        if not self.playing:
            try:
                new_time_signature = int(input("Set new Time Signature: "))
                self.time_signature = new_time_signature
                self.print_details()
            except ValueError:
                print("Invalid time signature. Please enter a number.")

    def print_details(self):
        print(f"BPM:  {self.bpm}")
        print(f"Time Signature:  {self.time_signature}") 

metronome = Metronome(bpm = 120, time_signature = 4)
metronome.print_details()
while(1): 
    if (keyboard.is_pressed('space')):
        metronome.start_metronome()
        time.sleep(0.3)
    if (keyboard.is_pressed('shift')):
        metronome.stop_metronome()
        time.sleep(0.3)
    if (keyboard.is_pressed("b")): 
        metronome.set_bpm()
        time.sleep(0.3) 
    if (keyboard.is_pressed("t")):
        metronome.set_time_signature()
        time.sleep(0.3)
    if (keyboard.is_pressed('esc')): 
        break
    time.sleep(0.3)
# metronome.print_details()
# metronome.start_metronome()

