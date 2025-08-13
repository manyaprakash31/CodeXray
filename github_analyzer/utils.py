import requests


OLLAMA_MODEL_NAME = "phi"
def analyze_with_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        return result.get("response", "❌ No response from model.")
    except Exception as e:
        return f"❌ Ollama error: {str(e)}" 
        
import os

import os
import requests  # ✅ Required for API call
# utils.py
def analyze_with_together(repo):
    from together import Together
    client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

    def get_all_code(repo, path=""):
        contents = repo.get_contents(path)
        code_text = ""
        for content in contents:
            if content.type == "dir":
                code_text += get_all_code(repo, content.path)
            else:
                if content.name.endswith(('.py', '.js', '.java', '.cpp', '.ts', '.html', '.css')):
                    try:
                        file_content = content.decoded_content.decode()
                        code_text += f"\n\n# File: {content.path}\n{file_content}\n"
                    except Exception as e:
                        continue
        return code_text

    # Extract all code
    code_text = get_all_code(repo)
    if not code_text:
        return "No valid code files found to analyze."

    # Prompt to AI
    prompt = f"Analyze the following code repository and provide a summary with major components and functionality:\n\n{code_text[:15000]}"

    response = client.chat.completions.create(
        model="togethercomputer/llama-3-8b-chat",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

    api_key = os.getenv("TOGETHER_API_KEY")
    print("🔐 Together API Key:", api_key)

    url = "https://api.together.xyz/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that explains and debugs code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


