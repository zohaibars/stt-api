from faster_whisper import WhisperModel

# Define the model size and load the model
model_size = "large-v2"
model = WhisperModel(model_size, device="cuda", compute_type="float16")
