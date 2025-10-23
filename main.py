import os
import time
from pathlib import Path
from docx import Document
import torch
from shutil import copy2, rmtree
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
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] [{status.upper()}] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass

def _console_standby_throttled(msg: str, interval: float = 8.0):
    """Prints a standby log message at limited intervals."""
    global _last_standby_print
    now = time.time()
    if now - _last_standby_print >= interval:
        _console("STANDBY", msg)
        _last_standby_print = now

# =============================
# GENERAL CONFIGURATION
# =============================
p = psutil.Process(os.getpid())
try:
    p.nice(psutil.HIGH_PRIORITY_CLASS)
except Exception:
    pass

os.environ["COQUI_TOS_AGREED"] = "1"

DEFAULT_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DOWNLOAD_PATH = r"C:\\"
textos_com_erro = []

# =============================
# GLOBAL LOCK SYSTEM
# =============================
LOCK_FILE = Path("app_in_use.lock")

def set_app_status(in_use: bool):
    """Creates or removes a lock file to indicate system usage."""
    if in_use:
        LOCK_FILE.write_text("IN_USE")
    else:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink(missing_ok=True)

def is_app_in_use() -> bool:
    """Checks if the system is currently in use by another user."""
    return LOCK_FILE.exists()

# =============================
# UTILITIES
# =============================
def sanitize_name(name: str) -> str:
    """Cleans invalid characters from filenames."""
    base = re.sub(r"[\\/:*?\"<>|]", "_", name)
    base = re.sub(r"\s+", " ", base).strip()
    return base

def list_wav_files(folder: str):
    """Lists all .wav files inside a folder."""
    try:
        p = Path(folder)
        if not p.exists():
            return []
        return [str(f.name) for f in p.glob("*.wav")]
    except Exception:
        return []

params = {
    "remove_trailing_dots": True,
    "voice": "",
    "language": "pt",
    "model_name": DEFAULT_MODEL,
    "device": DEFAULT_DEVICE,
}

def new_split_into_sentences(self, text):
    """Custom sentence splitter that removes single final dots."""
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

Synthesizer.split_into_sentences = new_split_into_sentences

# =============================
# MODEL LOADING
# =============================
@st.cache_resource(show_spinner=True)
def load_model(model_name: str, device: str):
    """Loads and caches the Coqui TTS model."""
    return TTS(model_name).to(device)

def flush_tts_cache():
    """Forces clearing the current model from cache and GPU."""
    try:
        _console("FLUSH", "Clearing TTS model cache...")
        st.cache_resource.clear()
        torch.cuda.empty_cache()
    except Exception as e:
        _console("ERROR", f"Failed to clear cache: {e}")

# =============================
# DOCX READING
# =============================
@st.cache_data(show_spinner=False)
def load_text(file_path):
    """Reads all paragraphs from a .docx file and replaces periods."""
    doc = Document(file_path)
    return [paragraph.text.replace('.', ',.') for paragraph in doc.paragraphs if paragraph.text.strip()]

def generate_audio_filename(index):
    """Generates a sequential name for audio files."""
    return f"audio_{index + 1}.wav"

# =============================
# TTS GENERATION WITH LOG
# =============================
def tts_to_file_logged(model, text: str, out_path: str, language: str, speaker_wav: str, speed: float = 0.85):
    """Generates speech audio and captures model logs."""
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
    _console_standby_throttled("Application started...")
    st.set_page_config(page_title="Travel Audio Generator (WEB)", layout="wide")

    # --- if the lock is old, remove it automatically ---
    if is_app_in_use():
        try:
            mod_time = time.time() - LOCK_FILE.stat().st_mtime
            if mod_time > 600:  # more than 10 minutes without activity? clear it.
                LOCK_FILE.unlink(missing_ok=True)
                _console("INFO", "Old lock automatically removed.")
        except Exception:
            pass

    st.title("Gerador de Áudio de Viagem (WEB)")
    st.caption("Now with simultaneous use blocking and voice switching fix.")

    # ===================================
    # ACTIVE USE WARNING (GLOBAL BANNER)
    # ===================================
    app_status_placeholder = st.empty()
    # always starts as available
    app_status_placeholder.markdown(
        "<div style='background-color:#4CAF50;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:bold;'>✅ Ready to use! No one is using it now.</div>",
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.subheader("Settings")

        language = st.radio("Narration language", options=["pt", "es"], index=0, horizontal=True)
        params["language"] = language

        default_voice_dir = r"C:\\"
        voice_dir = st.text_input("Folder with voices (.wav)", value=default_voice_dir)
        wavs = list_wav_files(voice_dir)

        if not wavs:
            st.warning("No .wav files found in this folder.")
        else:
            selected_wav_name = st.selectbox("Choose a voice (.wav file)", wavs)
            selected_wav_path = str(Path(voice_dir) / selected_wav_name)

            # If the selected voice changes, force model cache flush
            if params.get("voice") and params["voice"] != selected_wav_path:
                flush_tts_cache()

            params["voice"] = selected_wav_path

            st.markdown("**Preview of the selected voice**")
            try:
                with open(selected_wav_path, "rb") as f:
                    st.audio(f.read(), format="audio/wav")
            except Exception as e:
                st.error(f"Error loading voice preview: {e}")

        with st.expander("Advanced options"):
            params["model_name"] = st.text_input("Coqui model", value=params["model_name"])
            params["device"] = st.selectbox("Device", ["cuda", "cpu"], index=0 if DEFAULT_DEVICE == "cuda" else 1)
            params["remove_trailing_dots"] = st.checkbox("Remove single final dot from sentences", value=True)

    st.divider()

    st.markdown("### Quick test for the selected voice (TTS)")
    sample_text = st.text_input("Test text", value="Este é um teste de narração.")
    if st.button("Generate test sample"):
        if not params.get("voice"):
            st.error("Select a voice first.")
        elif is_app_in_use():
            st.error("Another user is using it now. Wait for the green message.")
        else:
            set_app_status(True)
            app_status_placeholder.markdown(
                "<div style='background-color:#ff4d4d;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:bold;'>🚫 Someone is using it! Please wait.</div>",
                unsafe_allow_html=True
            )
            try:
                with st.spinner("Generating sample..."):
                    model = load_model(params["model_name"], params["device"])
                    tmp_sample = Path("./_tmp_sample.wav")
                    _ = tts_to_file_logged(
                        model,
                        text=sample_text,
                        out_path=str(tmp_sample),
                        language=params["language"],
                        speaker_wav=params["voice"],
                        speed=0.9,
                    )
                    with open(tmp_sample, "rb") as f:
                        st.audio(f.read(), format="audio/wav")
            finally:
                if tmp_sample.exists():
                    tmp_sample.unlink(missing_ok=True)
                set_app_status(False)
                app_status_placeholder.markdown(
                    "<div style='background-color:#4CAF50;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:bold;'>✅ Ready to use! No one is using it now.</div>",
                    unsafe_allow_html=True
                )

    st.divider()

    uploaded_file = st.file_uploader("Select the .docx file", type="docx")
    if uploaded_file is not None:
        if is_app_in_use():
            st.error("Another user is generating audio now. Wait for the green message.")
            return

        set_app_status(True)
        app_status_placeholder.markdown(
            "<div style='background-color:#ff4d4d;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:bold;'>🚫 Someone is using it! Please wait.</div>",
            unsafe_allow_html=True
        )

        try:
            _console("RUNNING", f"Received file: {uploaded_file.name}")
            original_name = sanitize_name(uploaded_file.name)
            base_name = os.path.splitext(original_name)[0]
            new_folder_name = f"{params['language']}_{base_name}"
            new_folder_path = os.path.join(DOWNLOAD_PATH, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)

            docx_destination = os.path.join(new_folder_path, original_name)
            with open(docx_destination, "wb") as f:
                f.write(uploaded_file.read())

            paragraphs = load_text(docx_destination)
            model = load_model(params["model_name"], params["device"])

            st.write("Starting audio generation...")
            progress = st.progress(0)
            log_placeholder = st.empty()
            textos_com_erro.clear()
            error_texts = []

            for index, paragraph in enumerate(paragraphs):
                output_file_name = generate_audio_filename(index)
                output_file_path = os.path.join(new_folder_path, output_file_name)

                st.write(f"Generating audio for paragraph {index + 1}/{len(paragraphs)}...")
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
                except Exception as e:
                    log_placeholder.error(f"Error generating audio: {e}")
                    if "exceeds the character limit" in str(e).lower():
                        error_texts.append(paragraph)
                    continue

                if "exceeds the character limit" in (log or "").lower():
                    new_name = f"audio_{index + 1}__possible_error.wav"
                    os.rename(output_file_path, os.path.join(new_folder_path, new_name))
                    textos_com_erro.append(paragraph)

                progress.progress((index + 1) / len(paragraphs))

            if error_texts or textos_com_erro:
                error_docx_path = os.path.join(new_folder_path, "paragraphs_with_error.docx")
                error_doc = Document()
                for t in error_texts + textos_com_erro:
                    error_doc.add_paragraph(t)
                error_doc.save(error_docx_path)
                st.warning(f"Paragraphs with possible errors saved at: {error_docx_path}")

            st.success("Audio generation process completed!")
        finally:
            set_app_status(False)
            app_status_placeholder.markdown(
                "<div style='background-color:#4CAF50;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:bold;'>✅ Ready to use! No one is using it now.</div>",
                unsafe_allow_html=True
            )

    if uploaded_file is None and not is_app_in_use():
        _console_standby_throttled("Waiting for user action.")

if __name__ == "__main__":
    main_app()
