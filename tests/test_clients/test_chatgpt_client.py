import json
from unittest.mock import Mock, patch

import pytest

from src.clients.chatgpt_client import (
    ChatGPTAPIError,
    ChatGPTClient,
    ChatGPTClientError,
    DraftResult,
    JSONParseError,
    ShortVideoProposal,
    TranscriptionResult,
    ValidationError,
)


class TestChatGPTClient:
    """ChatGPTクライアントのテストクラス"""

    def test_init_with_api_key(self):
        """APIキー指定での初期化テスト"""
        client = ChatGPTClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "gpt-4o-mini"
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_init_without_api_key_raises_error(self):
        """APIキーなしでの初期化エラーテスト"""
        with patch("src.clients.chatgpt_client.env_setting") as mock_env:
            mock_env.OPENAI_API_KEY = ""
            with pytest.raises(ChatGPTClientError, match="OpenAI API key is required"):
                ChatGPTClient()

    def test_convert_time_to_seconds(self):
        """時間変換テスト"""
        client = ChatGPTClient(api_key="test-key")

        assert client._convert_time_to_seconds("01:23:45") == 5025.0
        assert client._convert_time_to_seconds("23:45") == 1425.0
        assert client._convert_time_to_seconds("45") == 45.0

        with pytest.raises(ValidationError):
            client._convert_time_to_seconds("invalid")

    def test_parse_json_response_with_code_block(self):
        """JSONコードブロック解析テスト"""
        client = ChatGPTClient(api_key="test-key")

        response_text = """```json
{
  "proposals": [
    {
      "title": "テストタイトル",
      "first_impact": "テストインパクト",
      "last_conclusion": "テスト結論",
      "summary": "テスト概要"
    }
  ]
}
```"""

        result = client._parse_json_response(response_text)
        assert "proposals" in result
        assert len(result["proposals"]) == 1
        assert result["proposals"][0]["title"] == "テストタイトル"

    def test_parse_json_response_without_code_block(self):
        """JSONコードブロックなし解析テスト"""
        client = ChatGPTClient(api_key="test-key")

        response_text = '{"test": "value"}'
        result = client._parse_json_response(response_text)
        assert result["test"] == "value"

    def test_parse_json_response_invalid_json(self):
        """無効JSON解析エラーテスト"""
        client = ChatGPTClient(api_key="test-key")

        with pytest.raises(JSONParseError):
            client._parse_json_response("invalid json")

    def test_validate_proposals_success(self):
        """企画案バリデーション成功テスト"""
        client = ChatGPTClient(api_key="test-key")

        proposals_data = [
            {
                "title": "テストタイトル1",
                "first_impact": "テストインパクト1",
                "last_conclusion": "テスト結論1",
                "summary": "テスト概要1",
            },
            {
                "title": "テストタイトル2",
                "first_impact": "テストインパクト2",
                "last_conclusion": "テスト結論2",
                "summary": "テスト概要2",
            },
        ]

        proposals = client._validate_proposals(proposals_data)
        assert len(proposals) == 2
        assert all(isinstance(p, ShortVideoProposal) for p in proposals)
        assert proposals[0].title == "テストタイトル1"

    def test_validate_proposals_missing_field(self):
        """企画案バリデーション失敗テスト"""
        client = ChatGPTClient(api_key="test-key")

        proposals_data = [{"title": "テストタイトル", "first_impact": "テストインパクト"}]

        with pytest.raises(ValidationError):
            client._validate_proposals(proposals_data)

    @patch("src.clients.chatgpt_client.OpenAI")
    def test_make_api_call_success(self, mock_openai):
        """API呼び出し成功テスト"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test response"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = ChatGPTClient(api_key="test-key")

        messages = [{"role": "user", "content": "test"}]
        result = client._make_api_call(messages)

        assert result == "test response"
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.clients.chatgpt_client.OpenAI")
    def test_make_api_call_retry_and_fail(self, mock_openai):
        """API呼び出しリトライ後失敗テスト"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        client = ChatGPTClient(api_key="test-key", max_retries=2, retry_delay=0.1)

        messages = [{"role": "user", "content": "test"}]

        with pytest.raises(ChatGPTAPIError):
            client._make_api_call(messages)

        assert mock_client.chat.completions.create.call_count == 2

    @patch.object(ChatGPTClient, "_make_api_call")
    def test_generate_draft_success(self, mock_api_call):
        """ドラフト生成成功テスト"""
        mock_response = """```json
{
  "proposals": [
    {
      "title": "テストタイトル1",
      "first_impact": "テストインパクト1",
      "last_conclusion": "テスト結論1",
      "summary": "テスト概要1"
    },
    {
      "title": "テストタイトル2",
      "first_impact": "テストインパクト2",
      "last_conclusion": "テスト結論2",
      "summary": "テスト概要2"
    },
    {
      "title": "テストタイトル3",
      "first_impact": "テストインパクト3",
      "last_conclusion": "テスト結論3",
      "summary": "テスト概要3"
    },
    {
      "title": "テストタイトル4",
      "first_impact": "テストインパクト4",
      "last_conclusion": "テスト結論4",
      "summary": "テスト概要4"
    },
    {
      "title": "テストタイトル5",
      "first_impact": "テストインパクト5",
      "last_conclusion": "テスト結論5",
      "summary": "テスト概要5"
    }
  ]
}
```"""
        mock_api_call.return_value = mock_response

        client = ChatGPTClient(api_key="test-key")
        transcription = TranscriptionResult(text="テスト文字起こし", duration=120.0, language="ja")

        result = client.generate_draft(transcription)

        assert isinstance(result, DraftResult)
        assert len(result.proposals) == 5
        assert result.total_count == 5
        assert result.proposals[0].title == "テストタイトル1"

    @patch.object(ChatGPTClient, "_make_api_call")
    def test_generate_draft_wrong_proposal_count(self, mock_api_call):
        """ドラフト生成企画案数エラーテスト"""
        mock_response = """```json
{
  "proposals": [
    {
      "title": "テストタイトル1",
      "first_impact": "テストインパクト1",
      "last_conclusion": "テスト結論1",
      "summary": "テスト概要1"
    }
  ]
}
```"""
        mock_api_call.return_value = mock_response

        client = ChatGPTClient(api_key="test-key")
        transcription = TranscriptionResult(text="テスト文字起こし", duration=120.0, language="ja")

        with pytest.raises(ValidationError, match="Expected exactly 5 proposals"):
            client.generate_draft(transcription)

    @patch.object(ChatGPTClient, "_make_api_call")
    def test_generate_draft_missing_proposals_field(self, mock_api_call):
        """ドラフト生成proposalsフィールドなしエラーテスト"""
        mock_response = """```json
{
  "data": []
}
```"""
        mock_api_call.return_value = mock_response

        client = ChatGPTClient(api_key="test-key")
        transcription = TranscriptionResult(text="テスト文字起こし", duration=120.0, language="ja")

        with pytest.raises(ValidationError, match="Response does not contain 'proposals' field"):
            client.generate_draft(transcription)


class TestModels:
    """モデルクラステスト"""

    def test_short_video_proposal(self):
        """ShortVideoProposalモデルテスト"""
        proposal = ShortVideoProposal(title="テストタイトル", first_impact="テストインパクト", last_conclusion="テスト結論", summary="テスト概要")

        assert proposal.title == "テストタイトル"
        assert proposal.first_impact == "テストインパクト"
        assert proposal.last_conclusion == "テスト結論"
        assert proposal.summary == "テスト概要"

    def test_draft_result(self):
        """DraftResultモデルテスト"""
        proposals = [ShortVideoProposal(title="テストタイトル1", first_impact="テストインパクト1", last_conclusion="テスト結論1", summary="テスト概要1")]

        result = DraftResult(proposals=proposals, total_count=1)

        assert len(result.proposals) == 1
        assert result.total_count == 1
        assert result.proposals[0].title == "テストタイトル1"

    def test_transcription_result(self):
        """TranscriptionResultモデルテスト"""
        transcription = TranscriptionResult(text="テスト文字起こし", duration=120.0, language="ja")

        assert transcription.text == "テスト文字起こし"
        assert transcription.duration == 120.0
        assert transcription.language == "ja"
