
import os
import time
from pathlib import Path
from docx import Document
import torch
from shutil import rmtree
from TTS.api import TTS
from TTS.utils.synthesizer import Synthesizer
import io
from contextlib import redirect_stdout
import streamlit as st
import psutil
import re

# =============================
# CONSOLE STATUS / LOG HELPERS
# =============================
_last_standby_print = 0.0

def _console(status: str, msg: str = ""):
    """Simple console logger with timestamp and status flag."""
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] [{status.upper()}] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass

def _console_standby_throttled(msg: str, interval: float = 8.0):
    """Avoid spamming STANDBY logs on Streamlit reruns."""
    global _last_standby_print
    now = time.time()
    if now - _last_standby_print >= interval:
        _console("STANDBY", msg)
        _last_standby_print = now

# =============================
# GENERAL CONFIG
# =============================
# Process priority (Windows)
p = psutil.Process(os.getpid())
try:
    p.nice(psutil.HIGH_PRIORITY_CLASS)  # or psutil.REALTIME_PRIORITY_CLASS
except Exception:
    pass

# Required by Coqui TTS (accept terms)
os.environ["COQUI_TOS_AGREED"] = "1"

DEFAULT_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Default output folder for generated audios
DOWNLOAD_PATH = r"C:\\Users\\dud\\Downloads\\youtube\\VIAJENS\\AUDIOS_FEITOS"

# Stores paragraphs that hit warning/limit
flagged_paragraphs = []

# =============================
# UTILITIES
# =============================

def sanitize_name(name: str) -> str:
    """Remove problematic characters from file/folder names."""
    base = re.sub(r"[\\/:*?\"<>|]", "_", name)
    base = re.sub(r"\s+", " ", base).strip()
    return base


def list_wav_files(folder: str):
    try:
        p = Path(folder)
        if not p.exists():
            return []
        return [str(f.name) for f in p.glob("*.wav")]
    except Exception:
        return []


# Custom sentence splitter: remove a single trailing dot from each sentence
params = {
    "remove_trailing_dots": True,
    "voice": "",  # set via UI
    "language": "en",  # set via UI
    "model_name": DEFAULT_MODEL,
    "device": DEFAULT_DEVICE,
}


def new_split_into_sentences(self, text):
    sentences = self.seg.segment(text)
    if params['remove_trailing_dots']:
        sentences_without_dots = []
        for sentence in sentences:
            if sentence.endswith('.') and not sentence.endswith('...'):
                sentence = sentence[:-1]
            sentences_without_dots.append(sentence)
        return sentences_without_dots
    else:
        return sentences

# Apply override to the library
Synthesizer.split_into_sentences = new_split_into_sentences


# =============================
# MODEL LOADING
# =============================
@st.cache_resource(show_spinner=True)
def load_model(model_name: str, device: str):
    return TTS(model_name).to(device)


# =============================
# DOCX READING
# =============================
@st.cache_data(show_spinner=False)
def load_text(file_path):
    doc = Document(file_path)
    # Replace '.' with ',.' to mitigate overly long sentence handling in some voices
    return [paragraph.text.replace('.', ',.') for paragraph in doc.paragraphs if paragraph.text.strip()]


def generate_audio_filename(index):
    return f"audio_{index + 1}.wav"


# =============================
# TTS WITH LOG CAPTURE
# =============================

def tts_to_file_logged(model, text: str, out_path: str, language: str, speaker_wav: str, speed: float = 0.85):
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        model.tts_to_file(
            text=text,
            file_path=out_path,
            speaker_wav=speaker_wav,
            language=language,
            speed=speed,
        )
    return output_buffer.getvalue()


# =============================
# STREAMLIT APP
# =============================

def main_app():
    _console_standby_throttled("App started; listening for UI events...")
    st.set_page_config(page_title="Travel Voiceover Generator (WEB)", layout="wide")

    st.title("Travel Voiceover Generator (WEB)")
    _console_standby_throttled("UI loaded; awaiting user action.")
    st.caption("Now with language selection (EN/ES/PT), folder-based voice selection, and instant preview.")

    with st.sidebar:
        st.subheader("Settings")

        # Narration language
        language = st.radio("Narration language", options=["en", "es", "pt"], index=0, horizontal=True)
        params["language"] = language

        # Voice folder path
        default_voice_dir = r"C:\\Users\\dud\\Downloads\\youtube\\scripts\\voices"
        voice_dir = st.text_input("Folder with reference voices (.wav)", value=default_voice_dir)
        wavs = list_wav_files(voice_dir)
        if not wavs:
            st.warning("No .wav files found in this folder.")
        else:
            selected_wav_name = st.selectbox("Choose the voice (.wav file)", wavs)
            selected_wav_path = str(Path(voice_dir) / selected_wav_name)
            params["voice"] = selected_wav_path

            # Voice preview: play the .wav itself
            st.markdown("**Pre-listen of the selected voice**")
            try:
                with open(selected_wav_path, "rb") as f:
                    st.audio(f.read(), format="audio/wav")
            except Exception as e:
                st.error(f"Failed to load voice preview: {e}")

        # Model and device (optional)
        with st.expander("Advanced options"):
            params["model_name"] = st.text_input("Coqui model", value=params["model_name"])  # usually xtts_v2
            params["device"] = st.selectbox("Device", ["cuda", "cpu"], index=0 if DEFAULT_DEVICE == "cuda" else 1)
            remove_trailing = st.checkbox("Remove single trailing dot from sentences", value=True)
            params["remove_trailing_dots"] = remove_trailing

        # Output folder override (optional)
        global DOWNLOAD_PATH
        DOWNLOAD_PATH = st.text_input("Output base folder for generated audios", value=DOWNLOAD_PATH)

    # DOCX upload
    st.write("Upload a .docx file to generate audios with live logs.")
    uploaded_file = st.file_uploader("Select the .docx file", type="docx")

    # Quick TTS sample preview (without a DOCX)
    st.divider()
    st.markdown("### Quick test of the selected voice (TTS)")
    sample_text = st.text_input("Sample text", value="This is a narration test.")
    if st.button("Generate and play sample"):
        _console("RUNNING", "Generating TTS sample with the selected voice...")
        if not params.get("voice"):
            st.error("Select a voice first.")
        else:
            with st.spinner("Generating sample..."):
                model = load_model(params["model_name"], params["device"])  # cache_resource prevents reload
                tmp_sample = Path("./_tmp_sample.wav")
                try:
                    _ = tts_to_file_logged(
                        model,
                        text=sample_text,
                        out_path=str(tmp_sample),
                        language=params["language"],
                        speaker_wav=params["voice"],
                        speed=0.9,
                    )
                    _console("RUNNING", "Sample generated successfully, playing...")
                    with open(tmp_sample, "rb") as f:
                        st.audio(f.read(), format="audio/wav")
                finally:
                    if tmp_sample.exists():
                        tmp_sample.unlink(missing_ok=True)

    st.divider()

    if uploaded_file is not None:
        _console("RUNNING", f"File received: {uploaded_file.name}. Preparing folders and loading paragraphs...")
        # Use the real uploaded file name for the output folder
        original_name = sanitize_name(uploaded_file.name)
        base_name = os.path.splitext(original_name)[0]
        lang_prefix = params["language"]  # 'en', 'es', or 'pt'
        new_folder_name = f"{lang_prefix}_{base_name}"
        new_folder_path = os.path.join(DOWNLOAD_PATH, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Save the original DOCX into the created folder, preserving the original name
        docx_destination = os.path.join(new_folder_path, original_name)
        with open(docx_destination, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"Output folder created: {new_folder_path}")

        # Load paragraphs
        paragraphs = load_text(docx_destination)

        # Load model (cached)
        model = load_model(params["model_name"], params["device"])
        _console("RUNNING", f"Model loaded ({params['model_name']} on {params['device']}). Starting audio generation...")

        st.write("Starting audio generation...")
        progress = st.progress(0)
        log_placeholder = st.empty()
        flagged_paragraphs.clear()
        error_texts = []

        for index, paragraph in enumerate(paragraphs):
            output_file_name = generate_audio_filename(index)
            output_file_path = os.path.join(new_folder_path, output_file_name)

            st.write(f"Generating audio for paragraph {index + 1}/{len(paragraphs)}...")
            _console("RUNNING", f"Paragraph {index + 1}/{len(paragraphs)}: generating file {output_file_name}...")

            try:
                log = tts_to_file_logged(
                    model,
                    text=paragraph,
                    out_path=output_file_path,
                    language=params["language"],
                    speaker_wav=params["voice"],
                    speed=0.85,
                )
                log_placeholder.code(log or "(no logs)")
                _console("RUNNING", f"Paragraph {index + 1}/{len(paragraphs)} finished: {output_file_name}")
            except Exception as e:
                log_placeholder.error(f"Error generating audio for {output_file_name}: {e}")
                _console("ERROR", f"Failed at paragraph {index + 1}/{len(paragraphs)} ({output_file_name}): {e}")
                if "exceeds the character limit" in str(e).lower():
                    error_texts.append(paragraph)
                continue

            # Check for character-limit warnings in stdout
            if "exceeds the character limit" in (log or "").lower():
                new_name = f"audio_{index + 1}__may have limit warning.wav"
                new_path = os.path.join(new_folder_path, new_name)
                try:
                    os.rename(output_file_path, new_path)
                except Exception:
                    pass
                flagged_paragraphs.append(paragraph)

            progress.progress((index + 1) / max(1, len(paragraphs)))

        # If there were problematic texts, save a docx report
        if error_texts or flagged_paragraphs:
            error_docx_path = os.path.join(new_folder_path, "paragraphs_with_limit_warnings.docx")
            error_doc = Document()
            for t in error_texts + flagged_paragraphs:
                error_doc.add_paragraph(t)
            error_doc.save(error_docx_path)
            st.warning(f"Paragraphs with potential issues saved to: {error_docx_path}")

        st.success("Audio generation completed!")
        _console("DONE", "Generation finished. System on standby, waiting for the next action.")

    # If no file was uploaded, log STANDBY in the console (with throttling)
    if uploaded_file is None:
        _console_standby_throttled("No active tasks. Waiting for DOCX upload, option changes, or button clicks.")


if __name__ == "__main__":
    main_app()
