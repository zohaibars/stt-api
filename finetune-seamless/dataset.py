import os
import json
from sklearn.model_selection import train_test_split

def load_dataset(dataset_dir):
    # Initialize an empty list to store samples
    samples = []
    
    # Initialize counters
    id_counter = 1
    total_file_counter = 0
    folders_summary = {}  # To store the file count in each subfolder

    # Iterate through folders in the dataset directory (e.g., v1, v2)
    for folder in os.listdir(dataset_dir):
        folder_path = os.path.join(dataset_dir, folder)
        
        if os.path.isdir(folder_path):
            # Process each subfolder within the current folder
            for subfolder in os.listdir(folder_path):
                subfolder_path = os.path.join(folder_path, subfolder)
                
                if os.path.isdir(subfolder_path):
                    subfolder_file_counter = 0  # Counter for files in the current subfolder
                    
                    # Process all files within the subfolder
                    for file_name in os.listdir(subfolder_path):
                        file_path = os.path.join(subfolder_path, file_name)

                        # Check if it's a file
                        if os.path.isfile(file_path):
                            base_name, file_extension = os.path.splitext(file_name)

                            if file_extension == ".wav":
                                # Read audio content (assuming further processing is done later)
                                with open(file_path, 'rb') as audio_file:
                                    audio_content = audio_file.read()

                                # Read corresponding text file
                                text_file_path = os.path.join(subfolder_path, base_name + ".txt")
                                if os.path.isfile(text_file_path):
                                    with open(text_file_path, 'r', encoding='utf-8') as text_file:
                                        text_content = text_file.read().replace('\n', '')

                                    # Create sample entry
                                    sample = {
                                        "source": {
                                            "id": id_counter,
                                            "lang": "urd",
                                            "text": text_content,
                                            "audio_local_path": file_path,
                                            "waveform": None,
                                            "sampling_rate": 16000,
                                            "units": None
                                        },
                                        "target": {
                                            "id": id_counter,
                                            "lang": "urd",
                                            "text": text_content,
                                            "audio_local_path": file_path,
                                            "waveform": None,
                                            "sampling_rate": 16000,
                                            "units": None
                                        }
                                    }

                                    # Append the sample to the list
                                    samples.append(sample)
                                    id_counter += 1
                                    subfolder_file_counter += 1
                                    total_file_counter += 1
                    
                    # Store the number of files processed in this subfolder
                    folders_summary[subfolder] = subfolder_file_counter

    # Print summary of processing
    print(f"Total subfolders processed: {len(folders_summary)}")
    for subfolder, file_count in folders_summary.items():
        print(f"Subfolder: {subfolder}, Files processed: {file_count}")
    print(f"Total files processed: {total_file_counter}")

    return samples

def split_and_write_json(dataset_dir, output_dir, train_ratio=0.8):
    # Load dataset
    samples = load_dataset(dataset_dir)

    # Split dataset into training and validation sets
    train_samples, val_samples = train_test_split(samples, train_size=train_ratio, random_state=42)

    # Display the number of files
    total_files = len(samples)
    train_files = len(train_samples)
    val_files = len(val_samples)

    print(f"Total files: {total_files}")
    print(f"Training files: {train_files}")
    print(f"Validation files: {val_files}")

    # Write training samples to JSON
    train_json_path = os.path.join(output_dir, "train.json")
    with open(train_json_path, 'w', encoding='utf-8') as train_json_file:
        for sample in train_samples:
            json.dump(sample, train_json_file, ensure_ascii=False)
            train_json_file.write('\n')  # Add a newline to separate entries

    # Write validation samples to JSON
    val_json_path = os.path.join(output_dir, "validation.json")
    with open(val_json_path, 'w', encoding='utf-8') as val_json_file:
        for sample in val_samples:
            json.dump(sample, val_json_file, ensure_ascii=False)
            val_json_file.write('\n')  # Add a newline to separate entries


# Example usage
dataset_directory = "/home/waqar/MWaqar/stt-api/Dataset/Custom_dataset"
output_directory = dataset_directory
split_and_write_json(dataset_directory, output_directory)
