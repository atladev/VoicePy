# VoicePy (Streamlit + Coqui TTS)

Generate clean voiceovers from a `.docx` script — one WAV per paragraph — using **Coqui TTS** with a **reference voice**.  
Built as a Streamlit web app for fast preview and batch export.

## Features

- **Paragraph-to-file**: Upload a `.docx`; each non-empty paragraph becomes a separate `.wav`.
- **Reference-voice cloning**: Point to a folder of `.wav` files and pick one as the speaker reference.
- **Multi-language**: Works with **English**, **Spanish**, and **Portuguese** (via `xtts_v2`).
- **Live logs**: Captures stdout from the TTS call and shows it inline.
- **Safety for long sentences**: Optionally removes single trailing dots to reduce overly long sentence inflections.
- **GPU-friendly**: Auto-detects CUDA; falls back to CPU.
  
## Prerequisites

- Python 3.x
- CUDA-capable GPU (recommended) or CPU
- Required Python packages:
  - python-docx
  - torch
  - TTS
  - tkinter

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:
```bash
pip install python-docx torch TTS
```

3. Place your reference voice file (.wav) in the appropriate directory and update the `params` configuration in the script:
```python
params = {
    "remove_trailing_dots": True,
    "voice": "C:\\.wav",  # Update this path
    "language": "en",
    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
    "device": "cuda"  # Use 'cpu' if CUDA is not available
}
```

## Usage

1. Run the script:
```bash
python version_1.0.py
```

2. When prompted, select your input .docx file using the file dialog
3. The program will:
   - Create a new folder named after your document
   - Move the original document to this folder
   - Generate audio files for each paragraph
   - Display progress in real-time

## Output

- Audio files are generated in WAV format
- Each paragraph gets its own audio file named `audio_X.wav` (where X is the paragraph number)
- Files are organized in a folder named after the input document

## Technical Details

### Text Processing
- Custom sentence splitting algorithm
- Handling of trailing dots and punctuation
- Special character preprocessing

### Audio Generation
- Real-time progress tracking
- Threading for progress display
- Error handling for each paragraph
- Support for multiple languages

## Performance

- GPU acceleration provides significant performance improvements
- Progress tracking includes both local (per-paragraph) and global timing
- Memory-efficient processing of large documents

## Limitations

- Requires sufficient disk space for audio output
- Processing time depends on document length and hardware capabilities
- Currently supports .docx format only

## Error Handling

The application includes robust error handling for:
- File selection cancellation
- File moving operations
- Audio generation process
- Resource management

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is free to use and modify. Please ensure you comply with Coqui TTS's terms of service and licensing requirements.
