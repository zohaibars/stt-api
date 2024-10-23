import requests
import concurrent.futures
import time

# Replace these values with actual test values
api_url = "http://localhost:3000"
api_key = "apikey1"  # Use a valid API key from user_api_keys
language = "urdu"  # or "english"
news_type = "live"  # or "dataset", "report"
file_path = "clip.mp4"  # Provide path to a test video file

def test_transcribe_video(file_path):
    start_time = time.time()
    with open(file_path, 'rb') as video_file:
        files = {'video_file': video_file}
        headers = {
            'api_key': api_key,
            'language': language,
            'news_type': news_type
        }
        response = requests.post(f"{api_url}/transcribe_video/", files=files, headers=headers)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    if response.status_code == 200:
        print(f"Transcribe Video Check Passed in {elapsed_time:.2f} seconds:", response.json())
    else:
        print(f"Transcribe Video Check Failed in {elapsed_time:.2f} seconds:", response.status_code, response.text)

def send_requests():
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_transcribe_video, file_path) for _ in range(10)]
        concurrent.futures.wait(futures)
    end_time = time.time()
    
    total_elapsed_time = end_time - start_time
    print(f"Total time for sending requests: {total_elapsed_time:.2f} seconds")

if __name__ == "__main__":
    while True:
        send_requests()
        time.sleep(60)  # Wait for 1 minute before sending the requests again
