from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
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
        # self.duration = round(self.midi_stream.get_end_time(), 2)
        if (tempo == None):
            self.tempo = self.get_tempo()
        self.duration = self.get_duration()
        self.notes = self.get_notes()
        self.beats_total = int((self.tempo/60) * self.duration * 2)
        self.key_signature = self.get_key_signature()
        self.time_signature = self.get_time_signature()
        self.chord_list = self.get_full_chord_list()
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
        return round((self.tempo / 60) * 3, 1)
    
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
        print(self.midi_stream21[meter.TimeSignature][0])
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

        for chord_name, _, _ in self.chord_list:
            if chord_name not in seen:
                seen.add(chord_name)
                chord_prog.append(chord_name)

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
        # full = self.get_full_chord_list()

        # if not full:
        #     return []

        # chords_with_rhythm = []
        # current_chord = full[0][0]
        # count = 1  # number of eighth-note intervals

        # for name, _ in full[1:]:
        #     if name == current_chord:
        #         count += 1
        #     else:
        #         chords_with_rhythm.append((current_chord, count))
        #         current_chord = name
        #         count = 1

        # chords_with_rhythm.append((current_chord, count))
        # return chords_with_rhythm
        full = self.get_full_chord_list()

        if not full:
            return []

        chords_with_rhythm = []

        for name, beats, disonance in full:
            if beats == 4:
                rhythm = "whole note"
            elif beats == 2:
                rhythm = "half note"
            elif beats == 1:
                rhythm = "quarter note"
            elif beats == 0.5:
                rhythm = "eighth note"
            # if beats:
            #     rhythm = duration.Duration(beats)
            else:
                rhythm = f"{beats} beats"

            chords_with_rhythm.append((name, rhythm))

        return chords_with_rhythm
    
    def get_key_signature(self):
        k = self.midi_stream21.analyze('key')
        return k.name
    
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

    def get_full_chord_list(self):
        quarter_length = 60 / self.tempo

        notes = sorted(self.notes, key=lambda x: x["onset"])

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
            chord_name = chord.Chord(current_pitches).pitchedCommonName
            current_chord = chord.Chord(current_pitches)
            chord_list.append((chord_name, duration_beats, current_chord.isConsonant()))

            i = j
        return chord_list
        # quarter_length = 60 / self.tempo
        # eigth_length = quarter_length / 2
        # chord_list = []
        # curr_chord = []
        # # curr_highest = 0
        # # curr_lowest = 100000
        # curr_highest_pitch = 0
        # curr_lowest_pitch = 100000
        # curr_max_interval_length = eigth_length
        # i = 0
        # for interval in range(self.beats_total):
        #     # self.key_signature.append(pretty_midi.KeySignature())
        #     while i < len(self.notes) and (self.notes[i]["onset"] <= curr_max_interval_length):
        #         curr_chord.append(self.notes[i]["pitch"])
        #         if self.notes[i]["pitch"] >= curr_highest_pitch:
        #             # curr_highest = self.notes[i]["onset"]
        #             curr_highest_pitch = self.notes[i]["pitch"]
        #         if self.notes[i]["pitch"] <= curr_lowest_pitch:
        #             # curr_lowest = self.notes[i]["onset"]
        #             curr_lowest_pitch = self.notes[i]["pitch"]
        #         i += 1
        #     chord_list.append((chord.Chord(curr_chord).pitchedCommonName, str(interval + 1)))
        #     curr_max_interval_length += eigth_length
        #     # curr_highest = 0
        #     # curr_lowest = 100000
        #     if i < len(self.notes) and curr_max_interval_length >= self.notes[i]["onset"]:
        #         curr_chord = []
        #         curr_highest_pitch = 0
        #         curr_lowest_pitch = 100000
        # # print("Chord List:")
        # # pprint.pp(chord_list)
        # return chord_list

# class Handler(FileSystemEventHandler):
#     def on_modified(self, event):
#         if event.src_path == ".\\samples\\midi_export.mid":
#             print("Updated MIDI file...")
#             midi_path = "samples/midi_export.mid"
#             midi_stream = MIDI_Stream(midi_path)
#             midi_stream.print_info()
#             chords = midi_stream.get_full_chord_list()

# observer = Observer()
# observer.schedule(Handler(), ".")
# observer.start()

# try:
#     while True:
#         pass
# except:
#     observer.stop()
# observer.join()
start = time.time()
midi_path = "samples/midi_export3.mid"
midi_stream = MIDI_Stream(midi_path)
midi_stream.print_info()
# midi_stream.print_prompt_low()
# midi_stream.print_prompt_mid()
# midi_stream.print_prompt_high()
chords = midi_stream.get_full_chord_list()
end = time.time()
print(end - start)