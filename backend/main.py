import os
import json
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
from pathlib import Path
from audiotool.core import process_audio
from audiotool.summarize import summarize as summarize_audio
from datetime import datetime

OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _save_json(data: dict, filename: str, folder_name: str) -> str:
    folder = OUTPUT_DIR / folder_name 
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / f"{filename}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filepath}")
    return filepath

# GPUライブラリ (CUDA/cuDNN) のパスを動的に追加
base_path = os.path.dirname(os.path.abspath(__file__))
cuda_paths = [
    os.path.join(base_path, "venv", "Lib", "site-packages", "nvidia", "cublas", "bin"),
    os.path.join(base_path, "venv", "Lib", "site-packages", "nvidia", "cudnn", "bin"),
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

app.mount("/outputs", StaticFiles(directory="output"), name="outputs")

def process_audio_background(input_filepath: str, folder_name: str):
    """バックグラウンドで文字起こしと要約を実行する"""
    try:
        print(f"Starting background processing for {folder_name}")
        # 1. 文字起こし + 話者分析
        transcription_result = process_audio(input_filepath)
        _save_json(transcription_result, "transcription", folder_name)

        # 2. 要約
        segments = transcription_result.get("segments", [])
        if segments:
            summary_result = summarize_audio(segments)
            _save_json(summary_result, "summary", folder_name)
    except Exception as e:
        print(f"Error processing background tasks for {folder_name}: {e}")

@app.post("/upload")
def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file.filename or "unknown.wav"
    stem = Path(original_filename).stem
    folder_name = f"{timestamp}_{stem}"
    folder_path = OUTPUT_DIR / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # 保存
    audio_path = folder_path / original_filename
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(process_audio_background, str(audio_path), folder_name)
    
    return {"message": "POSTしました。バックグラウンドで処理を開始します。", "folder": folder_name}

@app.get("/results")
def get_results():
    results = []
    if not OUTPUT_DIR.exists():
        return results
        
    for folder in sorted(OUTPUT_DIR.iterdir(), key=lambda x: x.name, reverse=True):
        if not folder.is_dir():
            continue
            
        has_summary = (folder / "summary.json").exists()
        has_transcription = (folder / "transcription.json").exists()
        
        audio_filename = None
        for f in folder.iterdir():
            if f.is_file() and f.suffix.lower() in [".wav"]:
                audio_filename = f.name
                break
                
        # フォルダ名からパース
        parts = folder.name.split("_", 2)
        if len(parts) >= 3:
            timestamp_str = f"{parts[0][:4]}/{parts[0][4:6]}/{parts[0][6:]} {parts[1][:2]}:{parts[1][2:4]}:{parts[1][4:]}"
            title = parts[2]
        else:
            timestamp_str = ""
            title = folder.name
        
        # transcription.jsonから作成日時を取得
        if has_transcription and not timestamp_str:
            try:
                with open(folder / "transcription.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    created_at = data.get("created_at")
                    if created_at:
                        timestamp_str = created_at
            except:
                pass
                
        results.append({
            "id": folder.name,
            "title": title,
            "timestamp": timestamp_str,
            "has_summary": has_summary,
            "has_transcription": has_transcription,
            "audio_filename": audio_filename
        })
        
    return {"results": results}

@app.get("/")
def read_root():
    return {"message": "Hello World"}
