import os

def list_text_files(base_directory):
    """List text files with 2 or fewer words and files containing newline characters."""
    files_with_two_or_fewer_words = []
    files_with_newline = []

    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".txt"):  # Process only text files
                text_file_path = os.path.join(root, file)

                with open(text_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check if file contains newline characters
                    if '\n' in content:
                        files_with_newline.append(text_file_path)

                    # Split content by spaces to check the word count
                    words = content.split()
                    
                    if len(words) <= 2:  # If the file has 2 or fewer words
                        files_with_two_or_fewer_words.append(text_file_path)

    return files_with_two_or_fewer_words, files_with_newline
# Specify the root directory where you want to start checking
root_directory = "/home/waqar/MWaqar/stt-api/Dataset/Custom_dataset"

# Call the function and get the paths of text files with word count not equal to two
files_with_two_or_fewer_words, files_with_newline = list_text_files(root_directory)

# Print the results
if files_with_two_or_fewer_words:
    print("Text files with 2 or fewer words:")
    for file_path in files_with_two_or_fewer_words:
        print(file_path)
else:
    print("No text files found with 2 or fewer words.")

if files_with_newline:
    print("\nText files containing newline characters:")
    for file_path in files_with_newline:
        print(file_path)
else:
    print("No text files found with newline characters.")

def delete_files(file_list):
    """Delete text files and their corresponding .wav files based on the provided file list."""
    for text_file_path in file_list:
        wav_file_path = text_file_path.replace(".txt", ".wav")

        # Delete the text file
        if os.path.exists(text_file_path):
            print(f"Deleting text file: {text_file_path}")
            os.remove(text_file_path)

        # Delete the corresponding .wav file
        if os.path.exists(wav_file_path):
            print(f"Deleting corresponding audio file: {wav_file_path}")
            os.remove(wav_file_path)

delete_files(files_with_two_or_fewer_words)
delete_files(files_with_newline)