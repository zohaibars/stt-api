from pydub import AudioSegment
import os
from transformers import WhisperTokenizer
import torchaudio
def check_and_remove_large_files(root_folder, max_tokens=1024):
    """Check all text files in the given folder, and remove both the text and corresponding audio files if the text exceeds the specified number of tokens."""
    # Initialize the Whisper tokenizer
    tokenizer = WhisperTokenizer.from_pretrained('openai/whisper-large-v2')

    # List to store paths of files to be removed
    files_to_remove = []

    # Iterate through each subfolder in the root folder
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            # Check if the file is a text file
            if file.lower().endswith('.txt'):
                # Get the full path of the text file
                file_path = os.path.join(subdir, file)

                # Read the content of the text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read().strip()

                # Tokenize the text
                tokens = tokenizer(text)['input_ids']

                # Check if the number of tokens exceeds the max_tokens limit
                if len(tokens) > max_tokens:
                    # Add both text and corresponding audio file paths to the list for removal
                    files_to_remove.append(file_path)
                    print(file_path)
                    corresponding_audio_path = file_path.replace('.txt', '.wav')
                    files_to_remove.append(corresponding_audio_path)

    # Remove the files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed: {file_path}")
        else:
            print(f"File not found, could not remove: {file_path}")



def calculate_total_duration(root_folder):
    """Calculate the total duration of all audio files in a given folder."""
    total_duration = 0

    # Iterate through each subfolder in the root folder
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            # Check if the file is an audio file (you can add more file extensions if needed)
            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                # Get the full path of the audio file
                file_path = os.path.join(subdir, file)

                # Load the audio file using pydub
                audio = AudioSegment.from_file(file_path)

                # Get the duration in seconds
                duration_seconds = audio.duration_seconds

                # Add the duration of the audio file to the total duration
                total_duration += duration_seconds

    return total_duration


def format_duration(duration_seconds):
    """Format the duration from seconds to hours, minutes, and seconds."""
    total_hours = int(duration_seconds // 3600)
    total_minutes = int((duration_seconds % 3600) // 60)
    total_seconds = int(duration_seconds % 60)

    return f"{total_hours} hours, {total_minutes} minutes, and {total_seconds} seconds"


def remove_empty_text_files(base_directory):
    """Remove empty text files and their corresponding audio files from the dataset."""
    audio_extensions = [".wav", ".mp3", ".flac"]

    for root, dirs, files in os.walk(base_directory):
        for file in files:
            for ext in audio_extensions:
                if file.endswith(ext):
                    audio_file_path = os.path.join(root, file)
                    text_file_path = os.path.join(root, file.replace(ext, ".txt"))

                    if os.path.exists(text_file_path) and os.path.getsize(text_file_path) == 0:
                        print(f"Removing empty files: {audio_file_path} and {text_file_path}")
                        os.remove(audio_file_path)
                        os.remove(text_file_path)

                    if not os.path.exists(audio_file_path) and os.path.exists(text_file_path):
                        print(f"Removing orphan text file: {text_file_path}")
                        os.remove(text_file_path)

                    if os.path.exists(audio_file_path) and not os.path.exists(text_file_path):
                        print(f"Removing orphan audio file: {audio_file_path}")
                        os.remove(audio_file_path)

    for root, dirs, files in os.walk(base_directory, topdown=False):
        for directory in dirs:
            folder_path = os.path.join(root, directory)
            if not os.listdir(folder_path):
                print(f"Removing empty folder: {folder_path}")
                os.rmdir(folder_path)

def get_audio_duration(audio_path):
    """Return the duration of the audio file in seconds."""
    waveform, sample_rate = torchaudio.load(audio_path)
    return waveform.shape[1] / sample_rate

def find_max_audio_duration(base_directory):
    """Find the audio file with the maximum duration."""
    max_duration = 0
    max_duration_file = None

    # Supported audio file extensions
    audio_extensions = [".wav", ".mp3", ".flac"]

    for root, dirs, files in os.walk(base_directory):
        for file in files:
            for ext in audio_extensions:
                if file.endswith(ext):
                    audio_file_path = os.path.join(root, file)

                    # Check the duration of the audio file
                    duration = get_audio_duration(audio_file_path)
                    # print(f"Processing {audio_file_path}, Duration: {duration} seconds")

                    if duration > max_duration:
                        max_duration = duration
                        max_duration_file = audio_file_path

    return max_duration, max_duration_file
def remove_long_audio_files(base_directory, max_duration=10):
    """Remove audio and text files where the audio duration exceeds max_duration."""
    # Supported audio file extensions
    audio_extensions = [".wav", ".mp3", ".flac"]

    for root, dirs, files in os.walk(base_directory):
        for file in files:
            for ext in audio_extensions:
                if file.endswith(ext):
                    audio_file_path = os.path.join(root, file)
                    text_file_path = os.path.join(root, file.replace(ext, ".txt"))

                    # Check the duration of the audio file
                    duration = get_audio_duration(audio_file_path)
                    # print(f"Processing {audio_file_path}, Duration: {duration} seconds")

                    # If the duration exceeds the max_duration, remove both files
                    if duration > max_duration:
                        print(f"Removing {audio_file_path} and {text_file_path} as they exceed {max_duration} seconds")
                        os.remove(audio_file_path)
                        if os.path.exists(text_file_path):
                            os.remove(text_file_path)
if __name__ == "__main__":
    root_folder = "/home/waqar/MWaqar/stt-api/Dataset/Custom_dataset"
    total_duration_seconds = calculate_total_duration(root_folder)
    output = format_duration(total_duration_seconds)
    print(f"Total duration: {output}")
    

    check_and_remove_large_files(root_folder)
    # max_duration, max_duration_file = find_max_audio_duration(root_folder)
    remove_empty_text_files(root_folder)
    # print(f"Max Duration: {max_duration} seconds")
    # print(f"Audio File: {max_duration_file}")

    total_duration_seconds = calculate_total_duration(root_folder)
    output = format_duration(total_duration_seconds)
    print(f"Total duration: {output}")
    
    # check_and_remove_large_files(root_folder)
    # # total_duration_seconds = calculate_total_duration(root_folder)
    # # output = format_duration(total_duration_seconds)
    # # print(f"Total duration: {output}")

    # # base_directory = root_folder
    # # remove_empty_text_files(base_directory)
  
    # total_duration_seconds = calculate_total_duration(root_folder)
    # output = format_duration(total_duration_seconds)
    # print(f"Total duration: {output}")