# Speech to Text

ローカルLLM環境で音声を文字起こしするためのツールです。  
Ollama と Python を使用して動作します。

---

# 環境構築手順

## 1. Ollama のインストール

以下の公式サイトから Ollama をインストールしてください。

https://ollama.com/

インストール後、以下のコマンドで動作確認ができます。

```bash
ollama --version
````

---

## 2. Python 環境の構築

必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

---

## 3. Ollama の起動

Ollama のサーバーを起動します。

```bash
ollama serve
```

---

## 4. プログラムの実行

以下のコマンドで音声の文字起こしを実行できます。

```bash
python speach2text.py
```


# 備考

* Ollama が起動していない場合、プログラムは動作しません
* 必要に応じて Ollama のモデルを事前に pull してください

```
