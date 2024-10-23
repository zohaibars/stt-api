from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import asyncio
import concurrent.futures
from utils import process_audio

transcription_router = APIRouter()

@transcription_router.post("/v1/audio/transcriptions")
async def transcribe_audio(file: UploadFile = Form(...), language: str = Form(...)):
    # Create a thread pool to handle the processing asynchronously
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: process_audio(file, language)
        )
    return result
