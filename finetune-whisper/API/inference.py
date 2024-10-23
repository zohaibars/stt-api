import torch
import librosa
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, GenerationConfig
import time  # Import time module for timing

# Device configuration
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Model path or ID
model_id = "65_hour"

# Load the model
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, 
    torch_dtype=torch_dtype, 
    low_cpu_mem_usage=True, 
    use_safetensors=True,
    ignore_mismatched_sizes=True
)
model.to(device)

# Load the processor
processor = AutoProcessor.from_pretrained(model_id)

# Ensure suppress_tokens is set correctly
if model.config.suppress_tokens is None or len(model.config.suppress_tokens) == 0:
    model.config.suppress_tokens = [
        processor.tokenizer.pad_token_id, 
        processor.tokenizer.eos_token_id
    ]

# Create the pipeline
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device
)

def transcribe_audio(audio_path):
    # Start measuring time for loading the audio
    # start_time = time.time()
    # 
    # Load the audio file using librosa without resampling
    audio, original_sampling_rate = librosa.load(audio_path, sr=None)

    # End timing for loading the audio
    # end_time = time.time()
    # print(f"Time taken to load audio: {end_time - start_time:.2f} seconds")
    
    # Start measuring time for model inference
    start_inference_time = time.time()

    # Process the entire audio file
    audio_features = processor(audio, sampling_rate=original_sampling_rate, return_tensors="pt", padding=True, truncation=True)
    
    # Extract input features and create attention mask
    input_features = audio_features["input_features"].to(device, dtype=torch_dtype)
    attention_mask = audio_features.get("attention_mask", torch.ones(input_features.shape, device=device, dtype=torch_dtype))
    
    # Set generation configuration
    generation_config = GenerationConfig(max_new_tokens=300)  # Adjust max_new_tokens if necessary
    
    # Perform inference
    with torch.no_grad():
        result = pipe.model.generate(
            input_features=input_features,
            attention_mask=attention_mask,
            generation_config=generation_config
        )
    
    # End timing for inference
    end_inference_time = time.time()
    # print(f"Time taken for model inference: {end_inference_time - start_inference_time:.2f} seconds")
    
    # Decode and join the transcription
    transcription = processor.batch_decode(result, skip_special_tokens=True)
    joined_transcription = ''.join([t.strip() for t in transcription if t.strip()])
    
    return joined_transcription

# Example usage
# audio_path = "path/to/your/audio/file.wav"  # Replace with your audio file path
# try:
#     transcription = transcribe_audio(audio_path)
#     print("Transcription:", transcription)
# except Exception as e:
#     print("Error during transcription:", str(e))
