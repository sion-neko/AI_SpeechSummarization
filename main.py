import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from audiotool.core import process_audio
from audiotool.summarize import summarize as summarize_audio


# GPUライブラリ (CUDA/cuDNN) のパスを動的に追加
base_path = os.path.dirname(os.path.abspath(__file__))
cuda_paths = [
    os.path.join(base_path, "venv", "Lib", "site-packages",
                 "nvidia", "cublas", "bin"),
    os.path.join(base_path, "venv", "Lib", "site-packages",
                 "nvidia", "cudnn", "bin"),
]

for path in cuda_paths:
    if os.path.exists(path):
        print(f"Adding DLL directory: {path}")
        os.add_dll_directory(path)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Segment(BaseModel):
    start: float
    end: float
    speaker: str | None = None
    text: str


class SummarizeRequest(BaseModel):
    segments: list[Segment]


@app.post("/transcription")
def transcription(file: UploadFile = File(...)):
    with open("audio_temp.wav", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = process_audio("audio_temp.wav")
    os.remove("audio_temp.wav")
    return result


@app.post("/summarize")
def summarize(body: SummarizeRequest):
    segments = [seg.model_dump() for seg in body.segments]
    result = summarize_audio(segments)
    return result


@app.get("/")
def read_root():
    return {"message": "Hello World"}
