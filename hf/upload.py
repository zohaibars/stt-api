import os
from datasets import Dataset, Features, Value, Audio
from huggingface_hub import HfApi

def load_data_from_directory(root_dir):
    data = {'audio': [], 'label': []}
    for subdir, dirs, files in os.walk(root_dir):
        print(f"Processing directory: {subdir}")
        
        for dir_name in dirs:
            print(f"  Subfolder: {os.path.join(subdir, dir_name)}")
        
        for file_name in files:
            if file_name.endswith('.wav'):
                # Construct the corresponding text file path
                txt_file_path = os.path.join(subdir, file_name.replace('.wav', '.txt'))
                
                if os.path.exists(txt_file_path):
                    with open(txt_file_path, 'r') as txt_file:
                        label = txt_file.read().strip()
                    
                    # Append the data
                    wav_file_path = os.path.join(subdir, file_name)
                    data['audio'].append(wav_file_path)
                    data['label'].append(label)
    return data

def create_dataset(data):
    # Define features
    features = Features({
        'audio': Audio(),
        'label': Value(dtype='string')
    })
    
    return Dataset.from_dict(data, features=features)

def main():
    # Define the root directory of your dataset
    data_dir = '/home/waqar/MWaqar/Dataset'
    
    # Load the data
    data = load_data_from_directory(data_dir)
    
    # Create the dataset
    dataset = create_dataset(data)
    
    # Define the repository ID of the existing dataset
    repo_id = 'forbmax-ai/STTUrdu'
    
    # Push new data to the existing dataset on Hugging Face Hub
    dataset.push_to_hub(repo_id, commit_message="Added new data to the dataset")

if __name__ == "__main__":
    main()
