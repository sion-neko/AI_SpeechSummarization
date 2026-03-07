from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu") 
segments, info = model.transcribe("sample.mp3", language="ja")

for segment in segments:
    print(segment.text)