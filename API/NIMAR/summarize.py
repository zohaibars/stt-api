import requests
from config import SUMMARIZE_URL
from typing import Dict, Any, List

def summarize(input_text: str, running_summaries: List[str] = ["string"]) -> Dict[str, Any]:
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'input': [input_text],
        'running_summaries': running_summaries,
    }

    try:
        # Set a short timeout for the request (e.g., 2 seconds)
        response = requests.post(SUMMARIZE_URL, json=data, headers=headers, timeout=2)
        response.raise_for_status()  # Raises an error for bad status codes
        return response.json()  # Returns the JSON response if successful
    except requests.ConnectionError:
        return {'error': f'API not live at {SUMMARIZE_URL}'}  # Connection error
    except requests.Timeout:
        return {'error': 'Request timed out'}  # Handle request timeout
    except requests.RequestException as e:
        return {'error': f'Request failed: {str(e)}'}  # Handle other request errors

# Example usage
if __name__ == "__main__":
    input_text = "اسپیکر پوچھ رہا ہے کہ \"آپ کون ہیں\" جو کہ کسی گفتگو یا تعارف کا آغاز معلوم ہوتا ہے"
    result = summarize(input_text)
    print(result)
