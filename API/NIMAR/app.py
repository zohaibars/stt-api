import os
import concurrent.futures
import asyncio
import logging
from utils import is_audio_or_video
from fastapi import FastAPI, UploadFile, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from langdetect import detect
from transcribe import STT_Job
from translation import translate
import shutil
from summarize import summarize
app = FastAPI()

# Configure logging to file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("STTapp.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

user_api_keys = {
    "user1": "apikey1",
    "user2": "apikey2",
}

upload_dir = "uploads"
if os.path.exists(upload_dir):
    shutil.rmtree(upload_dir)
os.makedirs(upload_dir, exist_ok=True)

# Semaphore to limit concurrent jobs
semaphore = asyncio.Semaphore(2)

async def process_file(file: UploadFile, ID: str = None):
    response_data = {}
    file_path = None
    try:
        file_content = file.file.read()
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as temp_file:
            temp_file.write(file_content)
        print(file_path)
        if is_audio_or_video(file_path):
            Original_Text = STT_Job(file_path=file_path)
            # print(Original_Text)           
            Translated_Text = translate(Original_Text)
            print(Original_Text)
            print(Translated_Text)
            summary=summarize(Original_Text)
            # print(summary)
            response_data["ID"] = ID
            source_language = detect(Original_Text)
          
            if source_language == "ur":

                OriginalTextSummary = summary.get("Urdu_summary","Summary not found")
                TranslationTextSummary =summary.get("English_summary","Summary not found")
                response_data["UrduText"] = Original_Text
                response_data["EnglishText"] = Translated_Text
                response_data["UrduTextSummary"] = OriginalTextSummary
                response_data["EnglishTextSummary"] = TranslationTextSummary
            else:
                TranslationTextSummary = summary.get("Urdu_summary","Summary not found")
                OriginalTextSummary =summary.get("English_summary","Summary not found")
                response_data["EnglishText"] = Original_Text
                response_data["UrduText"] = Translated_Text
                response_data["EnglishTextSummary"] = OriginalTextSummary
                response_data["UrduTextSummary"] = TranslationTextSummary
            # print("response_data", response_data)
            return response_data

        else:
            response_data = {"error": "Unsupported Format"}

    except FileNotFoundError:
        response_data = {"error": "File not supported"}

    except OSError as e:
        if "No space left on device" in str(e):
            response_data = {"error": "No disk space left."}
        elif "CUDA out of memory" in str(e):
            response_data = {"error": "CUDA out of memory."}
        else:
            response_data = {"error": "OS ERROR"}

    except Exception as e:
        if "object does not support item assignment" in str(e):
            response_data = {"error": "Unsupported Format"}
        elif "object has no attribute 'seek'" in str(e):
            response_data = {"error": "Unsupported Format"}
        else:
            response_data = {"error": "Error processing file." + str(e)}

    finally:
        if file_path:
            try:
                os.remove(file_path)
            except Exception as e:
                response_data = {"error": "File delete error"}

    return JSONResponse(content=response_data, status_code=500)

async def get_api_key(api_key: str = Header(None, convert_underscores=False)):
    if api_key not in user_api_keys.values():
        logger.warning("Invalid API key access attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.post("/STTNode/")
async def STTNode_endpoint(
    file: UploadFile,
    api_key: str = Depends(get_api_key),
    ID: str = Query(None, title="Optional ID parameter", description="Optional ID parameter for processing"),
):
    logger.info(f"Received request for STTNode with file: {file.filename}")
    async with semaphore:
        result = await process_file(file, ID)
    return result

@app.get("/live")
async def live_check():
    logger.info("Live status endpoint accessed")
    return {"live": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
    # run command in cmd 
    # uvicorn app:app --host 0.0.0.0 --port 3000 --reload
