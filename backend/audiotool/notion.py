import requests
import logging
import os

logger = logging.getLogger(__name__)

url = "https://api.notion.com/v1/pages"

VOICE_PAGE_ID = os.environ.get("VOICE_PAGE_ID")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")


def create_notion_page(title: str, content: str = None, blocks: list = None):
    children_blocks = []

    if blocks is not None:
        children_blocks = blocks
    elif content is not None:
        # Notionの仕様で、1つのリッチテキストコンテンツは最大2000文字の制限があります
        # 制限を回避するため、2000文字ごとに分割して複数の段落ブロックとして作成します
        chunk_size = 2000
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": chunk
                            }
                        }
                    ]
                }
            })

    payload = {
        "parent": {
            "page_id": VOICE_PAGE_ID
        },
        "properties": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        },
        "children": children_blocks
    }
    headers = {
        "Notion-Version": "2026-03-11",
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        raise


def format_and_save_summary(title: str, summary_result: dict):
    """
    要約結果(dict)を受け取り、いい感じの構造化ブロック（見出しや色など）にしてNotionに保存する
    """
    topics = summary_result.get("topics", [])
    if not topics:
        create_notion_page(title, content="要約データがありません。")
        return

    blocks = []

    for i, topic in enumerate(topics, 1):
        t_title = topic.get("title", "無題")
        t_summary = topic.get("summary", "")

        # 見出し (Heading 2)
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"{i}. {t_title}"}
                    }
                ]
            }
        })

        # 要約文 (Paragraph)
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": t_summary}
                    }
                ]
            }
        })

        highlights = topic.get("highlights", [])
        if highlights:
            # 重要な発言を太字で表示
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "【重要な発言】"},
                            "annotations": {"bold": True}
                        }
                    ]
                }
            })

            # 発言リスト
            for h in highlights:
                start = h.get("start", 0.0)
                try:
                    start_val = float(start)
                except (ValueError, TypeError):
                    start_val = 0.0

                mm, ss = divmod(int(start_val), 60)
                hh, mm = divmod(mm, 60)
                time_str = f"[{hh:02d}:{mm:02d}:{ss:02d}] " if hh > 0 else f"[{mm:02d}:{ss:02d}] "

                speaker = h.get("speaker", "Unknown")
                text = h.get("text", "")
                reason = h.get("reason", "")

                # 時間は青色、発言内容は通常、理由はグレーにする
                rich_text_array = [
                    {
                        "type": "text",
                        "text": {"content": time_str},
                        "annotations": {"color": "blue"}
                    },
                    {
                        "type": "text",
                        "text": {"content": f"{speaker}: 「{text}」"}
                    }
                ]

                if reason:
                    rich_text_array.append({
                        "type": "text",
                        "text": {"content": f" (理由: {reason})"},
                        "annotations": {"color": "gray"}
                    })

                # 箇条書きブロック
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": rich_text_array
                    }
                })

        # トピック間の区切り線
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

    # 保存処理
    create_notion_page(title, blocks=blocks)


def format_and_save_transcription(title: str, diarization_result: dict):
    """
    文字起こし結果(dict)を受け取り、いい感じのテキストにフォーマットしてNotionに保存する
    """
    formatted_text = ""
    segments = diarization_result.get("segments", [])

    if not segments:
        formatted_text = "文字起こしデータがありません。"

    for segment in segments:
        start = segment.get("start", 0.0)
        try:
            start_val = float(start)
        except (ValueError, TypeError):
            start_val = 0.0

        mm, ss = divmod(int(start_val), 60)
        hh, mm = divmod(mm, 60)
        time_str = f"[{hh:02d}:{mm:02d}:{ss:02d}]" if hh > 0 else f"[{mm:02d}:{ss:02d}]"

        speaker = segment.get("speaker") or "Unknown"
        text = segment.get("text", "").strip()

        formatted_text += f"{time_str} {speaker}: {text}\n"

    # 保存処理
    create_notion_page(title, formatted_text.strip())
