# VoicePy

## Overview

`VoicePy` is an AI-powered text-to-speech (TTS) synthesis tool designed to convert text from `.docx` documents into natural-sounding audio files. By leveraging advanced deep learning models, `VoicePy` delivers high-quality voice synthesis with customizable options for voice tone, language, and output configuration. 

This tool is ideal for content creators, educators, and anyone looking to transform written text into audio efficiently.

## Features

- Convert Word documents (.docx) to speech with advanced text preprocessing
- Utilizes the XTTS v2 multilingual model for high-quality voice synthesis
- Real-time progress tracking with visual progress bar
- Automatic organization of output files in dedicated folders
- GPU acceleration support (CUDA) for faster processing
- Custom voice cloning capability using reference audio files

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
