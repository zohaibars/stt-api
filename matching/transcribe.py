import os
import json
import difflib
from faster_whisper import WhisperModel
from utils import read_file,all_files

# Define the model size and load the model
model_size = "large-v2"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

transcribe_params = {
    "no_repeat_ngram_size": 2,
    "beam_size": 5,
    "condition_on_previous_text": False,
    "language": 'ur',
}

def tokenize(text):
    """Tokenize Urdu text into words."""
    return text.split()

def create_correction_dict(predicted, actual):
    """Create a dictionary of corrections from predicted to actual text."""
    predicted_words = tokenize(predicted)
    actual_words = tokenize(actual)
    
    matcher = difflib.SequenceMatcher(None, predicted_words, actual_words)
    
    corrections = {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace' or tag == 'delete':
            for i in range(i1, i2):
                p_word = predicted_words[i]
                if tag == 'replace':
                    for j in range(j1, j2):
                        a_word = actual_words[j]
                        corrections[p_word] = a_word
                elif tag == 'delete':
                    corrections[p_word] = "Missing in prediction"
        elif tag == 'insert':
            for j in range(j1, j2):
                a_word = actual_words[j]
                corrections["Missing in prediction"] = a_word
    
    # Handle extra words in prediction
    for i in range(len(predicted_words)):
        if predicted_words[i] not in corrections:
            corrections[predicted_words[i]] = "Extra word in prediction"
    
    return corrections

def save_to_json(data, file_path):
    """Save the dictionary to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    dataset_path = os.path.join("/home/waqar/MWaqar/stt-api/Dataset", "Custom_dataset")
    
    # Process the dataset and get all audio and text file paths
    all_audio_files, all_text_files = all_files(dataset_path)
    
    # Transcribe the audio file
    segments, info = model.transcribe(all_audio_files[1], **transcribe_params)
    segment_info = [{"start": segment.start, "end": segment.end, "text": segment.text} for segment in segments]
    full_text_urdu = ' '.join([segment["text"] for segment in segment_info])
    
    # Read the actual text from the file
    actual_text = read_file(all_text_files[1])
    
    # Create correction dictionary
    corrections = create_correction_dict(full_text_urdu, actual_text)
    
    # Save corrections to a JSON file
    output_json_path = 'corrections.json'
    save_to_json(corrections, output_json_path)
    
    print(f"Corrections have been saved to {output_json_path}")
