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


# crie uma função para ler um arquivo com varias musicas rtttl e
# formato do input:
# #1:d=4,o=6,b=180:16p,32g_5,8a5,32p,8a5,8a5,32d_,8e.5,16p,c5,a5,16a,16a5,32g_5,8a5,32p,8g5,a5,32a5,32a5,8p,8a5,32g_5,8a5,32p,16a.5,32p,32g_5,8a5,32p,8g5,8a5,8e5,16e.5,32p,16a.5,32p,32g_5,8a5,32p,8a5,8a5,8g5,8a5,8e5,32e5,32e5,8p,8e5,32g_5
# 1Stunna:d=4,o=6,b=90:2d,c,d_,2d,a_5,8c.,16a5,2g.5,8d_.5,16f5,1d5,2d,c,d_,2d,c,8a.5,16c,2g.5,8d_.5,16f5,1d5
# 'nOnsGel:d=4,o=5,b=112:8c6,8c6,8c6,16c6,8c.6,8c6,8a#,8g#,8g#,8g,8g,8f#,2g,8g#,8g#,8g#,16g#,8g#.,8g#,8g,8f,8f,8d#,8d#,8d,d#,8d#,8d#,8c#,8a#,2a#,8c#,8c#,8c,8g#,2g#,8g,8g#,a#,f,c6,b,2a#.,p,8c6,8c6,8c6,16c6,8c.6,8c6,8a#,8g#,8g#,8g,8g,8f#,2g,8g#,8g#,8g#,16g#,8g#.,8g#,8g,8f,8f,8d#,8d#,8d,d#,8d#,8d#,8c#,8a#,2a#,8c#,8c#,8c,8g#,2g#,8g,8g#,a#,c#6,c6,a#,2g#
# 'tQuero:d=16,o=5,b=63:8f.6,f,2f,8f,e,d,8d.,c,2c,8d,c,a#,4a,4f,4g,g,8f,e,1f
# (Don't)G:d=4,o=5,b=125:8c6,8c6,8c6,8c6,e6,p,8p,a#,8c6,2p,8p,8c6,8c6,8c6,f6,d#6,c6,8f6,8d#6,p,8a#,8c6,8p,8c,8c,8d#,2p,8p,8c,8c,8f,8p,8d#,8p,8c,8p,d#,8d,1p,8d#6,8d6,8c6,8d6,8e6,8e6,2p,8c6,d#6,8d6,2p,8p,8c6,8d#6,8c6,8c6,8a#,c6,8a#,8c6,2p,8p,8a#,8a#,8c6,1p,8a#,8a#,8a#,8a#,a#,8a#,c.6
# (Dont)Gi:d=8,o=6,b=125:c,c,c,c,4e,4p.,4a#5,c,2p,p,c,c,c,4f,4d#,4c,f,d#,4p,a#5,c,p,c5,c5,d#5,2p,p,c5,c5,f5,p,d#5,p,c5,p,4d#5,d5,1p.,d#,d,c,d,e,e,2p,c,4d#,d,2p,p,c,d#,c,c,a#5,4c,a#5,c,2p,p,a#5,a#5,c,1p,a#5,a#5,a#5,a#5,4a#5,a#5,4c.
# (Karma)A:d=4,o=6,b=100:16e5,32f5,32e5,8d_5,8e5,2c,8p,16d,8b5,8a5,16g5,2g5,8p,8e5,8d5,8c5,2f5,8p,16a5,8g_5,8f5,16e5,2e5,8p,8c,8b5,8g5,a5,a5,16g5,16a5,16g5,16a5,8g5,8f5,16e5,16g5,16f5,16e5,d5,8p,8d5,8b5,8d5,g.5,8f5,a5,8g5,8f5,e5
# (Rap)Sup:d=4,o=5,b=200:d,f,a,d,a#,d,a,f,d,f,a,a,a#,d,a,f,d,f,a,d,c6,d,a#,a,d,f,a,d,c6,c,a#,a,d,f,a,d,a#,d,a,f,d,f,a,d,c6,d,a#,a
# (ReachFo:d=4,o=6,b=140:g,g,g,8a,f,2d,8d,8d,f.,d.,8d,8d,f.,2d,p,g,g,g,8a,f,2d,8d,8d,f.,d.,8d,8d,f.,2d.,g,g,g,8a,f,2d,8d,8d,f.,d.,8d,8d,f.,2d,p,g,g,g,8a,f,2d,8d,8d,f.,d.,8d,8d,f.,2d.
# (YouAre):d=4,o=6,b=100:16e5,16p,8p,8d_,8c_,c_,8d_,c_,8b5,16g_5,16p,8b5,8a_5,16a_5,16a_5,16f_5,8b5,16b5,16e5,16p,8p,8d_,8c_,c_,8d_,8c_,16g_5,16p,8b5,16g_5,16p,8b5,8f_,16f_,16f_,16f_5,8a_5,b5,16p,e,8d_,8c_,8c_,8b5,8f_,16e,16e,16g_5,8d_,16c_,16f_5,8d_,16b5,16f_5,8b.5,16e5,16p,16e5,16p,16b5,16b5,16b5,16b5,8b5,16b5,8c_,8b.5,p,16f_5,8f_5,16d_,16p,8d_,16c_,16p,8b.5,8b5
# 007Theme:d=4,o=6,b=125:8c5,16d5,16d5,8d5,d5,8c5,8c5,8c5,16d_5,16d_5,8d_5,d_5,8d5,8d5,8d5,8c5,16d5,16d5,8d5,d5,8c5,8c5,8c5,8c5,16d_5,16d_5,8d_5,d_5,8d5,8c_5,8c5,8c,b,8g,8f,g
# 00brahim:d=4,o=6,b=112:16d.5,32g_5,a.5,32d7,16p,16d,16d5,16d5,16d5,8a5,32c7,16p,16c,16p,16c5,8a_5,16a_5,16a_5,16a_5,16a5,16p,8g.5
# 03Bonnie:d=4,o=5,b=180:32c6,16p,32c6,16p,8c.6,16p,32c6,16p,32c6,16p,16c.6,32p,8b,8p,8b,8p,8b.,16p,32d6,16p,16e,16p,16e.,8p,32p,16e.,32p,8b.,16p,8a,p,32a6,16p,16a6,16p,16a6,16p,16a6,16p,16a6,16p,16a6,16p,16d6,16p,16c6,16p,16a,16p,8f6,8p,8f.6,16p,1e6,8p,32b,32p,32g,32p,1e,32p,16d.6,32p,16d.6,32p,8c6,1b,32p,16a.,32p,16c.6,32p,16d6
# 03Bonnie:d=4,o=5,b=180:c6,8c6,c6,8b,8b,b,8a,a.,8p,e,8p,8e,8e,b,8a,8p,8p,8e,8p,8e,b,a,8p,8c6,8c6,8c6,c6,8b,8b,b,8a,a.,8p,e,8p,8e,8e,b,8a,8p,8p,8e,8p,8e,b,8a,p,c6,8c6,c6,8b,8b,b,8a,a.,8p,e,8p,8e,8e,b,8a,8p,8p,8e,8p,8e,b,a,8p,8c6,8c6,8c6,c6,8b,8b,b,8a,a.,8p,e,8p,8e,8e,b,8a,8p,8p,8e,8p,8e,b,8a,8p
# 03Bonnie:d=4,o=5,b=90:8c6,16c6,8c6,16b,16b,8b,16a,8a,8p,16f,8e,16e,16e,8b,8a,16p,16e,16e,16e,8b,8a,16p,8c7,16c7,8c7,16b6,16b6,8b6,16a6,8a6,8p,16f6,8e6,16e6,16e6,8b6,8a6,16p,16e6,16e6,16e6,8b6,8a6
# retornar um outro arquivo csv com com duas colunas, uma com o nome da musica
# e outra com a melodia no formato rtttl
# formato do output:
# NOME;RTTTL
# 03Bonnie;03Bonnie:d=4,o=5,b=180:32c6,16p,32c6,16p,8c.6,16p,32c6,16p,32c6,16p,16c.6,32p,8b,8p,8b,8p,8b.,16p,32d6,16p,16e,16p,16e.,8p,32p,16e.,32p,8b.,16p,8a,p,32a6,16p,16a6,16p,16a6,16p,16a6,16p,16a6,16p,16a6,16p,16d6,16p,16c6,16p,16a,16p,8f6,8p,8f.6,16p,1e6,8p,32b,32p,32g,32p,1e,32p,16d.6,32p,16d.6,32p,8c6,1b,32p,16a.,32p,16c.6,32p,16d6
# ...
def read_and_save_rtttl(file_path):
    from tqdm import tqdm

    with open(file_path, "r") as file:
        rtttl_songs = file.readlines()

    with open("rtttl_songs.psv", "w") as file:
        file.write("NOME|RTTTL\n")
        for song in tqdm(rtttl_songs):
            name = song.strip().split(":")[0]
            file.write(f"{name}|{song}")


if __name__ == "__main__":
    read_and_save_rtttl("rtttl_songs.txt")
    print("Arquivo rtttl_songs.csv criado com sucesso!")
