import os

def process_subfolder(subfolder_path):
    """Process files within a subfolder and return the counts of .wav and .txt files."""
    wav_count = 0
    txt_count = 0
    
    for file_name in os.listdir(subfolder_path):
        if file_name.endswith(".wav"):
            wav_count += 1
        elif file_name.endswith(".txt"):
            txt_count += 1

    return wav_count, txt_count

def count_folders_and_files(dataset_path):
    """Traverse the dataset directory structure and count folders and .wav and .txt files."""
    total_folders = 0
    total_wav_files = 0
    total_txt_files = 0
    folder_file_info = {}  # Dictionary to store file counts per folder

    for root, dirs, files in os.walk(dataset_path):
        # Get the relative folder structure
        relative_path = os.path.relpath(root, dataset_path)
        folder_parts = relative_path.split(os.sep)

        if len(folder_parts) == 1:  # Only the main folder
            parent_folder = folder_parts[0]
            for subfolder in dirs:
                subfolder_path = os.path.join(root, subfolder)
                wav_count, txt_count = process_subfolder(subfolder_path)
                total_folders += 1
                total_wav_files += wav_count
                total_txt_files += txt_count
                folder_file_info[f"{parent_folder}/{subfolder}"] = {
                    'wav_count': wav_count,
                    'txt_count': txt_count
                }
        else:
            # Handle deeper subfolder structures
            parent_folder = folder_parts[-2]  # Parent folder
            subfolder_name = folder_parts[-1]  # Current folder
            wav_count, txt_count = process_subfolder(root)
            total_folders += 1
            total_wav_files += wav_count
            total_txt_files += txt_count
            folder_file_info[f"{parent_folder}/{subfolder_name}"] = {
                'wav_count': wav_count,
                'txt_count': txt_count
            }

    return total_folders, total_wav_files, total_txt_files, folder_file_info

def mark_correctness(wav_count, txt_count):
    """Determine correctness based on counts and return corresponding mark."""
    if wav_count == 0 and txt_count == 0:
        return "❌"  # Both counts are zero
    elif txt_count > wav_count and txt_count > 0:
        return "❌"  # More text files than audio files
    elif wav_count > 0 and txt_count == 0:
        return "❌"  # Audio files exist but no text files
    elif wav_count > 0 and txt_count <= wav_count:
        return "✔️"  # Audio files exist and are greater than or equal to text files
    else:
        return "❌"  # Any other case

if __name__ == "__main__":
    dataset_path = os.path.join("/home/waqar/MWaqar/stt-api/Dataset", "Custom_dataset")
    
    total_folders, total_wav_files, total_txt_files, folder_file_info = count_folders_and_files(dataset_path)
    
    print(f"Total folders processed: {total_folders}")
    print(f"Total .wav files processed: {total_wav_files}")
    print(f"Total .txt files processed: {total_txt_files}")
    
    # Print the file count for each folder with marks
    print("\nFolder-wise file counts:")
    for folder, files in folder_file_info.items():
        wav_count = files['wav_count']
        txt_count = files['txt_count']
        mark = mark_correctness(wav_count, txt_count)
        print(f"Folder: {folder}, .wav files: {wav_count}, .txt files: {txt_count} {mark}")
