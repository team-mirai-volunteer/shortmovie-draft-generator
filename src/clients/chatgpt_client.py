import json
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel, Field
from pydantic import ValidationError as PydanticValidationError

from ..setting import env_setting


class ChatGPTClientError(Exception):
    """ChatGPTクライアントの基底例外クラス"""

    pass


class ChatGPTAPIError(ChatGPTClientError):
    """ChatGPT API呼び出しエラー"""

    pass


class JSONParseError(ChatGPTClientError):
    """JSON解析エラー"""

    pass


class ValidationError(ChatGPTClientError):
    """バリデーションエラー"""

    pass


class ShortVideoProposal(BaseModel):
    """ショート動画企画案"""

    title: str = Field(..., description="動画タイトル")
    first_impact: str = Field(..., description="最初の2秒のインパクト")
    last_conclusion: str = Field(..., description="最後の結論")
    summary: str = Field(..., description="企画の概要")


class DraftResult(BaseModel):
    """ドラフト生成結果"""

    proposals: List[ShortVideoProposal] = Field(..., description="企画案リスト")
    total_count: int = Field(..., description="企画案の総数")


class TranscriptionResult(BaseModel):
    """文字起こし結果"""

    text: str = Field(..., description="文字起こしテキスト")
    duration: float = Field(..., description="動画の長さ（秒）")
    language: str = Field(default="ja", description="言語")


class ChatGPTClient:
    """ChatGPT APIクライアント"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        ChatGPTクライアントを初期化

        Args:
            api_key: OpenAI APIキー（Noneの場合は環境変数から取得）
            model: 使用するモデル名
            max_retries: 最大リトライ回数
            retry_delay: リトライ間隔（秒）
        """
        self.api_key = api_key or env_setting.OPENAI_API_KEY
        if not self.api_key:
            raise ChatGPTClientError("OpenAI API key is required")

        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = OpenAI(api_key=self.api_key)

    def _convert_time_to_seconds(self, time_str: str) -> float:
        """
        時間文字列（hh:mm:ss）を秒数に変換

        Args:
            time_str: 時間文字列（例: "01:23:45"）

        Returns:
            秒数
        """
        try:
            parts = time_str.split(":")
            if len(parts) == 3:
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            else:
                return float(time_str)
        except (ValueError, AttributeError):
            raise ValidationError(f"Invalid time format: {time_str}")

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        JSON応答を解析

        Args:
            response_text: 応答テキスト

        Returns:
            解析されたJSONデータ
        """
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    json_text = response_text[start:end].strip()
                else:
                    json_text = response_text[start:].strip()
            else:
                json_text = response_text.strip()

            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise JSONParseError(f"Failed to parse JSON response: {e}")

    def _validate_proposals(self, proposals_data: List[Dict[str, Any]]) -> List[ShortVideoProposal]:
        """
        企画案データをバリデーション

        Args:
            proposals_data: 企画案データのリスト

        Returns:
            バリデーション済み企画案リスト
        """
        try:
            proposals = []
            for proposal_data in proposals_data:
                proposal = ShortVideoProposal(**proposal_data)
                proposals.append(proposal)
            return proposals
        except PydanticValidationError as e:
            raise ValidationError(f"Proposal validation failed: {e}")

    def _make_api_call(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        OpenAI APIを呼び出し

        Args:
            messages: メッセージリスト
            temperature: 温度パラメータ

        Returns:
            API応答テキスト
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=4000,
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ChatGPTAPIError(f"API call failed after {self.max_retries} attempts: {e}")
                time.sleep(self.retry_delay * (2**attempt))

    def generate_draft(self, transcription: TranscriptionResult, additional_context: str = "") -> DraftResult:
        """
        文字起こしからドラフトを生成

        Args:
            transcription: 文字起こし結果
            additional_context: 追加のコンテキスト情報

        Returns:
            生成されたドラフト結果
        """
        prompt = f"""
以下の動画の文字起こしから、魅力的なショート動画の企画案を5つ生成してください。

文字起こし内容:
{transcription.text}

動画の長さ: {transcription.duration}秒

{additional_context}

以下のJSON形式で正確に5つの企画案を返してください:

```json
{{
  "proposals": [
    {{
      "title": "企画案のタイトル（20-30文字程度）",
      "first_impact": "最初の2秒で視聴者の興味を惹くフレーズ",
      "last_conclusion": "動画の最後に来る結論や学び、オチ",
      "summary": "企画の概要説明"
    }}
  ]
}}
```

要件:
- 必ず5つの企画案を生成すること
- titleは20-30文字程度で魅力的に
- first_impactは最初の2秒で視聴者を惹きつける内容
- last_conclusionは視聴者が満足できる結論
- summaryは企画の魅力を簡潔に説明
"""

        messages = [
            {
                "role": "system",
                "content": "あなたはYouTubeショート動画の企画を専門とするクリエイターです。視聴者の興味を惹く魅力的な企画案を生成してください。",
            },
            {"role": "user", "content": prompt},
        ]

        response_text = self._make_api_call(messages)
        response_data = self._parse_json_response(response_text)

        if "proposals" not in response_data:
            raise ValidationError("Response does not contain 'proposals' field")

        proposals_data = response_data["proposals"]
        if len(proposals_data) != 5:
            raise ValidationError(f"Expected exactly 5 proposals, got {len(proposals_data)}")

        proposals = self._validate_proposals(proposals_data)

        return DraftResult(proposals=proposals, total_count=len(proposals))

    def generate_draft_from_prompt(self, prompt: str, context: str = "") -> DraftResult:
        """
        プロンプトからドラフトを生成

        Args:
            prompt: 生成プロンプト
            context: 追加のコンテキスト

        Returns:
            生成されたドラフト結果
        """
        full_prompt = f"""
{prompt}

{context}

以下のJSON形式で正確に5つの企画案を返してください:

```json
{{
  "proposals": [
    {{
      "title": "企画案のタイトル（20-30文字程度）",
      "first_impact": "最初の2秒で視聴者の興味を惹くフレーズ",
      "last_conclusion": "動画の最後に来る結論や学び、オチ",
      "summary": "企画の概要説明"
    }}
  ]
}}
```

要件:
- 必ず5つの企画案を生成すること
- titleは20-30文字程度で魅力的に
- first_impactは最初の2秒で視聴者を惹きつける内容
- last_conclusionは視聴者が満足できる結論
- summaryは企画の魅力を簡潔に説明
"""

        messages = [
            {
                "role": "system",
                "content": "あなたはYouTubeショート動画の企画を専門とするクリエイターです。視聴者の興味を惹く魅力的な企画案を生成してください。",
            },
            {"role": "user", "content": full_prompt},
        ]

        response_text = self._make_api_call(messages)
        response_data = self._parse_json_response(response_text)

        if "proposals" not in response_data:
            raise ValidationError("Response does not contain 'proposals' field")

        proposals_data = response_data["proposals"]
        if len(proposals_data) != 5:
            raise ValidationError(f"Expected exactly 5 proposals, got {len(proposals_data)}")

        proposals = self._validate_proposals(proposals_data)

        return DraftResult(proposals=proposals, total_count=len(proposals))
