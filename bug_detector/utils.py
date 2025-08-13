import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ollama_request(prompt, model="phi"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "❌ No response from model.")
    except Exception as e:
        print("❌ Ollama request failed:", e)
        if 'response' in locals():
            print("❌ Raw response:", response.text)
        return "❌ Local model request failed."

def generate_code(prompt, language):
    full_prompt = f"Write {language} code for the following prompt:\n{prompt}"
    return ollama_request(full_prompt)

def debug_code(code):
    prompt = f"This code has bugs:\n{code}\n\nPlease correct it and return the fixed version only."
    return ollama_request(prompt)
