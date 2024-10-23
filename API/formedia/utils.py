import re
import subprocess 
import os
from pydub import AudioSegment
import unicodedata
import uuid
import logging
from fastapi import HTTPException
# Configure logging to file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("nimar.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)
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
def remove_hindi_text(input_string):
    # Normalize the input string to handle any combined Unicode characters
    normalized_string = unicodedata.normalize('NFC', input_string)
    
    # Regex pattern for Hindi characters (Devanagari script)
    hindi_pattern = re.compile(r'[\u0900-\u097F]+', re.UNICODE)
    
    # Remove all Hindi characters from the string
    result_string = re.sub(hindi_pattern, '', normalized_string)
    
    return result_string
    
def generate_temp_file_name(original_name):
    file_extension = os.path.splitext(original_name)[1]
    temp_file_name = f"{uuid.uuid4().hex}{file_extension}"
    return temp_file_name

def merge_segments(segment_info, max_length=3):
    """
    Merges segments based on max_length.

    Parameters:
    - segment_info: List of dictionaries containing 'start', 'end', and 'text'.
    - max_length: Maximum number of segments to merge into one.

    Returns:
    - merged_segments: List of merged segments with combined start, end, and text.
    """
    merged_segments = []
    current_segment = {"start": None, "end": None, "text": ""}

    for i, segment in enumerate(segment_info):
        if current_segment["start"] is None:
            current_segment["start"] = segment["start"]
        
        current_segment["end"] = segment["end"]
        current_segment["text"] += (segment["text"] + " ")
        
        # If we've reached the max length for a chunk or it's the last segment
        if (i + 1) % max_length == 0 or i == len(segment_info) - 1:
            merged_segments.append({
                "start": current_segment["start"],
                "end": current_segment["end"],
                "text": current_segment["text"].strip()
            })
            # Reset current segment for next chunk
            current_segment = {"start": None, "end": None, "text": ""}

    return merged_segments

async def extract_audio_with_ffmpeg(video_file_path, audio_file_path):
    try:
        command = [
            'ffmpeg', '-i', video_file_path, '-vn', 
            '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', 
            audio_file_path, '-loglevel', 'quiet'
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the audio file was created and is not empty
        if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
            raise HTTPException(status_code=404, detail="No audio found in the provided video.")

        return audio_file_path
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to extract audio from video.")



def extract_audio_clip(audio_file, start_time, end_time, output_file):
    """
    Extracts a segment from an audio file and saves it as a new file.
    
    :param audio_file: Path to the main audio file.
    :param start_time: Start time in seconds (float or int).
    :param end_time: End time in seconds (float or int).
    :param output_file: Output file path for the extracted clip.
    """
    # Load the main audio file
    audio = AudioSegment.from_file(audio_file)
    
    # Convert start and end times to milliseconds
    start_ms = start_time * 1000
    end_ms = end_time * 1000

    # Extract the desired audio segment
    clip = audio[start_ms:end_ms]

    # Save the extracted clip to the specified output file
    clip.export(output_file, format="wav")
    print(f"Clip saved: {output_file}")