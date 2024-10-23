import os
import wave

def process_subfolder(folder_name, subfolder_name, subfolder_path, sampling_rate_counts):
    """Process files within a subfolder and return the count of .wav files grouped by sampling rate."""
    wav_count = 0
    
    for file_name in os.listdir(subfolder_path):
        if file_name.endswith(".wav"):
            file_path = os.path.join(subfolder_path, file_name)
            with wave.open(file_path, 'r') as wav_file:
                sampling_rate = wav_file.getframerate()
            
            # Count the files by their sampling rate
            if sampling_rate in sampling_rate_counts:
                sampling_rate_counts[sampling_rate] += 1
            else:
                sampling_rate_counts[sampling_rate] = 1
            
            wav_count += 1

    return wav_count

def count_folders_and_wav_files_by_sampling_rate(dataset_path):
    """Traverse the dataset directory structure and count folders and .wav files by sampling rate."""
    total_folders = 0
    total_wav_files = 0
    sampling_rate_counts = {}

    for root, dirs, files in os.walk(dataset_path):
        # Get the relative folder structure
        relative_path = os.path.relpath(root, dataset_path)
        folder_parts = relative_path.split(os.sep)

        if len(folder_parts) == 1:  # Only the main folder
            folder_name = folder_parts[0]
            for subfolder in dirs:
                subfolder_path = os.path.join(root, subfolder)
                wav_count = process_subfolder(folder_name, subfolder, subfolder_path, sampling_rate_counts)
                total_folders += 1
                total_wav_files += wav_count
        else:
            # Handle deeper subfolder structures
            folder_name = folder_parts[-2]  # Parent folder
            subfolder_name = folder_parts[-1]  # Current folder
            wav_count = process_subfolder(folder_name, subfolder_name, root, sampling_rate_counts)
            total_folders += 1
            total_wav_files += wav_count

    return total_folders, total_wav_files, sampling_rate_counts

if __name__ == "__main__":
    dataset_path = os.path.join("/home/waqar/MWaqar/stt-api/Dataset", "Custom_dataset")
    
    total_folders, total_wav_files, sampling_rate_counts = count_folders_and_wav_files_by_sampling_rate(dataset_path)
    
    print(f"Total folders processed: {total_folders}")
    print(f"Total .wav files processed: {total_wav_files}")
    print("Sampling rate wise file counts:")
    for rate, count in sampling_rate_counts.items():
        print(f"Sampling Rate: {rate} Hz, Number of files: {count}")
