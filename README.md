# VoicePy

## Overview

`VoicePy` is an AI-powered text-to-speech (TTS) synthesis tool designed to convert text from `.docx` documents into natural-sounding audio files. By leveraging advanced deep learning models, `VoicePy` delivers high-quality voice synthesis with customizable options for voice tone, language, and output configuration. 

This tool is ideal for content creators, educators, and anyone looking to transform written text into audio efficiently.

---

## Key Features

- **AI-Powered Voice Synthesis**: Utilizes state-of-the-art artificial intelligence models for realistic and expressive speech generation.
- **Customizable Voices**: Supports the use of custom `.wav` voice samples to personalize the generated audio.
- **Multilingual Support**: Handles multiple languages for text-to-speech synthesis.
- **Batch Processing**: Automatically processes paragraphs from `.docx` files, generating individual audio files for each.
- **GPU Acceleration**: Detects and uses CUDA-enabled GPUs to enhance processing speed.
- **Error Handling**: Robust error detection for smooth user experience, even with complex text inputs.
- **Output Organization**: Saves all outputs in structured folders with logs for easy management.

---

## Requirements

### Dependencies
- Python 3.8 or higher
- Required Libraries:
  - `torch`: For AI model inference.
  - `TTS`: The core library for text-to-speech synthesis.
  - `python-docx`: For reading `.docx` files.
  - `tkinter`: For file selection dialog.
  - `shutil` and `pathlib`: For file and folder management.

### Environment Variable
- `COQUI_TOS_AGREED`: Must be set to `"1"` to confirm agreement with Coqui TTS terms of service.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/voicepy.git
   cd voicepy
   ```

2. Install the required dependencies:
   ```bash
   pip install torch TTS python-docx
   ```

3. Set the `COQUI_TOS_AGREED` environment variable:
   ```bash
   export COQUI_TOS_AGREED=1
   ```

---

## Usage

### Running the Program
1. Launch `VoicePy`:
   ```bash
   python voicepy.py
   ```

2. A file dialog will appear. Select a `.docx` file containing the text to convert.

3. The program will:
   - Process the `.docx` file, splitting it into paragraphs.
   - Use AI models to generate high-quality audio for each paragraph.
   - Save the audio files in a folder named after the input file.

4. Outputs include:
   - Individual `.wav` audio files for each paragraph.
   - A `audio_times.txt` log summarizing processing times.

---

## Parameters and Customization

Modify the `params` dictionary within the script to customize functionality:

- **`remove_trailing_dots`**: Removes trailing dots from sentences for smoother audio (default: `True`).
- **`voice`**: Path to a custom `.wav` voice file for synthesis.
- **`language`**: Language for text-to-speech synthesis (default: `"pt"` for Portuguese).
- **`model_name`**: Pre-trained TTS model to use (default: `tts_models/multilingual/multi-dataset/xtts_v2`).
- **`device`**: Automatically uses `cuda` if GPU is available; otherwise, defaults to `cpu`.

---

## Example Output

```
C:\Users\<username>\Downloads\youtube\<document_name>\
├── audio_1.wav
├── audio_2.wav
├── ...
├── audio_times.txt
└── <document_name>.docx
```

---

## Advanced Features

### AI Integration
`VoicePy` is built on cutting-edge AI text-to-speech models, offering:
- Natural intonation and expression.
- Flexibility in choosing pre-trained or custom models.
- The ability to replicate specific voices with custom samples.

### GPU Optimization
If a CUDA-enabled GPU is available, `VoicePy` accelerates synthesis, reducing audio generation times significantly.

---

## Error Handling

- **Empty Text**: Detects and skips empty or invalid inputs, ensuring smooth processing.
- **TTS Model Errors**: Captures exceptions during synthesis and logs them for troubleshooting.

---

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-branch
   ```
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Acknowledgements

`VoicePy` leverages the powerful [Coqui TTS](https://coqui.ai/) library for its AI-powered voice synthesis. Special thanks to the open-source community for enabling this project.
