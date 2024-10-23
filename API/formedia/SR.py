import requests
import json

# Replace these values with actual test values
API_URL = "http://192.168.18.164:8011/"

def speaker_recognition(file_path):
    """
    Sends a video file to the speaker recognition API and prints the person's name.

    Args:
        file_path (str): Path to the video file.
    """
    try:
        with open(file_path, 'rb') as video_file:
            files = {'video_file': video_file}
            headers = {'api_key': "apikey1"}
            response = requests.post(f"{API_URL}/Speaker_Recognition/", 
                                     files=files, headers=headers)

        if response.status_code == 200:
            data = response.text  # Response is a string
            # print(type(data))
            try:
                # Manually parse the string to JSON
                data = json.loads(data)
                # print(f"Successfully parsed JSON: {data}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON. Response was: {data}")
                return  # Exit if parsing fails

            # Now handle the parsed data (which should be a list)
            if isinstance(data, list) and len(data) > 0:
                first_entry = data[0]  # Get the first dictionary in the list
                if isinstance(first_entry, dict):
                    person_name = first_entry.get('person', 'Person not found')
                    return person_name
                else:
                    print("First entry is not a dictionary.")
            else:
                print("Unexpected response structure: empty or not a list.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print("SR API is not working")

if __name__ == "__main__":
    FILE_PATH = "test.wav"
    print(speaker_recognition(file_path=FILE_PATH))
