import os
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# Replace 'path/to/your/service-account-file.json' with your service account file
SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-file.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Authenticate and construct the service
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# Replace with your folder ID
FOLDER_ID = '1WpDZlmorZw0S7ImtP9iIXcE3GfnNAwn4'

def download_file(file_id, file_name, folder_path):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(folder_path, file_name), mode='wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Downloaded {file_name} {int(status.progress() * 100)}%.")

def list_files_in_folder(folder_id, parent_folder_path):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)",
        spaces='drive'
    ).execute()
    items = results.get('files', [])

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # If item is a folder, create a new directory and list its contents
            new_folder_path = os.path.join(parent_folder_path, item['name'])
            os.makedirs(new_folder_path, exist_ok=True)
            list_files_in_folder(item['id'], new_folder_path)
        else:
            # If item is a file, download it
            download_file(item['id'], item['name'], parent_folder_path)

# Create the base folder where all files will be downloaded
base_folder_path = 'downloaded_files'
os.makedirs(base_folder_path, exist_ok=True)

# Start listing files from the root folder
list_files_in_folder(FOLDER_ID, base_folder_path)
