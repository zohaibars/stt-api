from faster_whisper import WhisperModel
import subprocess
import numpy as np
import torch
import time

# Initialize the Faster Whisper model for Urdu language
model_path = "large-v2"  # Specify the large-v model
model = WhisperModel(model_path, device="cuda" if torch.cuda.is_available() else "cpu")

def ffmpeg_stream_to_numpy(stream_url):
    """
    Function to capture the audio stream using FFmpeg and return it as a NumPy array.
    """
    ffmpeg_command = [
        "ffmpeg",
        "-i", stream_url,   # URL of your live stream
        "-f", "f32le",      # Output format (32-bit floating point)
        "-ac", "1",         # Mono audio
        "-ar", "16000",     # Sample rate (16kHz)
        "-vn",              # No video
        "-loglevel", "error",  # Suppress output except errors
        "pipe:1"           # Output to stdout
    ]

    with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        while True:
            audio_data = process.stdout.read(4096)  # Read audio in chunks
            if not audio_data:
                break
            
            # Convert bytes to NumPy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            yield audio_array

def process_audio_stream(stream_url):
    """
    Function to process the audio stream and transcribe it with Faster Whisper.
    """
    audio_buffer = np.array([], dtype=np.float32)  # Buffer to accumulate audio
    start_time = time.time()

    while True:
        audio_chunk = next(ffmpeg_stream_to_numpy(stream_url))  # Get audio data
        audio_buffer = np.concatenate((audio_buffer, audio_chunk))  # Accumulate audio data

        # Check if enough data is available for 5 seconds of audio
        if len(audio_buffer) >= 16000 * 5:  # 16000 samples per second * 5 seconds
            # Transcribe the buffered audio directly with Faster Whisper for Urdu language
            try:
                # Transcribe the buffered audio
                segments, _ = model.transcribe(audio_buffer, language="ur")  # Specify language as Urdu

                current_text = ""  # Reset for the current 5 seconds of text

                # Combine the transcription results for the current buffer
                for segment in segments:
                    current_text += segment.text + " "  # Accumulate the transcription text

                # Print the current text every 5 seconds
                print(f"Current Transcription (last 5 seconds): {current_text.strip()}")
                
                # Remove the processed audio from the buffer
                audio_buffer = audio_buffer[int(16000 * 5):]  # Keep only unprocessed audio
                start_time = time.time()  # Reset the timer
            except Exception as e:
                print(f"Error processing audio stream: {e}")

if __name__ == "__main__":
    stream_url = "udp://@239.1.1.9:1111"  # Replace with your actual live stream URL
    process_audio_stream(stream_url)
