import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
from datetime import datetime
from audiotool.core import process_audio


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
    allow_origins=["http://localhost:5173"]
)


@app.post("/summarize")
def summarize(file: UploadFile = File(...)):
    with open("audio_temp.wav", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # result = process_audio("audio_temp.wav", True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    diarization_result = {"created_at": now, "segments": []}
    diarization_result["segments"] = [
        {"start": 0.0, "end": 5.2, "speaker": "鈴木",
         "text": "本日はお集まりいただきありがとうございます。これよりプロジェクト進捗会議を始めます。"},
        {"start": 5.5, "end": 12.1, "speaker": "佐藤",
         "text": "よろしくお願いします。まずは開発チームからの報告ですが、現在システムAのUI改修はスケジュール通り進んでいます。"},
        {"start": 12.5, "end": 18.0, "speaker": "田中",
         "text": "はい、バックエンド側もAPIの繋ぎ込みが完了し、本番環境でのテスト段階に入りました。"},
        {"start": 18.5, "end": 22.3, "speaker": "鈴木",
         "text": "素晴らしいですね。何か懸念点はありますか？"},
        {"start": 23.0, "end": 30.5, "speaker": "高橋",
         "text": "デザイン側からですが、一部のアニメーションの挙動について、もう少し軽量化できないかという相談を受けています。"},
        {"start": 31.0, "end": 36.2, "speaker": "佐藤",
         "text": "なるほど、それならCSSの最適化を次回のスプリントに組み込みましょうか。"},
        {"start": 36.5, "end": 40.0, "speaker": "伊藤",
         "text": "ですね、インフラ側でも一部のキャッシュ機構を追加すれば解決できそうです。"},
        {"start": 40.5, "end": 45.4, "speaker": "鈴木",
         "text": "わかりました、ではその方針で次回までに調整をお願いします。"},
    ]
    os.remove("audio_temp.wav")
    return diarization_result

    @app.get("/")
    def read_root():
        return {"message": "Hello World"}
