import os
import shutil

def copy_finetune_checkpoint_files_to_destination(source_path="finetune", checkpoint_path="checkpoint-56172", destination_folder="65_hour"):
    """
    Copies specific finetuning and checkpoint-related files from the source and checkpoint paths
    to the destination folder. If the destination folder exists, it will be replaced.
    
    :param source_path: Directory containing finetuning files (default: 'finetune').
    :param checkpoint_path: Directory containing checkpoint files (default: 'checkpoint-68100').
    :param destination_folder: Folder where files will be copied (default: '22_hour').
    """
    
    # Remove the destination folder if it exists
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
    
    # Create the destination folder
    os.makedirs(destination_folder)

    checkpoint_path = os.path.join(source_path, checkpoint_path)

    # List of files to copy
    source_files = [
        f"{source_path}/added_tokens.json",
        f"{source_path}/normalizer.json",
        f"{source_path}/preprocessor_config.json",
        f"{source_path}/special_tokens_map.json",
        f"{source_path}/tokenizer_config.json",
        f"{source_path}/merges.txt",
        f"{source_path}/vocab.json",
        f"{checkpoint_path}/config.json",
        f"{checkpoint_path}/model-00001-of-00002.safetensors",
        f"{checkpoint_path}/model-00002-of-00002.safetensors",
        f"{checkpoint_path}/model.safetensors.index.json",
        f"{checkpoint_path}/training_args.bin",
    ]

    # Copy files to the destination folder
    for file_path in source_files:
        if os.path.exists(file_path):
            shutil.copy(file_path, destination_folder)
        else:
            print(f"Warning: File not found - {file_path}")

# Example usage
copy_finetune_checkpoint_files_to_destination()
