from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
import time
import os
import uuid
import asyncio

app = FastAPI()

# Ensure the 'chunks' directory exists
os.makedirs("chunks", exist_ok=True)

# Load the Faster Whisper model
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

def extract_audio_from_video(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".wav")
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path

def transcribe(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, beam_size=5)
    transcription = "".join([segment.text for segment in segments])
    return transcription

async def process_video(video_file: UploadFile) -> str:
    unique_id = uuid.uuid4().hex
    video_path = f"chunks/{unique_id}_{video_file.filename}"
    
    # Save the video file
    with open(video_path, "wb") as f:
        f.write(await video_file.read())
    
    # Extract audio and transcribe
    audio_path = extract_audio_from_video(video_path)
    transcription = transcribe(audio_path)
    
    # Clean up temporary files
    os.remove(video_path)
    os.remove(audio_path)
    
    return transcription

@app.post("/benchmark/")
async def benchmark(
    video_file: UploadFile = File(...),
    num_requests: int = 10
):
    if not video_file:
        raise HTTPException(status_code=400, detail="No video file provided.")
    
    start_time = time.time()

    # Create tasks for processing multiple requests concurrently
    tasks = [process_video(video_file) for _ in range(num_requests)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    avg_time_per_request = total_time / num_requests

    return {
        "total_time": total_time,
        "average_time_per_request": avg_time_per_request,
        "throughput": num_requests / total_time,
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
