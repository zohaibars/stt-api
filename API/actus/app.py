from fastapi import FastAPI
from routes import transcription_router

app = FastAPI()

# Include the router from routes.py
app.include_router(transcription_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
