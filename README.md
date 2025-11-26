# VoicePy (Streamlit + Coqui TTS)

A Streamlit and Coqui TTS web app designed to convert .docx documents into natural-sounding audio files.

## Key Features

- DOCX to Speech Conversion – Reads and converts Word document paragraphs into high-quality .wav audio files.

- Multilingual Support – Easily switch between Portuguese and Spanish narration.

- Custom Voices – Select your own voice sample (.wav) for cloning and personalized narration.

- GPU Acceleration – Automatic CUDA detection for faster inference when available.

- Usage Lock System – Prevents simultaneous execution by multiple users.

- Error Handling & Logs – Detects long text issues and saves problematic paragraphs for review.

- Streamlit Web Interface – Simple, responsive, and ready for local or remote use.
  
## Prerequisites

- Python 3.x
- CUDA-capable GPU (recommended) or CPU
- Required Python packages:
  - python-docx
  - torch
  - TTS
  - tkinter

## Quick start

> Requires **Python 3.10+**. CUDA is recommended but optional.

```bash
# 1) Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install streamlit torch python-docx psutil TTS==0.22.0

# 3) (Optional) Accept Coqui TTS terms via env var
#    You can also set this in your shell profile.
set COQUI_TOS_AGREED=1    # Windows (cmd)
$env:COQUI_TOS_AGREED=1   # Windows (PowerShell)
export COQUI_TOS_AGREED=1 # macOS/Linux

# 4) Run the app
streamlit run web_travel_tts.py
```

> If you use a GPU, ensure your PyTorch install matches your CUDA version. See the official PyTorch install matrix.

## How to use

1. **Open the app** (`streamlit run web_travel_tts.py`).
2. In the **sidebar**:
   - Choose the **narration language** (`en`, `es`, `pt`).
   - Point to a **folder with reference voices** (`.wav` files) and select one.
   - (Advanced) Set the **Coqui model** (default `tts_models/multilingual/multi-dataset/xtts_v2`) and **device** (`cuda`/`cpu`).
   - (Advanced) Toggle *Remove single trailing dot from sentences* if you prefer crisper stops.
   - (Optional) Override the **output base folder**.
3. Use **Quick test** to generate a short **sample** with the selected voice.
4. **Upload your `.docx`**. Each paragraph becomes `audio_#.wav` inside:
   ```
   <OUTPUT_BASE>/<LANG>_<DOC_BASENAME>/
   ```
   The original `.docx` is also saved there.
5. If any paragraph logs a **character-limit warning**, the corresponding file is renamed with a suffix:
   ```
   audio_# __may have limit warning.wav
   ```
   and a report file `paragraphs_with_limit_warnings.docx` is created in the same folder.

## Reference voice tips

- Use a **clean, noise-free** `.wav` that represents the voice you want.
- **English**, **Spanish**, and **Portuguese** are supported via `xtts_v2`. Other languages may work, but are untested.
- Results improve with **longer**, **higher-quality** reference audio (but avoid background music).

## Configuration

- **Output base folder**: Default is a Windows path:
  ```
  C:\Users\
  ```
  You can change this in the sidebar.
- **Voice folder** default:
  ```
  C:\Users\
  ```

## Troubleshooting

- **Torch / CUDA mismatch**: Reinstall PyTorch matching your CUDA version.
- **No audio files generated**: Check the **stdout logs** area for errors.
- **Long paragraphs**: If you see "exceeds the character limit", split the paragraph. The app will also flag and list them in the report.
- **Performance**: GPU is strongly recommended for large documents.

## Notes

- This app **monkey-patches** the Coqui `Synthesizer.split_into_sentences` to optionally remove single trailing periods. Disable in the **Advanced options** if undesired.
- The app replaces literal `.` with `,.` when reading `.docx` paragraphs to smooth phrasing on some voices. Adjust as needed.

## Acknowledgments

- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [Streamlit](https://streamlit.io)

## License

This project is free to use and modify. Please ensure you comply with Coqui TTS's terms of service and licensing requirements.
