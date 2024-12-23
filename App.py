import streamlit as st
from rtttl import (
    freq_to_note_name,
    generate_tone,
    parse_rtttl,
    generate_arduino_code,
    parse_rtttl2,
)
import numpy as np
from scipy.io.wavfile import write
import tempfile
import plotly.graph_objects as go

# Configuração inicial da página
st.set_page_config(page_title="RTTTL to Arduino", page_icon="🎶", layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🎶 RTTTL to Arduino 🎶</h1>",
    unsafe_allow_html=True,
)

# Introdução ao RTTTL
st.markdown(
    """
<style>
body {
    background: linear-gradient(90deg, #f3f4f6, #e8f5e9);
    font-family: 'Arial', sans-serif;
}
textarea {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    border: 1px solid #4CAF50;
    border-radius: 5px;
}
button {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 15px;
    font-size: 16px;
    cursor: pointer;
}
button:hover {
    background-color: #45a049;
}
</style>
""",
    unsafe_allow_html=True,
)

st.write(
    """
Esta ferramenta simula o clássico compositor Nokia e permite criar e testar melodias no formato RTTTL.
Insira um código RTTTL e visualize seu equivalente em código Arduino ou toque diretamente no navegador.

### Exemplo de código RTTTL:

```plaintext
Flinstones:d=4,o=5,b=40:32p,16f6,16a#,16a#6,32g6,16f6,16a#.,16f6,32d#6,32d6,32d6,32d#6,32f6,16a#,16c6,d6,16f6,16a#.,16a#6,32g6,16f6,16a#.,32f6,32f6,32d#6,32d6,32d6,32d#6,32f6,16a#,16c6,a#,16a6,16d.6,16a#6,32a6,32a6,32g6,32f#6,32a6,8g6,16g6,16c.6,32a6,32a6,32g6,32g6,32f6,32e6,32g6,8f6,16f6,16a#.,16a#6,32g6,16f6,16a#.,16f6,32d#6,32d6,32d6,32d#6,32f6,16a#,16c.6,32d6,32d#6,32f6,16a#,16c.6,32d6,32d#6,32f6,16a#6,16c7,8a#.6
```
---

Vamos criar música juntos! 🎵
"""
)
st.write("---")


melodias_predefinidas = {
    "Flinstones": "Flinstones:d=4,o=5,b=40:32p,16f6,16a#,16a#6,32g6,16f6,16a#.,16f6,32d#6,32d6,32d6,32d#6,32f6,16a#,16c6,d6,16f6,16a#.,16a#6,32g6,16f6,16a#.,32f6,32f6,32d#6,32d6,32d6,32d#6,32f6,16a#,16c6,a#,16a6,16d.6,16a#6,32a6,32a6,32g6,32f#6,32a6,8g6,16g6,16c.6,32a6,32a6,32g6,32g6,32f6,32e6,32g6,8f6,16f6,16a#.,16a#6,32g6,16f6,16a#.,16f6,32d#6,32d6,32d6,32d#6,32f6,16a#,16c.6,32d6,32d#6,32f6,16a#,16c.6,32d6,32d#6,32f6,16a#6,16c7,8a#.6",
    "Mission Impossible": "Mission Impossible:d=16,o=6,b=95:32d,32d#,32d,32d#,32d,32d#,32d,32d#,32d,32d,32d#,32e,32f,32f#,32g,g,8p,g,8p,a#,p,c7,p,g,8p,g,8p,f,p,f#,p,g,8p,g,8p,a#,p,c7,p,g,8p,g,8p,f,p,f#,p,a#,g,2d,32p,a#,g,2c#,32p,a#,g,2c,a#5,8c,2p,32p,a#5,g5,2f#,32p,a#5,g5,2f,32p,a#5,g5,2e,d#,8d",
    "Super Mario": "Super Mario:d=4,o=5,b=100:16e6,16e6,32p,8e6,16c6,8e6,8g6,8p,8g,8p,8c6,16p,8g,16p,8e,16p,8a,8b,16a#,8a,16g.,16e6,16g6,8a6,16f6,8g6,8e6,16c6,16d6,8b,16p,8c6,16p,8g,16p,8e,16p,8a,8b,16a#,8a,16g.,16e6,16g6,8a6,16f6,8g6,8e6,16c6,16d6,8b,8p,16g6,16f#6,16f6,16d#6,16p,16e6,16p,16g#,16a,16c6,16p,16a,16c6,16d6,8p,16g6,16f#6,16f6,16d#6,16p,16e6,16p,16c7,16p,16c7,16c7,p,16g6,16f#6,16f6,16d#6,16p,16e6,16p,16g#,16a,16c6,16p,16a,16c6,16d6,8p,16d#6,8p,16d6,8p,16c6",
    "The Simpsons": "The Simpsons:d=4,o=5,b=160:c.6,e6,f#6,8a6,g.6,e6,c6,8a,8f#,8f#,8f#,2g,8p,8p,8f#,8f#,8f#,8g,a#.,8c6,8c6,8c6,c6",
    "Indiana Jones": "Indiana Jones:d=4,o=5,b=250:e,8p,8f,8g,8p,1c6,8p.,d,8p,8e,1f,p.,g,8p,8a,8b,8p,1f6,p,a,8p,8b,2c6,2d6,2e6,e,8p,8f,8g,8p,1c6,p,d6,8p,8e6,1f.6,g,8p,8g,e.6,8p,d6,8p,8g,e.6,8p,d6,8p,8g,f.6,8p,e6,8p,8d6,2c6",
    "James Bond": "James Bond:d=4,o=5,b=320:c,8d,8d,d,2d,c,c,c,c,8d#,8d#,2d#,d,d,d,c,8d,8d,d,2d,c,c,c,c,8d#,8d#,d#,2d#,d,c#,c,c6,1b.,g,f,1g.",
    "Star Wars": "Star Wars:d=4,o=5,b=45:32p,32f#,32f#,32f#,8b.,8f#.6,32e6,32d#6,32c#6,8b.6,16f#.6,32e6,32d#6,32c#6,8b.6,16f#.6,32e6,32d#6,32e6,8c#.6,32f#,32f#,32f#,8b.,8f#.6,32e6,32d#6,32c#6,8b.6,16f#.6,32e6,32d#6,32c#6,8b.6,16f#.6,32e6,32d#6,32e6,8c#6",
    "Mozzart": "we-rock:d=4,o=6,b=140:32d#.5,32d.5,32d#.5,8f#.5,32g#.5,32f#.5,32f.5,32f#.5,8a#.5,16b5,16a#5,16a5,16a#5,16f6,16d#6,16d6,16d#6,16f6,16d#6,16d6,16d#6,8f#.6,8d#6,8f#6,32c#6,32d#6,16f6,8d#6,8c#6,8d#6,32c#6,32d#6,16f6,8d#6,8c#6,8d#6,32c#6,32d#6,16f6,8d#6,8c#6,8c6,4a#5,16f5,32d#5,16d5,16d#5,4f#5,16g#5,16f#5,16f5,16f#5,4a#5,16b5,16a#5,16a5,16a#5,16f6,16d#6,16d6,16d#6,16f6,16d#6,16d6,16d#6,4f#6,8d#6,8f#6,32c#6,32d#6,16f6,8d#6,8c#6,8d#6,32c#6,32d#6,16f6,8d#6,8c#6,8d#6,32c#6,32d#6,16f6,8d#6,8c#6,8c6,4a#5,8a#5,8b5,8c#6,8c#6,16d#6,16c#6,16b5,",
    "Matrix": "Matrix:d=4,o=6,b=50:32c#5,32d#5,16g#5,16c#5,16c#5,16g#5,16g#5,16g5,32d#5,32f5,16g5,16d#5,16f5,16g5,16c#5,16g#5,16c#5,16c#5,16g#5,16g#5,16g5,16f5,d#5,32c#5,32d#5,16g#5,16c#5,16c#5,16g#5,16g#5,16g5,32d#5,32f5,16g5,16f5,16g5,16g#5,16c,16a#5,16g#5,16a#5,16g#5,16g5",
    "The X Files": "The X Files:d=4,o=5,b=112:16c,16d#,16g,8g#,2p,8p,c,c,c,c,g,f,g,a#,16g,16d#,16g,8g#,2p,p,2d.6,d#6,d6,c6,a#,d6,2g.,d#6,d6,c6,a#,d6,1g,16c,16d#,16g,8g#,2p,p,c,c,c",
    "Beatles - All you need is love": "Beatles - All you need is love:d=4,o=5,b=140:8g6,16p,8g6,8g6,16p,8g6,16p,16p,8g6,2p,16b6,16p,16p,8a#6,8a6,16g#6,8g6,p,8g6,16p,8g6,8g6,16p,8g6,8p,8g6,p,8p,8b6,16p,8a#6,16a6,8g#6,8g6,p,8g6,16p,8g6,8g#6,16p,8g#6,8p,a6,p,2e6,p,8d6,16e6,8d6,8p,16c6,8c6,",
    "X-Men-Them": "X-Men-Them:d=4,o=6,b=70:32g,32c,32d,32d_,8d,16c,g,32g,32c.,32d,32d_,8d,16c,g_,32g,32c,32d,32d_.,8d,16c,2d_,16d,2c,32c,32f,32g,32g_.,8g,16f,8c.,32c,32f,32g,32g_,8g,16f,8c_,32g,32c.,32d,32d_.,8d,16c,2d_,16d,16c",
    "X-MenCarto": "X-MenCarto:d=4,o=6,b=125:8c,8c,8d_,8c,8d_,8d_,8f,8d_,8c,8c,8d_,8c,8d_,8d_,8f,8d_,8c,8c,8d_,8c,8d_,8d_,8f,8d_,8c,8c,8d_,8c,d_,8g5,16c,16d_,d,8c,2g5,16c,16d_,d,8c,2g_5,16c,16d_,d,8c,d_,8p,g5,c,8p",
}

melodia_selecionada = st.selectbox(
    "Escolha uma melodia pré-definida:",
    ["Selecione..."] + list(melodias_predefinidas.keys()),
)


def play_melody(melody, sample_rate=44100):
    audio = np.concatenate(
        [generate_tone(freq, duration, sample_rate) for freq, duration in melody]
    )
    audio = (audio * 32767).astype(np.int16)  # Convert to 16-bit PCM format
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, sample_rate, audio)
    st.audio(temp_file.name, format="audio/wav")


# Função para exibir visualização gráfica das notas
def plot_notes(melody):
    frequencies, durations = zip(*melody)
    times = np.cumsum(durations)
    note_names = [freq_to_note_name(freq) for freq in frequencies]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,  # Eixo X é o tempo acumulado
            y=frequencies,  # Eixo Y é a frequência
            mode="lines+markers+text",
            text=note_names,  # Nome das notas exibido como rótulo
            textposition="top center",
            line=dict(color="royalblue", width=2),
            marker=dict(size=8),
        )
    )
    fig.update_layout(
        title="Visualização da Melodia com Notas Musicais",
        xaxis_title="Tempo (ms)",
        yaxis_title="Frequência (Hz)",
        template="plotly_white",
    )
    st.plotly_chart(fig)


# Carregar melodia pré-definida ou entrada personalizada
if melodia_selecionada != "Selecione...":
    codigo_rtttl = melodias_predefinidas[melodia_selecionada]
else:
    codigo_rtttl = ""

codigo_rtttl = st.text_area(
    "Insira o código RTTTL:",
    value=codigo_rtttl,  # Atualiza o valor do text_area com o código RTTTL selecionado
    placeholder="Exemplo: StarWars:d=4,o=5,b=120:c.6,e.6,g6,a6,b6,a6,g6,e6,c.6",
    height=150,
)


# Exibe o código Arduino assim que o campo é preenchido
if codigo_rtttl:
    codigo_rtttl = codigo_rtttl.strip()
    try:
        name, parsed_notes = parse_rtttl2(codigo_rtttl)
        arduino_code = generate_arduino_code(name, parsed_notes)
        st.markdown(
            "<h2 style='color: #4CAF50;'>Código Arduino Gerado:</h2>",
            unsafe_allow_html=True,
        )
        st.code(arduino_code, language="c")

        st.markdown(
            "<h2 style='color: #4CAF50;'>Visualização da Melodia:</h2>",
            unsafe_allow_html=True,
        )
        plot_notes(parsed_notes)

    except KeyError as ke:
        st.error(f"Nota inválida encontrada: {ke}. Verifique o formato do RTTTL.")
    except Exception as e:
        st.error(f"Erro ao gerar código Arduino: {e}")

    try:
        st.markdown(
            f"<p style='color: #4CAF50;'>🎶 Tocando: {codigo_rtttl.split(":")[0]}</p>",
            unsafe_allow_html=True,
        )
        melody = parse_rtttl(codigo_rtttl)
        play_melody(melody)
    except Exception as e:
        st.error(f"Erro ao tocar RTTTL: {e}")
else:
    st.error("Insira um código RTTTL válido!")

# Rodapé
st.markdown(
    """
<footer style='text-align: center; margin-top: 50px;'>
    <p>Inspirado em:<br> 
        <a href='https://eddmann.com/nokia-composer-web/' target='_blank' style='color: #4CAF50;'>Nokia Composer Web</a>.<br>
        <a href='https://adamonsoon.github.io/rtttl-play/' target='_blank' style='color: #4CAF50;'>RTTTL Play</a>.<br>
        <a href='https://en.wikipedia.org/wiki/Ring_Tone_Text_Transfer_Language' target='_blank' style='color: #4CAF50;'>RTTTL Wiki</a>.<br>
        <a href='https://picaxe.com/rtttl-ringtones-for-tune-command/' target='_blank' style='color: #4CAF50;'>Baixe Tons aqui</a>.<br>
    </p>
</footer>
""",
    unsafe_allow_html=True,
)
