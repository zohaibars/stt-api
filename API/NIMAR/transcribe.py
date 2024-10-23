import requests
from config import *

def STT_Job(file_path):
    try:
        # print('API IS LIVE')
        with open(file_path, 'rb') as file_path_:
            files = {'video_file': file_path_}
            headers = {
            'api_key': APIKEY,
            'language': LANGUAGE,
            'news_type': NEWS_TYPE
             }
          
            response = requests.post(SPEECH_URL, files=files, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return(result.get("urdu_full_text"))
        else:
            return(response.text)
    except Exception as e:
        return("Error:", str(e))
print(STT_Job(r"C:\Users\waqar\stt-api\uploads\audio.wav"))