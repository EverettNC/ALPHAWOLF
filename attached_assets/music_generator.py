# music_generator.py
import pretty_midi
import os


def generate_music(style="ambient"):
    print(f"[MUSIC] Generating {style} music...")
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)

    # Simple ascending scale for demo
    for i, note_number in enumerate(range(60, 68)):
        note = pretty_midi.Note(velocity=100, pitch=note_number, start=i, end=i+1)
        piano.notes.append(note)

    midi.instruments.append(piano)
    output_midi_path = "derek_music_output.mid"
    midi.write(output_midi_path)
    print(f"[MUSIC] MIDI output saved to {output_midi_path}")

    # Convert to WAV
    output_wav_path = output_midi_path.replace(".mid", ".wav")
    try:
        midi = pretty_midi.PrettyMIDI(output_midi_path)
        audio_data = midi.synthesize()

        import soundfile as sf
        sf.write(output_wav_path, audio_data, 44100)
        print(f"[MUSIC] WAV output saved to {output_wav_path}")
    except Exception as e:
        print(f"[ERROR] Failed to convert MIDI to WAV: {e}")

    return output_midi_path, output_wav_path


if __name__ == "__main__":
    generate_music()
