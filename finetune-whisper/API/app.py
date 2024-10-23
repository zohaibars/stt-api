import os
import shutil
import logging
import time
import torch
import aiofiles
import asyncio
from fastapi import FastAPI, UploadFile, Depends, HTTPException, Header
from utils import convert_audio_to_16000, get_file_size, format_size, get_file_duration
from chunking import extract_audio_from_video, split_audio_into_chunks
from inference import transcribe_audio
from english_inference import transcribe_english_audio

app = FastAPI()

# Configure logging to file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("formedia.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Define a directory to store uploaded videos and audio
upload_dir = "formedia_uploads"
if os.path.exists(upload_dir):
    shutil.rmtree(upload_dir)
os.makedirs(upload_dir, exist_ok=True)

user_api_keys = {
    "user1": "apikey1",
    "user2": "apikey2",
    # Add more users and their API keys as needed
}

# Create a semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(4)  # Limit to 4 concurrent requests

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

        # Check if the file is a video
        if any(file_path.lower().endswith(ext) for ext in video_extensions):
            audio_file_path = os.path.join(file_folder, f"{original_file_name}.wav")
            # Extract audio from video using FFmpeg (faster than moviepy)
            await extract_audio_from_video(file_path, audio_file_path)
            if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
                raise HTTPException(status_code=500, detail="No audio found in the provided video.")
        else:
            audio_file_path = convert_audio_to_16000(file_path, file_path)

        # Log file size and duration
        file_size = get_file_size(file_path)
        readable_size = format_size(file_size)
        file_duration = get_file_duration(file_path)
        duration_str = f"{file_duration:.2f}s"
        logger.info(f"Uploaded file: {original_file_name}, Size: {readable_size}, Duration: {duration_str}")

        # Split audio into chunks
        all_chunks = await split_audio_into_chunks(audio_path=audio_file_path, output_folder=os.path.join(file_folder, "Chunks"))

        segment_info = []
        full_text_urdu = ''
        full_text_english = ''

        # Process each audio chunk based on language
        for chunk in all_chunks:
            try:
                start_time = chunk["start"]
                end_time = chunk["end"]
                chunk_path = chunk["chunk_path"]

                if language == "ur":
                    text = transcribe_audio(chunk_path)  # Using Urdu model
                    if full_text_urdu:
                        last_word_urdu = full_text_urdu.split()[-1]
                        first_word_urdu = text.split()[0]
                        if last_word_urdu == first_word_urdu:
                            text = " ".join(text.split()[1:])  # Remove the first word from the current chunk
                    full_text_urdu = (full_text_urdu + " " + text).strip()

                else:
                    text = transcribe_english_audio(chunk_path)  # Using English model
                    if full_text_english:
                        last_word_english = full_text_english.split()[-1]
                        first_word_english = text.split()[0]
                        if last_word_english == first_word_english:
                            text = " ".join(text.split()[1:])  # Remove the first word from the current chunk
                    full_text_english = (full_text_english + " " + text).strip()

                # Create segment info
                segment_info.append({
                    "start": start_time,
                    "end": end_time,
                    "text": text
                })

            except Exception as chunk_error:
                # Log the error and continue processing the next chunk
                logger.error(f"Error processing chunk {chunk_path}: {str(chunk_error)}")
                continue

        # Clean up files
        shutil.rmtree(file_folder, ignore_errors=True)
        # Clear PyTorch GPU cache to free up memory (model remains loaded)
        torch.cuda.empty_cache()

        return {
            "urdu_full_text": full_text_urdu if language == "ur" else None,
            "english_full_text": full_text_english if language == "en" else None,
            "Timestamp": segment_info
        }

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

news_type_list = ["live"]

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
    logger.info(f"Received request for transcribe_video with file: {video_file.filename}")
    
    async with semaphore:  # Limit concurrent requests
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
    uvicorn.run(app, host="0.0.0.0", port=2000)
