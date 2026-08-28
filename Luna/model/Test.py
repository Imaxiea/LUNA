"""
Description: 测试qwen的连接。
"""
import requests


while True:
    prompt = input('user: ')
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b-instruct-q5_K_M",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
            }
        },
        timeout=600
    )
    result = response.json()["response"]
    print(f'reply: {result}')
