import os

def read_file(file_path):
    """Read the contents of a file and return it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
    return content

def process_subfolder(subfolder_path):
    """Process files within a subfolder and return the list of audio and text files."""
    audio_files = []
    text_files = []
    
    # Loop through the files in the subfolder
    for file_name in os.listdir(subfolder_path):
        file_path = os.path.join(subfolder_path, file_name)
        
        # If it's a WAV audio file
        if file_name.endswith(".wav"):
            audio_files.append(file_path)
            
            # Check if the corresponding text file exists
            text_file_path = os.path.join(subfolder_path, f"{file_name.split('.')[0]}.txt")
            if os.path.exists(text_file_path):
                text_files.append(text_file_path)
    
    # Return the list of audio and text files for this subfolder
    return audio_files, text_files

def all_files(dataset_path):
    """Traverse the dataset directory structure and process each subfolder."""
    all_audio_files = []
    all_text_files = []
    
    # Loop through each folder in the dataset
    for folder in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder)
        
        if os.path.isdir(folder_path):
            for subfolder in os.listdir(folder_path):
                subfolder_path = os.path.join(folder_path, subfolder)
                
                if os.path.isdir(subfolder_path):
                    # Process each subfolder to get audio and text files
                    audio_files, text_files = process_subfolder(subfolder_path)
                    
                    # Print the length of audio and text files for the subfolder
                    # print(f"Processed folder: {subfolder_path}")
                    # print(f"Number of audio files: {len(audio_files)}")
                    # print(f"Number of text files: {len(text_files)}\n")
                    
                    # Add to the final list of all audio and text files
                    all_audio_files.extend(audio_files)
                    all_text_files.extend(text_files)
    
    # Return all audio and text file paths
    return all_audio_files, all_text_files

# if __name__ == "__main__":
#     dataset_path = os.path.join("/home/waqar/MWaqar/stt-api/Dataset", "Custom_dataset")
    
#     # Process the dataset and get all audio and text file paths
#     all_audio_files, all_text_files = all_files(dataset_path)
#     # print(all_audio_files)
#     # Print the final counts of all audio and text files
#     print(f"Total number of audio files: {len(all_audio_files)}")
#     print(f"Total number of text files: {len(all_text_files)}")
