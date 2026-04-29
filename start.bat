@echo off
chcp 65001 > nul
echo =====================================
echo AI Speech Summarization を起動しています...
echo =====================================

REM バッチファイルのディレクトリへ移動
cd /d "%~dp0"

REM ---- バックエンド: 初回セットアップ ----
if not exist "backend\venv\Scripts\python.exe" (
    echo [Setup] venv が見つかりません。作成しています...
    python -m venv backend\venv
    if errorlevel 1 (
        echo [Error] venv の作成に失敗しました。Python 3.10+ がインストールされているか確認してください。
        pause
        exit /b 1
    )
    echo [Setup] 依存パッケージをインストールしています...
    backend\venv\Scripts\pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo [Error] pip install に失敗しました。
        pause
        exit /b 1
    )
    echo [Setup] バックエンドのセットアップが完了しました。
)

REM ---- フロントエンド: 初回セットアップ ----
if not exist "frontend\node_modules" (
    echo [Setup] node_modules が見つかりません。npm install を実行しています...
    cd frontend
    npm install
    if errorlevel 1 (
        echo [Error] npm install に失敗しました。Node.js がインストールされているか確認してください。
        cd /d "%~dp0"
        pause
        exit /b 1
    )
    cd /d "%~dp0"
    echo [Setup] フロントエンドのセットアップが完了しました。
)

REM ---- サーバー起動 ----
echo Backend / Frontend サーバーを起動中...
wt new-tab --title "Backend" -- cmd /k "cd /d "%~dp0backend" && venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" ; new-tab --title "Frontend" -- cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM バックエンド起動待ち（疎通確認ポーリング、最大60秒）
echo バックエンドの起動を待機しています...
set RETRY=0
:wait_backend
curl -s http://localhost:8000/docs > nul 2>&1
if not errorlevel 1 goto backend_ready
set /a RETRY+=1
if %RETRY% geq 30 (
    echo [Error] バックエンドが60秒以内に起動しませんでした。Backend タブのログを確認してください。
    pause
    exit /b 1
)
timeout /t 2 > nul
goto wait_backend
:backend_ready
echo バックエンドの起動を確認しました。

REM ブラウザで開く（Viteのデフォルトポートは5173）
echo ブラウザを開いています...
start http://localhost:5173
