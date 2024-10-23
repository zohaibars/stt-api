from pydub import AudioSegment
import os
import yt_dlp
from pydub.silence import split_on_silence
import re
import subprocess
def get_file_duration(file_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    # Decode the output and strip any whitespace/newline characters
    output = result.stdout.decode().strip()
    
    # Use regex to extract the duration as a float
    match = re.search(r'(\d+\.\d+)', output)
    if match:
        return float(match.group(1))
    else:
        raise ValueError("Could not parse duration from output: " + output)
def get_file_size(file_path):
    """
    Get the size of the file in bytes and return a human-readable format.
    """
    file_size = os.path.getsize(file_path)
    return file_size

def format_size(size_in_bytes):
    """
    Format the size in a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
def generate_unique_filename(extension):
    base_filename = "audio_download"
    count = 1
    while True:
        filename = f"{base_filename}_{count}{extension}"
        if not os.path.exists(filename):
            return filename
        count += 1

def download_youtube_audio(url):
    print(f"Downloading audio from YouTube: {url}")
    output_path = generate_unique_filename(".wav")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': output_path + ".%(ext)s",
        'keepvideo': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Rename file if necessary
    if os.path.exists(output_path + ".wav"):
        os.rename(output_path + ".wav", output_path)

    if os.path.exists(output_path):
        print(f"Audio download completed. File saved at: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
    else:
        print(f"Error: File {output_path} not found after download.")

    return output_path



def get_large_audio_chunks_on_silence(path, output_folder="chunks", max_chunk_duration=10 * 1000):
    # Ensure the output folder exists
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)  # Changed to makedirs to handle nested directories

    all_chunks_paths = []
    chunk_number = 1  # Initialize chunk numbering

    try:
        # Open the audio file using pydub
        sound = AudioSegment.from_file(path)
    except Exception as e:
        print(f"Error loading {path}: {e}")
       

    # Split audio sound where silence is 1000 milliseconds or more and get chunks
    chunks = split_on_silence(
        sound,
        min_silence_len=1000,  # Minimum silence length in milliseconds
        silence_thresh=sound.dBFS - 14,  # Silence threshold
        keep_silence=500,  # Keep silence of 500 milliseconds
    )

    # Ensure each chunk is no longer than max_chunk_duration
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_duration:
            # Split large chunks into smaller chunks of max_chunk_duration
            for start in range(0, len(chunk), max_chunk_duration):
                end = start + max_chunk_duration
                final_chunks.append(chunk[start:end])
        else:
            final_chunks.append(chunk)

    # Process each chunk and save with unique filenames
    for audio_chunk in final_chunks:
        # Generate a unique filename with prefix GW_chunk_
        chunk_filename = os.path.join(output_folder, f"chunks_{chunk_number}.wav")
        try:
            audio_chunk.export(chunk_filename, format="wav")
            all_chunks_paths.append(chunk_filename)
            chunk_number += 1  # Increment chunk number for the next chunk
        except Exception as e:
            print(f"Error exporting chunk {chunk_number}: {e}")

    print("Processing complete. Chunks saved to:", output_folder)
    return all_chunks_paths  # Return paths of saved chunks if needed
# download_youtube_audio("https://www.youtube.com/watch?v=y6n3b96WXsA")

def convert_audio_to_16000(audio_path, output_path):
    """
    Convert the audio file to a sampling rate of 16000 Hz and save it.

    Parameters:
        audio_path (str): Path to the input audio file.
        output_path (str): Path to save the converted audio file.
    """
    try:
        # Load the audio file
        sound = AudioSegment.from_file(audio_path)

        # Set the frame rate to 16000 Hz
        sound = sound.set_frame_rate(16000)

        # Export the converted audio file
        sound.export(output_path, format="wav")

        print(f"Audio converted to 16000 Hz and saved to: {output_path}")
    except Exception as e:
        print(f"Error converting audio: {e}")
    return output_path