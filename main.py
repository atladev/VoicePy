import os
import time
from pathlib import Path
from docx import Document
import torch
from shutil import copy2, rmtree
from TTS.api import TTS
from TTS.utils.synthesizer import Synthesizer
from tkinter import Tk
from tkinter.filedialog import askopenfilename

os.environ["COQUI_TOS_AGREED"] = "1"

# Configuration parameters for the TTS model
params = {
    "remove_trailing_dots": True,
    "voice": "C:\\.wav",
    "language": "en",
    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
    "device": "cuda"  # Set to 'cpu' if CUDA is not available
}

# Custom sentence splitting function to handle text preprocessing
def new_split_into_sentences(self, text):
    """
    Split text into sentences and optionally remove trailing dots.
    
    Args:
        text (str): Input text to be split into sentences
        
    Returns:
        list: List of processed sentences
    """
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

# Override the original sentence splitting method
Synthesizer.split_into_sentences = new_split_into_sentences

# Initialize and load the TTS model
def load_model():
    """
    Initialize the Text-to-Speech model with specified parameters.
    
    Returns:
        TTS: Initialized TTS model instance
    """
    model = TTS(params["model_name"]).to(params["device"])
    return model

# Generate audio with real-time progress tracking
def generate_audio_with_progress(text, output_path, model):
    """
    Generate audio from text with a progress bar display.
    
    Args:
        text (str): Input text to convert to speech
        output_path (str): Path where the audio file will be saved
        model (TTS): Initialized TTS model instance
    """
    from threading import Thread, Event

    process_done_event = Event()
    duration = 20  # Estimated duration - adjust as needed
    start_time_global = time.time()

    progress_thread = Thread(target=progress_bar, args=(duration, process_done_event, start_time_global))
    progress_thread.start()

    try:
        model.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=params["voice"],
            language=params["language"]
        )
    finally:
        process_done_event.set()
        progress_thread.join()

# Display real-time progress bar
def progress_bar(duration, process_done_event, start_time_global):
    """
    Display a progress bar with timing information.
    
    Args:
        duration (int): Estimated duration of the process
        process_done_event (Event): Event to signal process completion
        start_time_global (float): Start time of the entire process
    """
    print("Generating audio...")
    start_time_local = time.time()

    while not process_done_event.is_set():
        current_time = time.time()
        elapsed_time_local = int(current_time - start_time_local)
        elapsed_time_global = int(current_time - start_time_global)
        
        elapsed_global_minutes = elapsed_time_global // 60
        elapsed_global_seconds = elapsed_time_global % 60
        elapsed_local_minutes = elapsed_time_local // 60
        elapsed_local_seconds = elapsed_time_local % 60
        
        progress = min(int((elapsed_time_local / duration) * 50), 50)
        bar = "[" + "=" * progress + " " * (50 - progress) + "]"
        
        print(f"\r{bar} {elapsed_local_minutes:02}:{elapsed_local_seconds:02} (Total: {elapsed_global_minutes:02}:{elapsed_global_seconds:02})", end="")
        time.sleep(0.1)
    
    print("\nAudio generation completed successfully!")

# Load and process the text document
def load_text(file_path):
    """
    Load and preprocess text from a Word document.
    
    Args:
        file_path (str): Path to the Word document
        
    Returns:
        list: List of processed paragraphs
    """
    doc = Document(file_path)
    return [paragraph.text.replace('.', ',.') for paragraph in doc.paragraphs if paragraph.text.strip()]

def generate_audio_filename(index):
    """
    Generate a filename for the audio output.
    
    Args:
        index (int): Index of the current paragraph
        
    Returns:
        str: Generated filename
    """
    return f"audio_{index + 1}.wav"

def main():
    """
    Main execution function that handles the TTS workflow:
    1. File selection
    2. Directory creation
    3. Text processing
    4. Audio generation
    """
    print("Please select the input file.")
    root = Tk()
    root.withdraw()
    TEXT_FILE_PATH = askopenfilename(title="Select .docx file", filetypes=[("Word Documents", "*.docx")])
    
    if not TEXT_FILE_PATH:
        print("No file selected. Exiting program.")
        return

    paragraphs = load_text(TEXT_FILE_PATH)

    DOWNLOAD_PATH = r"C:\\"
    new_folder_name = os.path.splitext(os.path.basename(TEXT_FILE_PATH))[0]
    new_folder_path = os.path.join(DOWNLOAD_PATH, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    print(f"Created folder: {new_folder_path}")

    docx_filename = os.path.basename(TEXT_FILE_PATH)
    docx_destination = os.path.join(new_folder_path, docx_filename)
    try:
        os.rename(TEXT_FILE_PATH, docx_destination)
        print(f"DOCX file moved to: {docx_destination}")
    except Exception as e:
        print(f"Error moving DOCX file: {e}")

    model = load_model()

    for index, paragraph in enumerate(paragraphs):
        output_file_name = generate_audio_filename(index)
        output_file_path = os.path.join(new_folder_path, output_file_name)

        print(f"Generating audio for paragraph {index + 1}/{len(paragraphs)}...")
        try:
            generate_audio_with_progress(paragraph, output_file_path, model)
        except Exception as e:
            print(f"Error generating audio for {output_file_name}: {e}")

    print("Audio generation process completed!")

if __name__ == "__main__":
    main()
