from faster_whisper import WhisperModel
import requests


model = WhisperModel("large-v3", device="cpu") 
segments, info = model.transcribe("input/sample.mp3", language="ja")

text = ""
for segment in segments:
    text += segment.text


url = "http://localhost:11434/api/generate"
data = {
    "model": "qwen3.5:4b",
    "prompt": "要約してください。" + text,
    "stream": False
}

res = requests.post(url, json=data)
print(res.json()["response"])
    