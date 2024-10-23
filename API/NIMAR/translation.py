import requests
from config import TRANSLATE_URL

def translate(text: str) -> str:
    """Send a POST request to the API and return only the translated text."""
    payload = {'text': text}

    try:
        # Send the POST request with a timeout (e.g., 2 seconds)
        response = requests.post(TRANSLATE_URL, json=payload, timeout=2)

        if response.status_code == 200:
            # Extract 'translated_text' from the response JSON
            result = response.json()
            return result.get('translated_text', "No translated_text found")
        else:
            return f"Request failed with status code {response.status_code}"

    except requests.ConnectionError:
        return f'API not live at {TRANSLATE_URL}'  # Connection error
    except requests.Timeout:
        return 'Request timed out'  # Handle request timeout
    except requests.RequestException as e:
        return f'Request failed: {str(e)}'  # Handle other request errors


# Example usage
if __name__ == "__main__":
    text_input = "my name is waqar"
    translated_text = translate(text_input)
    print(translated_text)
