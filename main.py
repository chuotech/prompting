from music21 import *
import pretty_midi
import time
import pprint

class MIDI_Stream:
    def __init__(self, midi_file, tempo = None):
        self.midi_file = midi_file
        self.tempo = tempo
        self.midi_stream = pretty_midi.PrettyMIDI(midi_file)
        self.midi_stream21 = converter.parse(midi_file)
        self.duration = round(self.midi_stream.get_end_time())
        if (tempo == None):
            self.tempo = self.get_tempo()
        self.notes = self.get_notes()
        self.beats_total = int((self.tempo/60) * self.duration * 2)
        self.key_signature = []

    def get_notes(self):
        notes = []
        for instrument in self.midi_stream.instruments:
            for note in instrument.notes:
                notes.append({"pitch": note.pitch, "onset": round(note.start, 5), "offset": round(note.end, 5)})
        # pprint.pp(notes)
        return notes
    
    def get_tempo(self):
        tempo_changes = self.midi_stream.get_tempo_changes()
        if (len(tempo_changes[0])) > 0:
            tempo = tempo_changes[1][0]
            return tempo
        else:
            print("No tempo")
            return
        
    def print_info(self):
        print(self.duration)
        print(self.tempo)
        print(self.midi_stream21[meter.TimeSignature][0])
        k = self.midi_stream21.analyze('key')
        print(k.name)
        measure_stream = self.midi_stream21.makeMeasures()
        measure_stream.show('text')
        pprint.pp(self.notes)
        return

    def get_full_chord_list(self):
        quarter_length = 60 / self.tempo
        eigth_length = quarter_length / 2
        chord_list = []
        curr_chord = []
        # curr_highest = 0
        # curr_lowest = 100000
        curr_highest_pitch = 0
        curr_lowest_pitch = 100000
        curr_max_interval_length = eigth_length
        i = 0
        for interval in range(self.beats_total):
            # self.key_signature.append(pretty_midi.KeySignature())
            while i < len(self.notes) and (self.notes[i]["onset"] <= curr_max_interval_length):
                curr_chord.append(self.notes[i]["pitch"])
                if self.notes[i]["pitch"] >= curr_highest_pitch:
                    # curr_highest = self.notes[i]["onset"]
                    curr_highest_pitch = self.notes[i]["pitch"]
                if self.notes[i]["pitch"] <= curr_lowest_pitch:
                    # curr_lowest = self.notes[i]["onset"]
                    curr_lowest_pitch = self.notes[i]["pitch"]
                i += 1
            chord_list.append((chord.Chord(curr_chord).pitchedCommonName, str(interval + 1)))
            curr_max_interval_length += eigth_length
            # curr_highest = 0
            # curr_lowest = 100000
            if i < len(self.notes) and curr_max_interval_length >= self.notes[i]["onset"]:
                curr_chord = []
                curr_highest_pitch = 0
                curr_lowest_pitch = 100000
        pprint.pp(chord_list)
        return chord_list
        
start = time.time()
midi_path = "samples/sample1.mid"
midi_stream = MIDI_Stream(midi_path)
midi_stream.print_info()
chords = midi_stream.get_full_chord_list()
end = time.time()
print(end - start)