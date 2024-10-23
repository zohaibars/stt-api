from fastapi import FastAPI, Form
from utils import download_youtube_audio, get_large_audio_chunks_on_silence
from inference import transcribe_audio
import os
import shutil
import asyncio

# Define the FastAPI app
app = FastAPI()

# Create an asyncio lock
processing_lock = asyncio.Lock()

@app.post("/process-url/")
async def process_url(url: str = Form(...)):
    async with processing_lock:  # Ensure only one request is processed at a time
        # Download audio from YouTube
        audio_path = download_youtube_audio(url)
        # Get chunks of audio based on silence detection
        all_chunks_path = get_large_audio_chunks_on_silence(audio_path)
        # Remove the original audio file after processing
        os.remove(audio_path)
        
        text = []
        for audio in all_chunks_path:
            text.append(transcribe_audio(audio))
        
        # Clean up chunks directory
        shutil.rmtree("chunks")
        
        # Join all transcriptions into a single string
        return " ".join(text)

# Run the app with `uvicorn filename:app --reload`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
