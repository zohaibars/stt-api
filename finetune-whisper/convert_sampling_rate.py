import os
from pydub import AudioSegment

def convert_audio_to_16khz(source_folder):
    # Iterate through all subfolders and files
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith(('.wav', '.mp3', '.flac')):  # Add or remove audio extensions as needed
                file_path = os.path.join(root, file)
                
                # Load the audio file
                audio = AudioSegment.from_file(file_path)
                
                # Convert to 16kHz (16000 Hz) and keep the original file name
                audio_16khz = audio.set_frame_rate(16000)
                
                # Save the new file in the same folder with the same name (overwrite)
                audio_16khz.export(file_path, format="wav")
                print(f"Processed: {file_path}")

dataset_path = os.path.join("/home/waqar/MWaqar/stt-api/Dataset", "Custom_dataset")
convert_audio_to_16khz(source_folder=dataset_path)
