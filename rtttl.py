import numpy as np
import re

# Função para converter notas em frequências
NOTE_FREQUENCIES = {
    "c": 261.63,
    "c#": 277.18,
    "d": 293.66,
    "d#": 311.13,
    "e": 329.63,
    "f": 349.23,
    "f#": 369.99,
    "g": 392.00,
    "g#": 415.30,
    "a": 440.00,
    "a#": 466.16,
    "b": 493.88,
    "p": 0,  # p represents a pause
}


def note_to_freq(note, octave):
    if note == "p":
        return 0
    return NOTE_FREQUENCIES[note.lower()] * (2 ** (octave - 4))


def parse_rtttl(rtttl):
    name, settings, melody = rtttl.split(":")
    settings = dict(item.split("=") for item in settings.split(","))
    default_duration = int(settings.get("d", 4))
    default_octave = int(settings.get("o", 5))
    bpm = int(settings.get("b", 63))

    beat_duration = 60 / bpm * 4  # Duration of a whole note in seconds
    melody = re.findall(r"(\d*)([a-gp#]+)(\d*)(\.*)", melody, re.IGNORECASE)

    parsed_melody = []
    for duration, note, octave, dot in melody:
        duration = int(duration) if duration else default_duration
        octave = int(octave) if octave else default_octave
        duration_factor = 1.5 if dot else 1
        note_duration = beat_duration / duration * duration_factor
        note = note.replace(".", "")  # Remove dots from note names for processing
        freq = note_to_freq(note, octave)
        parsed_melody.append((freq, note_duration))
    return parsed_melody


def generate_tone(freq, duration, sample_rate=44100):
    if freq == 0:  # Pause
        return np.zeros(int(sample_rate * duration))
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    return wave


# Funções para tocar áudio usando scipy e numpy
def generate_tone(freq, duration, sample_rate=44100):
    if freq == 0:  # Pausa
        return np.zeros(int(sample_rate * duration))
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    return wave


def parse_rtttl2(rtttl_string):
    # Divide a string RTTTL em seções: nome, parâmetros padrão e notas
    sections = rtttl_string.split(":")
    if len(sections) != 3:
        raise ValueError("Formato RTTTL inválido.")

    name, defaults, notes = sections

    # Processa os parâmetros padrão
    default_settings = {}
    for item in defaults.split(","):
        key, value = item.split("=")
        default_settings[key] = int(value) if key != "b" else int(value)

    # Define os valores padrão
    default_duration = default_settings.get("d", 4)  # Duração
    default_octave = default_settings.get("o", 6)  # Oitava
    bpm = default_settings.get("b", 63)  # Batidas por minuto

    # Converte BPM em milissegundos por batida
    ms_per_beat = 60000 / bpm

    # Processa as notas
    note_pattern = re.compile(r"(?:(\d+)?)([a-gpA-GP])(#?)(\d*)")
    parsed_notes = []

    for match in note_pattern.finditer(notes):
        duration, note, sharp, octave = match.groups()
        duration = int(duration) if duration else default_duration
        octave = int(octave) if octave else default_octave

        if note.lower() == "p":  # Pausa
            frequency = 0
        else:
            note_frequencies = {
                "c": 16.35,
                "d": 18.35,
                "e": 20.60,
                "f": 21.83,
                "g": 24.50,
                "a": 27.50,
                "b": 30.87,
            }
            frequency = note_frequencies[note.lower()] * (2 ** (octave - 4))
            if sharp:
                frequency *= 2 ** (1 / 12)  # Ajuste para sustenido

        note_duration = ms_per_beat * (4 / duration)
        parsed_notes.append(
            (int(frequency * 9), int(note_duration))
        )  # Luciano adicionou * 9 para aumentar o volume

    return name, parsed_notes


def freq_to_note_name(freq):
    if freq == 0:
        return "Pause"
    note_freq_map = {
        "C": 261.63,
        "C#": 277.18,
        "D": 293.66,
        "D#": 311.13,
        "E": 329.63,
        "F": 349.23,
        "F#": 369.99,
        "G": 392.00,
        "G#": 415.30,
        "A": 440.00,
        "A#": 466.16,
        "B": 493.88,
    }
    note_names = list(note_freq_map.keys())
    frequencies = list(note_freq_map.values())
    closest_idx = np.argmin([abs(freq - f) for f in frequencies])
    return note_names[closest_idx]


def generate_arduino_code(name, notes):
    melody_array = ", ".join([str(note[0]) for note in notes])
    duration_array = ", ".join([str(note[1]) for note in notes])

    arduino_code = f"// Melodia: {name}\n"
    arduino_code += "#define TONE_PIN 9\n"
    arduino_code += "int melody[] = { " + melody_array + " };\n"
    arduino_code += "int noteDurations[] = { " + duration_array + " };\n\n"

    arduino_code += "void melodia() {\n"
    arduino_code += "  for (int thisNote = 0; thisNote < sizeof(melody)/sizeof(melody[0]); thisNote++) {\n"
    arduino_code += "    int noteDuration = noteDurations[thisNote];\n"
    arduino_code += "    tone(TONE_PIN, melody[thisNote], noteDuration);\n"
    arduino_code += "    delay(noteDuration);\n"
    arduino_code += "    noTone(TONE_PIN);\n"
    arduino_code += "  }\n"
    arduino_code += "}\n\n"

    arduino_code += "void setup() {\n"
    arduino_code += "  pinMode(TONE_PIN, OUTPUT);\n"
    arduino_code += "}\n\n"

    arduino_code += "void loop() {\n"
    arduino_code += "  melodia();\n"
    arduino_code += "  delay(2000);\n"
    arduino_code += "}\n"
    return arduino_code
