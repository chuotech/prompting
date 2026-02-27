from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from music21 import *
import pretty_midi
import time
import pprint
import threading
import json
import math

class MIDI_Stream:
    def __init__(self, midi_file, tempo = None):
        self.midi_file = midi_file
        self.tempo = tempo
        self.midi_stream = pretty_midi.PrettyMIDI(midi_file)
        self.midi_stream21 = converter.parse(midi_file)
        # self.duration = round(self.midi_stream.get_end_time(), 2)
        if (tempo == None):
            self.tempo = self.get_tempo()
        self.duration = self.get_duration()
        self.notes = self.get_notes()
        self.beats_total = int((self.tempo/60) * self.duration * 2)
        self.key_signature = self.get_key_signature()
        self.major_minor = self.key_signature.split()[1]
        self.scale_pitches = self.get_scale_pitches()
        self.time_signature = self.get_time_signature()
        self.chord_list = self.get_full_chord_list()
        self.chord_list = self.enforce_repeating_progression()
        self.chord_prog = self.get_chord_prog()
        self.chords_rhythm = self.get_chords_with_rhythm()

    def get_notes(self):
        notes = []
        for instrument in self.midi_stream.instruments:
            for note in instrument.notes:
                notes.append({"pitch": note.pitch, "onset": round(note.start, 2), "offset": round(note.end, 2)})
        # pprint.pp(notes)
        return notes
    
    def get_duration(self):
        real_duration_seconds = self.midi_stream.get_end_time()
        seconds_per_beat = 60 / self.tempo
        total_beats = real_duration_seconds / seconds_per_beat
        time_sig = self.midi_stream21[meter.TimeSignature][0]
        beats_per_measure = time_sig.numerator
        measures = math.ceil(total_beats / beats_per_measure)
        rounded_beats = measures * beats_per_measure
        rounded_seconds = rounded_beats * seconds_per_beat
        return round(rounded_seconds, 3)
        
    def get_tempo(self):
        tempo_changes = self.midi_stream.get_tempo_changes()
        if (len(tempo_changes[0])) > 0:
            tempo = tempo_changes[1][0]
            return tempo
        else:
            print("No tempo")
            return
        
    def get_time_signature(self):
        time_signature = self.midi_stream21[meter.TimeSignature][0]
        return f"{time_signature.numerator}/{time_signature.denominator}"

    def print_info(self):
        print("Time Duration in Seconds:")
        print(self.duration)
        print("Tempo BPM:")
        print(self.tempo)
        print("Time Signature")
        print(self.time_signature)
        k = self.midi_stream21.analyze('key')
        print("Key Signature")
        print(k.name)
        measure_stream = self.midi_stream21.makeMeasures()
        print("Music21 Measure Data:")
        measure_stream.show('text')
        print("Individual Notes: (MIDI pitch, onset, offset)")
        pprint.pp(self.notes)
        print("Chord List (chord name/note, note length):")
        pprint.pp(self.chord_list)
        print("Chord Progression:")
        pprint.pp(self.chord_prog)
        print("Chord with Rhythm: (chord/name note, name of beat or duration of note)")
        pprint.pp(self.chords_rhythm)
        self.get_dissonance_intervals()
        return
    
    def get_chord_prog(self):
        seen = set()
        chord_prog = []

        for chord_data in self.chord_list:
            name = chord_data["name"]
            if name not in seen:
                seen.add(name)
                chord_prog.append(name)

        return chord_prog
    
    def get_chords_with_length(self):
        # full = self.get_full_chord_list()

        # if not full:
        #     return []

        # chords_with_length = []
        # current_chord = full[0][0]
        # count = 1

        # for name, _ in full[1:]:
        #     if name == current_chord:
        #         count += 1
        #     else:
        #         beats = count / 2  # 2 eighths = 1 beat
        #         chords_with_length.append((current_chord, beats))
        #         current_chord = name
        #         count = 1

        # beats = count / 2
        # chords_with_length.append((current_chord, beats))

        # return chords_with_length
        full = self.get_full_chord_list()

        if not full:
            return []

        return full

    def get_chords_with_rhythm(self):

        full = self.get_full_chord_list()

        if not full:
            return []

        chords_with_rhythm = []

        for chord_data in full:
            name = chord_data["name"]
            beats = chord_data["beats"]

            if beats == 4:
                rhythm = "whole note"
            elif beats == 3:
                rhythm = "dotted half note"
            elif beats == 2:
                rhythm = "half note"
            elif beats == 1.5:
                rhythm = "dotted quarter note"
            elif beats == 1:
                rhythm = "quarter note"
            elif beats == 0.5:
                rhythm = "eighth note"
            else:
                rhythm = f"{beats} beats"

            chords_with_rhythm.append({
                "name": name,
                "rhythm": rhythm
            })

        return chords_with_rhythm
    
    def get_key_signature(self):
        k = self.midi_stream21.analyze('key')
        return k.name

    def get_scale_pitches(self):
        k = self.midi_stream21.analyze('key')
        scale_obj = k.getScale()
        return [p.name for p in scale_obj.getPitches()]

    def print_prompt_low(self):
        print("Low prompt")
        print("Produce a song in " + str(self.key_signature) + " with a " + str(self.time_signature) + " time signature in " + str(self.tempo) + " bpm.\n" +
        "The chord progression is :")
        print(", ".join(self.get_chord_prog()))
        print("The song last 3 measures")
        return

    def print_prompt_mid(self):
        measure_stream = self.midi_stream21.makeMeasures()
        num_measures = len(measure_stream.getElementsByClass('Measure'))
        chords = self.get_chords_with_length()
        print("Middle prompt")
        print(
            "Produce a song in " + str(self.key_signature) +
            " with a " + str(self.time_signature) +
            " time signature at " + str(self.tempo) + " bpm.\n" +
            "The chord progression is:"
        )
        formatted = [f"{name} ({length} beats)" for name, length in chords]
        print(", ".join(formatted))
        print("The song last 3 measures")
        return

    def print_prompt_high(self):
        print("High prompt")

        formatted = [
            f"{name} ({rhythm})"
            for name, rhythm in self.get_chords_with_rhythm()
        ]

        print(
            f"Produce a song in {self.key_signature}, "
            f"{self.time_signature} time, at {self.tempo} BPM.\n"
            f"Chord progression: {', '.join(formatted)}."
        )

        print("The song lasts 3 measures")
        # print("High prompt")
        # formatted = [
        #     f"{name} ({self.format_rhythm(count)})"
        #     for name, count in self.get_chords_with_rhythm()
        # ]

        # print(
        #     f"Produce a song in {self.key_signature}, "
        #     f"{self.time_signature} time, at {self.tempo} BPM.\n"
        #     f"Chord progression: {', '.join(formatted)}."
        # )
        # print("The song last 3 measures")
        # return
    def get_dissonance_intervals(self):
        total_dissonance = 0
        for i in range(len(self.notes) - 1):
            note1 = note.Note(self.notes[i]["pitch"])
            note2 = note.Note(self.notes[i+1]["pitch"])
            if (not interval.Interval(note1, note2).isConsonant()):
                print(str(note1.name) + ", " + str(note2.name) + " are dissonant")
                total_dissonance += 1
        print("Total Dissonance: ")
        print(str(total_dissonance))
        return

    def quantize_notes(self, subdivision=0.25):
        quarter_length = 60 / self.tempo
        grid_seconds = quarter_length * subdivision

        quantized = []

        for n in self.notes:
            quant_onset = round(round(n["onset"] / grid_seconds) * grid_seconds, 4)
            quant_offset = round(round(n["offset"] / grid_seconds) * grid_seconds, 4)

            quantized.append({
                "pitch": n["pitch"],
                "onset": quant_onset,
                "offset": quant_offset
            })

        return quantized
    
    def get_full_chord_list(self, subdivision=0.25):

        quarter_length = 60 / self.tempo
        notes = sorted(self.quantize_notes(subdivision), key=lambda x: x["onset"])

        chord_list = []
        i = 0
        midi_end = self.duration

        while i < len(notes):

            current_onset = notes[i]["onset"]
            current_pitches = [notes[i]["pitch"]]

            j = i + 1

            while j < len(notes) and notes[j]["onset"] == current_onset:
                current_pitches.append(notes[j]["pitch"])
                j += 1

            if j < len(notes):
                next_onset = notes[j]["onset"]
            else:
                next_onset = midi_end

            duration_seconds = next_onset - current_onset
            duration_beats = round(duration_seconds / quarter_length, 3)

            current_chord = chord.Chord(current_pitches)

            intervals = []
            dissonant_intervals = []

            for i_note in range(len(current_chord.pitches)):
                for j_note in range(i_note + 1, len(current_chord.pitches)):
                    intv = interval.Interval(
                        current_chord.pitches[i_note],
                        current_chord.pitches[j_note]
                    )
                    intervals.append(intv.simpleName)

                    if not intv.isConsonant():
                        dissonant_intervals.append(intv.simpleName)

            chord_list.append({
                "name": current_chord.pitchedCommonName,
                "beats": duration_beats,
                "is_consonant": len(dissonant_intervals) == 0,
                "intervals": intervals,
                "dissonant_intervals": dissonant_intervals
            })

            i = j

        return chord_list
    
    def enforce_repeating_progression(self):
        chords = self.chord_list
        if not chords:
            return chords
        names = [c["name"] for c in chords]
        for size in range(1, len(names)//2 + 1):
            pattern = names[:size]
            mismatch_count = 0
            for i in range(len(names)):
                expected = pattern[i % size]
                if names[i] != expected:
                    mismatch_count += 1
            if mismatch_count <= size:
                for i in range(len(names)):
                    chords[i]["name"] = pattern[i % size]
                return chords
        return chords
    
    def to_dict(self):
        return {
            "midi_file": self.midi_file,
            "tempo": self.tempo,
            "duration": self.duration,
            "time_signature": self.time_signature,
            "key_signature": self.key_signature,
            "scale_pitches": self.scale_pitches,
            "notes": self.notes,
            "chord_list": self.chord_list,
            "chord_progression": self.chord_prog,
            "chords_with_rhythm": self.chords_rhythm
        }
    
    def export_to_json(self, output_file="midi_analysis.json"):
        with open(output_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

start = time.time()
midi_path = "samples/repeating_chords.mid"
midi_stream = MIDI_Stream(midi_path)
midi_stream.print_info()
# midi_stream.print_prompt_low()
# midi_stream.print_prompt_mid()
# midi_stream.print_prompt_high()
chords = midi_stream.get_full_chord_list()
midi_stream.export_to_json("output.json")
end = time.time()
print(end - start)