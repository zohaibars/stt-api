import os
from pydub import AudioSegment
import subprocess


async def extract_audio_from_video(video_path, output_audio_path):
    """
    Extract audio from a video file using ffmpeg and set the audio sampling rate to 16000 Hz.

    Parameters:
        video_path (str): Path to the input video file.
        output_audio_path (str): Path to save the extracted audio file.
    """
    try:
        # Use ffmpeg to extract audio from video with a sampling rate of 16000 Hz
        command = [
            'ffmpeg',
            '-i', video_path,
            '-q:a', '0',  # Set audio quality
            '-map', 'a',  # Map only audio
            '-ar', '16000',  # Set audio sampling rate to 16000 Hz
            '-y',  # Overwrite output file without asking
            output_audio_path,
        ]
        
        # Redirect stdout and stderr to subprocess.PIPE to suppress output
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
    except subprocess.CalledProcessError as e:
        # Handle errors without printing ffmpeg output
        print(f"Error extracting audio from {video_path}: {e.stderr.decode()}")

async def split_audio_into_chunks(audio_path, output_folder, chunk_duration_ms=10 * 1000, min_chunk_duration_ms=1000):
    """
    Split audio file into chunks of specified duration and save them to the output folder.
    Only chunks longer than the minimum duration are saved, except for the last chunk which is merged
    with the previous one if it's shorter than the minimum duration.

    Parameters:
        audio_path (str): Path to the audio file to split.
        output_folder (str): Folder where the audio chunks will be saved.
        chunk_duration_ms (int): Duration of each audio chunk in milliseconds. Default is 10 seconds.
        min_chunk_duration_ms (int): Minimum duration of each chunk in milliseconds. Default is 1 second.

    Returns:
        list: List of dictionaries with start time, end time, and chunk file path.
    """

    # Ensure the output folder exists
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    chunk_number = 1  # Initialize chunk numbering
    chunk_info_list = []  # List to store start time, end time, and chunk paths

    try:
        # Load the audio file
        sound = AudioSegment.from_file(audio_path)
    except Exception as e:
        print(f"Error loading {audio_path}: {e}")
        return chunk_info_list

    # Track the last full chunk to merge the final short chunk
    previous_chunk = None
    previous_start = 0

    # Split audio into chunks of specified duration (in milliseconds)
    for start in range(0, len(sound), chunk_duration_ms):
        end = min(start + chunk_duration_ms, len(sound))
        audio_chunk = sound[start:end]

        # If the current chunk is shorter than 1 second and it's the last chunk, merge it with the previous one
        if len(audio_chunk) < min_chunk_duration_ms and end == len(sound):
            # Merge the last chunk with the previous one
            if previous_chunk is not None:
                merged_chunk = previous_chunk + audio_chunk

                # Update the previous chunk's file with the merged content
                chunk_filename = os.path.join(output_folder, f"chunk_{chunk_number-1}.wav")
                try:
                    merged_chunk.export(chunk_filename, format="wav")

                    # Update the end time of the merged chunk
                    chunk_info_list[-1]["end"] = end / 1000.0

                except Exception as e:
                    print(f"Error exporting merged chunk {chunk_number-1}: {e}")

            continue  # Skip saving this chunk since it was merged with the previous one

        # Save each chunk with a unique filename
        chunk_filename = os.path.join(output_folder, f"chunk_{chunk_number}.wav")
        try:
            audio_chunk.export(chunk_filename, format="wav")

            # Convert start and end time from milliseconds to seconds for readability
            start_time_sec = start / 1000.0
            end_time_sec = end / 1000.0

            # Append chunk info (start time, end time, chunk file path)
            chunk_info_list.append({
                "start": start_time_sec,
                "end": end_time_sec,
                "chunk_path": chunk_filename
            })

            previous_chunk = audio_chunk  # Store the current chunk to potentially merge with the next one
            previous_start = start_time_sec

            chunk_number += 1
        except Exception as e:
            print(f"Error exporting chunk {chunk_number}: {e}")

    print(f"Audio split into chunks and saved to: {output_folder}")
    return chunk_info_list

# audio_file_path = "/home/waqar/MWaqar/stt-api/finetune-whisper/test/testaudio.wav"
# output_folder = "audio_chunks"
# chunks_info = split_audio_into_chunks(audio_file_path, output_folder)

# # Print the details of the audio chunks
# for chunk in chunks_info:
#     print(chunk)