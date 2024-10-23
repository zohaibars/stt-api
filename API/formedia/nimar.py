import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import shutil
import logging
import asyncio
import time
import aiofiles

from fastapi import FastAPI, UploadFile, Depends, HTTPException, Header
from faster_whisper import WhisperModel
import torch
import re  # To help with text cleanup
from utils import *
app = FastAPI()

model_size = "large-v2"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

# Configure logging to file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("nimar.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Define a directory to store uploaded videos and audio
upload_dir = "nimar_uploads"
if os.path.exists(upload_dir):
    shutil.rmtree(upload_dir)
os.makedirs(upload_dir, exist_ok=True)

user_api_keys = {
    "user1": "apikey1",
    "user2": "apikey2",
    # Add more users and their API keys as needed
}

# Semaphore to limit concurrent requests to 4
semaphore = asyncio.Semaphore(4)

async def process_video(file: UploadFile, news_type: str = None, language: str = None):
    try:
        original_file_name = file.filename
        file_folder = os.path.join(upload_dir, original_file_name)
        os.makedirs(file_folder, exist_ok=True)
        file_path = os.path.join(file_folder, original_file_name)

        # Asynchronously read and write the file
        async with aiofiles.open(file_path, "wb") as temp_file:
            file_content = await file.read()
            await temp_file.write(file_content)

        # Video extensions list
        video_extensions = [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv"]
        # Log the file size after saving the file
        file_size = get_file_size(file_path)
        readable_size = format_size(file_size)
        logger.info(f"Uploaded file: {original_file_name}, Size: {readable_size}")

        # Check if the file is a video
        if any(file_path.lower().endswith(ext) for ext in video_extensions):
            audio_file_path = os.path.join(file_folder, f"{original_file_name}.wav")
            # Extract audio from video using FFmpeg (faster than moviepy)
            await extract_audio_with_ffmpeg(file_path, audio_file_path)
        else:
            audio_file_path = file_path

        # Transcription logic
        transcribe_params = {
            "no_repeat_ngram_size": 2,
            "beam_size": 5,
            "condition_on_previous_text": False,
            "language": language,
        }

        if news_type == "live":
            segments, info = model.transcribe(audio_file_path, **transcribe_params)
            if language == "ur":
                segment_info = [{"start": segment.start, "end": segment.end, "text": segment.text} for segment in segments]
                full_text_urdu = ''.join([segment["text"] for segment in segment_info])
                # Remove Hindi text if present in Urdu transcription
                full_text_urdu = remove_hindi_text(full_text_urdu)
                full_text_english = ""
            else:
                full_text_urdu = ""
                segment_info = [{"start": segment.start, "end": segment.end, "text": segment.text} for segment in segments]
                full_text_english = ''.join([segment["text"] for segment in segment_info])
        else:
            transcribe_params_report = transcribe_params.copy()
            transcribe_params_report["task"] = "translate"
            segments, info = model.transcribe(audio_file_path, **transcribe_params_report)
            segment_info = [{"start": segment.start, "end": segment.end, "text": segment.text} for segment in segments]
            full_text_english = ''.join([segment["text"] for segment in segment_info])
            full_text_urdu = ""

        # Merge segments into larger chunks (if needed)
        merged_segments = merge_segments(segment_info, max_length=3)

        # Clean up files
        shutil.rmtree(file_folder, ignore_errors=True)

        # Clear PyTorch GPU cache to free up memory (model remains loaded)
        torch.cuda.empty_cache()

        return {"urdu_full_text": full_text_urdu, "english_full_text": full_text_english, "Timestamp": merged_segments}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return {"error": f"Internal Error {str(e)}"}

async def get_api_key(api_key: str = Header(None, convert_underscores=False)):
    if api_key not in user_api_keys.values():
        logger.warning("Invalid API key access attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

language_list = {
    "english": "en",
    "urdu": "ur",
}

async def get_language_key(language: str = Header(None, convert_underscores=False)):
    if language.lower() not in language_list.keys():
        raise HTTPException(status_code=401, detail="Invalid language")
    return language_list[language.lower()]

news_type_list = ["live", "dataset", "report"]

async def get_news_type(news_type: str = Header(None, convert_underscores=False)):
    if news_type.lower() not in news_type_list:
        raise HTTPException(status_code=401, detail="Invalid news_type value")
    return news_type.lower()

@app.post("/transcribe_video/")
async def transcribe_video_endpoint(
    video_file: UploadFile,
    api_key: str = Depends(get_api_key),
    news_type: str = Depends(get_news_type),
    language: str = Depends(get_language_key)
):
    async with semaphore:
        logger.info(f"Received request for transcribe_video with file: {video_file.filename}")
        
        start_time = time.time()  # Record the start time
        
        result = await process_video(video_file, news_type, language)
        
        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time  # Calculate the time difference
        
        # Log the time taken for the request along with the filename
        logger.info(f"Processed file: {video_file.filename} in {time_taken:.2f} seconds")
        
        return result


@app.get("/live")
async def live_check():
    logger.info("Live status endpoint accessed")
    return {"live": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2001)
