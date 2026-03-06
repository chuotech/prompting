from music21 import *
import pretty_midi
import time
import pprint
import threading
import json
import math

class Melody:
    def __init__(self, midi_file, tempo = None):
        self.midi_file = midi_file
        self.tempo = tempo
        self.midi_stream = pretty_midi.PrettyMIDI(midi_file)
        self.midi_stream21 = converter.parse(midi_file)
        self.duration = 10
        self.key_signature = self.get_key_signature()
        self.scale_pitches = self.get_scale_pitches()
        self.notes = self.get_notes()
        self.intervals = self.get_interval_info()
    
    def get_key_signature(self):
        k = self.midi_stream21.analyze('key')
        return k.name
    
    def get_scale_pitches(self):
        k = self.midi_stream21.analyze('key')
        scale_obj = k.getScale()
        return [p.name for p in scale_obj.getPitches()]
    
    def get_notes(self):
        notes = []
        for instrument in self.midi_stream.instruments:
            for note in instrument.notes:
                if note.start > self.duration:
                    return notes
                elif note.end > self.duration:
                    notes.append({"pitch": note.pitch, "onset": round(note.start, 2), "offset": round(10, 2)})
                else:
                    notes.append({"pitch": note.pitch, "onset": round(note.start, 2), "offset": round(note.end, 2)})
        return notes
    
    def get_interval_info(self):
        interval_info = []
        for i in range(len(self.notes) - 1):
            pitch1 = self.notes[i]["pitch"]
            note1 = note.Note()
            note1.pitch.midi = pitch1
            pitch2 = self.notes[i+1]["pitch"]
            note2 = note.Note()
            note2.pitch.midi = pitch2
            inter = interval.Interval(noteStart=note1, noteEnd=note2)
            pitch_jump = self.notes[i+1]["pitch"] - self.notes[i]["pitch"]
            interval_name = inter.niceName
            dissonance = 0
            if note2.pitch.name in self.scale_pitches:
                dissonance = 0
            else:
                dissonance = 1
            if abs(pitch_jump) == 1 and (note1.pitch.name not in self.scale_pitches or note2.pitch.name not in self.scale_pitches):
                motion = "chromatic step"
            elif abs(inter.generic.directed) == 2:
                motion = "step"
            else:
                motion = "leap"
            interval_info.append({
                "interval": interval_name,
                "jump": pitch_jump,
                "motion": motion,
                "dissonant": dissonance
            })
        return interval_info


            
    def print_info(self):
        print(self.key_signature)
        pprint.pp(self.notes)
        pprint.pp(self.intervals)
    
    def to_dict(self):
        return {
            "midi_file": self.midi_file,
            "duration": self.duration,
            "key_signature": self.key_signature,
            "scale_pitches": self.scale_pitches,
            "notes": self.notes,
            "interval_info": self.intervals
        }
    
    def export_to_json(self, output_file="midi_analysis.json"):
        with open(output_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
start = time.time()
midi_path = "samples/vincent_type_beat.mid"
midi_stream = Melody(midi_path)
midi_stream.print_info()
midi_stream.export_to_json("melody.json")
end = time.time()
print(end - start)