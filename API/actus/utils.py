import os
from models import model
from fastapi.responses import FileResponse
from fastapi import UploadFile
# Define the directory for audio uploads
upload_dir = "audio_uploads"
os.makedirs(upload_dir, exist_ok=True)

def process_audio(audio_file: UploadFile, language: str):
    try:
        # Read the uploaded audio file into memory
        audio_content = audio_file.file.read()
        audio_name = os.path.splitext(audio_file.filename)[0]
        
        # Save the uploaded audio in the upload folder
        audio_file_path = os.path.join(upload_dir, f"{audio_name}.mp3")
        with open(audio_file_path, "wb") as temp_audio_file:
            temp_audio_file.write(audio_content)

        # Language selection
        language = language.lower()
        if language == "english":
            lang = 'en'
        elif language == "urdu":
            lang = 'ur'
        else:
            return {"error": "Unsupported language"}

        # Perform transcription
        segments, info = model.transcribe(audio_file_path, beam_size=5, language=lang)

        # Generate SRT file content
        srt_content = ""
        for i, segment in enumerate(segments, 1):
            start_time = segment.start
            end_time = segment.end
            text = segment.text

            # Convert start and end times to the SRT format
            start_time_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{start_time % 60:06.3f}"
            end_time_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{end_time % 60:06.3f}"

            srt_content += f"{i}\n"
            srt_content += f"{start_time_str} --> {end_time_str}\n"
            srt_content += f"{text}\n\n"

        # Save the SRT content to a file
        srt_file_path = os.path.join(upload_dir, f"{audio_name}.srt")
        with open(srt_file_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(srt_content)

        # Clean up the audio file
        os.remove(audio_file_path)

        # Return the SRT file as a response
        return FileResponse(srt_file_path, filename=f'{audio_name}.srt')

    except Exception as e:
        return {"error": str(e)}
