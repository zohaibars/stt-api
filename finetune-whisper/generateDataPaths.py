import os

def read_file(file_path):
    """Read the contents of a file and return it as a single line."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()  # Remove leading/trailing whitespace
    return content.replace('\n', ' ')  # Replace all newlines with spaces to keep the text in a single line

def process_subfolder(folder_name, subfolder_name, subfolder_path, audio_path_fp, text_fp, mismatch_fp):
    """Process files within a subfolder and write unique audio paths and transcripts to the output files."""
    audio_written = False
    text_written = False
    audio_count = 0  # Counter for audio files in the current folder
    mismatch_count = 0  # Counter for mismatched audio and text files
    
    for file_name in os.listdir(subfolder_path):
        file_path = os.path.join(subfolder_path, file_name)

        if file_name.endswith(".wav"):
            # Create a unique utt_id by combining the folder name, subfolder name, and file name
            utt_id = f"{folder_name}_{subfolder_name}_{file_name.split('.')[0]}"
            text_file_path = os.path.join(subfolder_path, f"{file_name.split('.')[0]}.txt")
            
            if os.path.exists(text_file_path):
                transcript = read_file(text_file_path)
                
                if transcript:  # Only write if transcript is not empty
                    text_fp.write(f"{utt_id} {transcript}\n")
                    audio_path_fp.write(f"{utt_id} {file_path}\n")
                    
                    text_written = True
                    audio_written = True
                    mismatch_fp.write(f"{utt_id}: True\n")
                    audio_count += 1  # Increment audio file counter
            else:
                # Mark as mismatch if the corresponding text file is missing
                mismatch_fp.write(f"{utt_id}: Cross\n")
                mismatch_count += 1

    if audio_written and text_written:
        print(f"Processed folder: {subfolder_path}, Audio files: {audio_count}, Mismatches: {mismatch_count}")
    
    return audio_count, mismatch_count  # Return the number of audio files and mismatches in this subfolder

def create_dataset(dataset_path, output_path):
    """Traverse the dataset directory structure and process each subfolder recursively."""
    audio_path_file = os.path.join(output_path, "audio_paths")
    text_file = os.path.join(output_path, "text")
    mismatch_file = os.path.join(output_path, "mismatch_report")

    total_folders = 0  # Counter for total folders
    total_audio_files = 0  # Counter for total audio files
    total_mismatches = 0  # Counter for total mismatches

    with open(audio_path_file, 'w', encoding='utf-8') as audio_path_fp, \
         open(text_file, 'w', encoding='utf-8') as text_fp, \
         open(mismatch_file, 'w', encoding='utf-8') as mismatch_fp:

        # Process folders and subfolders recursively
        for root, dirs, files in os.walk(dataset_path):
            # Get the relative folder structure to construct utt_id
            relative_path = os.path.relpath(root, dataset_path)
            folder_parts = relative_path.split(os.sep)

            if len(folder_parts) == 1:  # Only the main folder
                folder_name = folder_parts[0]
                for subfolder in dirs:
                    subfolder_path = os.path.join(root, subfolder)
                    audio_count, mismatch_count = process_subfolder(folder_name, subfolder, subfolder_path, audio_path_fp, text_fp, mismatch_fp)
                    total_folders += 1
                    total_audio_files += audio_count
                    total_mismatches += mismatch_count
            else:
                # Handle deeper subfolder structures
                folder_name = folder_parts[-2]  # Parent folder
                subfolder_name = folder_parts[-1]  # Current folder
                audio_count, mismatch_count = process_subfolder(folder_name, subfolder_name, root, audio_path_fp, text_fp, mismatch_fp)
                total_folders += 1
                total_audio_files += audio_count
                total_mismatches += mismatch_count

    print(f"Total folders processed: {total_folders}")
    print(f"Total audio files processed: {total_audio_files}")
    print(f"Total mismatches: {total_mismatches}")

if __name__ == "__main__":
    dataset_path = os.path.join("/home/waqar/MWaqar/stt-api/Dataset", "Custom_dataset")
    output_path = "/home/waqar/MWaqar/stt-api/Dataset"
    
    create_dataset(dataset_path, output_path)
