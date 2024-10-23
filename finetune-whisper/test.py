import torch
import librosa
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, GenerationConfig

# Device configuration
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Model path or ID
model_id = "/home/waqar/MWaqar/stt-api/finetune-whisper/New_Model"

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

# Debugging information
print("Suppress tokens:", model.config.suppress_tokens)
print("Decoder start token ID:", model.config.decoder_start_token_id)

# Create the pipeline
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device
)

# Path to the audio file
audio_path = "/home/waqar/MWaqar/stt-api/Dataset/Custom_dataset/30auguest/27auguesthamzaheadline/chunks_1.wav"

def transcribe_audio(pipe, audio_path):
    # Read and resample the audio file using librosa
    audio, original_sampling_rate = librosa.load(audio_path, sr=None)  # Load with original sampling rate
    target_sampling_rate = 16000
    
    if original_sampling_rate != target_sampling_rate:
        # Resample audio to target_sampling_rate
        audio = librosa.resample(audio, orig_sr=original_sampling_rate, target_sr=target_sampling_rate)
    
    # Process the audio file
    audio_features = processor(audio, sampling_rate=target_sampling_rate, return_tensors="pt", padding=True, truncation=True)
    
    # Extract input features and create attention mask
    input_features = audio_features["input_features"].to(device, dtype=torch_dtype)
    
    # Create attention mask if it's not provided
    attention_mask = audio_features.get("attention_mask")
    if attention_mask is None:
        attention_mask = torch.ones(input_features.shape, device=device, dtype=torch_dtype)
    
    # Set generation configuration with reduced max_new_tokens
    generation_config = GenerationConfig(
        max_new_tokens=300  # Adjust this value to ensure it fits within the model's limits
    )
    
    # Perform inference
    with torch.no_grad():
        result = pipe.model.generate(
            input_features=input_features,
            attention_mask=attention_mask,
            generation_config=generation_config
        )
    
    # Decode result
    transcription = processor.batch_decode(result, skip_special_tokens=True)
    
    # Post-process if necessary
    transcription = [t.strip() for t in transcription if t.strip()]
    
    return transcription

# Run the transcription
try:
    transcription = transcribe_audio(pipe, audio_path)
    print("Transcription:", transcription[0])
except Exception as e:
    print("Error during transcription:", str(e))
