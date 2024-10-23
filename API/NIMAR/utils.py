import magic
def is_audio_or_video(file_path):
    audio_extensions = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'wma', 'm4a', 'opus']
    video_extensions = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'mpeg', 'mpg', 'ts']
    file_extension = file_path.split('.')[-1].lower()
    if file_extension in audio_extensions or file_extension in video_extensions:
        return True

    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path).split('/')[0]
    return file_type in ["audio", "video"]