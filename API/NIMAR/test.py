import requests
from utils import get_ip_address
# Replace with the URL where your FastAPI server is running
speech_url = "http://"+"192.168.18.81"+":3000"
# print(url)
# Replace with your API key
api_key = "apikey1"
def STT(file_path,ID=None):
    try:
        # print('API IS LIVE')
        with open(file_path, 'rb') as file_path_:
            files = {'file': file_path_}
            headers={
                'api_key': api_key
            }
            params = {'ID': ID} 
            response = requests.post(f"{speech_url}/STTNode/", files=files, headers=headers,params=params)
        if response.status_code == 200:
            result = response.json()
            print(result)
        else:
            print(response.text)
    except Exception as e:
        print("Error:", str(e))
if __name__ == "__main__":
 
    STT(r"/home/waqar/MWaqar/NIMAR/TestSample/download (3).jpg",ID=5)
    # STT(r"/home/waqar/MWaqar/NIMAR/TestSample/urdu video.mp4",ID=4)
    # STT(r"/home/waqar/MWaqar/NIMAR/TestSample/english.mp4",ID=1122)