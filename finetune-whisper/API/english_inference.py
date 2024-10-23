from faster_whisper import WhisperModel

def transcribe_english_audio(audio_path: str) -> str:
    # Load the faster-whisper English-specific model (medium.en)
    model = WhisperModel("medium.en", device="cuda", compute_type="float16")  # Use 'cpu' if no GPU available
    
    # Transcribe the audio file
    segments, info = model.transcribe(audio_path, language="en")  # Specify English language explicitly
    
    # Extract the full transcription text from segments
    full_text = ''.join([segment.text for segment in segments])

    return full_text

# # Example usage
# audio_file_path ="test.wav"
# english_text = transcribe_english_audio(audio_file_path)
# print(english_text)
