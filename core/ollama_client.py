import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

def ask_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1200,
                    "stop": ["END_JSON"]
                }
            },
            timeout=180
        )

        if response.status_code != 200:
            print("Ollama API error:", response.text)
            return None

        return response.json().get("response", "")

    except Exception as e:
        print("Ollama connection error:", e)
        return None