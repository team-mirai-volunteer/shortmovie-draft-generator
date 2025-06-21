import json
import re
from typing import Any, Optional, List, Dict, cast
import traceback


def parse_variables(text: str) -> list[str]:
    """テキストから{}で囲まれた部分を抽出する"""
    pattern = r"\{(.+?)\}"
    return re.findall(pattern, text)


def parse_json(text: str | dict[str, Any] | None) -> dict[str, Any]:
    """JSONデータをパースする。Pythonコードブロックを含む場合も適切に処理する。"""
    # dict が渡された場合はそのまま返す
    if isinstance(text, dict):
        return text
    # None の場合は空 dict を返す
    if text is None:
        return {}
    try:
        # Markdownのコードフェンス（jsonラベル付き or 無ラベル）から優先的に抽出
        # ```json
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence_match:
            json_data = fence_match.group(1).strip()
        else:
            # 無ラベルのコードフェンスにも対応
            fence_match2 = re.search(r"```([\s\S]*?)```", text)
            if fence_match2:
                json_data = fence_match2.group(1).strip()
            else:
                # JSONを探して抽出
                start = text.find("{")
                end = text.rfind("}") + 1
                if start == -1 or end <= 0:
                    pattern = r"{((.|\n)+?)}"
                    matches = re.findall(pattern, text)
                    json_data = matches[-1][0] if matches else text
                    json_data = "{" + json_data + "}"
                else:
                    json_data = text[start:end]
        # 末尾の不要なカンマを削除
        json_data = re.sub(r",\s*(?=[}\]])", "", json_data)
        # JSONをパース
        return json.loads(json_data, strict=False) or {}
    except json.JSONDecodeError as e:
        try:
            # Pythonリテラルとして評価
            from ast import literal_eval

            result = literal_eval(json_data)
            # dictであれば返却、それ以外は空dict
            if isinstance(result, dict):
                return cast(dict[str, Any], result)
            return {}
        except Exception:
            print("-" * 30)
            print(f"JSON parse error: {e}")
            print(traceback.format_exc())
            print("-" * 30)
            return {}
    except Exception as e:
        print("-" * 30)
        print(f"Unexpected error during JSON parsing: {e}")
        print(traceback.format_exc())
        print("-" * 30)
        return {}


def parse_list(text: str) -> list[Any]:
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        json_data = text[start:end]
        print(json_data)
        return json.loads(json_data, strict=False) or []
    except json.JSONDecodeError:
        try:
            pattern = r"[((.|\n)+?)]"
            matches = re.findall(pattern, text)
            json_data = matches[-1][0] if matches else text
            json_data = "[" + json_data + "]"
            return json.loads(json_data, strict=False) or []
        except json.JSONDecodeError:
            return []


def parse_python_code(text: str) -> str:
    """Pythonコードをパースする"""
    pattern = r"```python\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code_block = match.group(1)
        return code_block
    return ""


def parse_mermaid_flowchart(text: str) -> str:
    """Mermaidフローチャートをパースする"""
    mermaid_match = re.search(r"```mermaid\n(.*?)```", text, re.DOTALL)
    if mermaid_match:
        return mermaid_match.group(1)
    return ""


def parse_page_title_from_filename(file_name: str) -> str:
    """ファイル名からページイトルを抽出する"""
    pattern = r"\d+_(.+?)\.py"
    match = re.search(pattern, file_name)
    if match:
        return match.group(1)
    return file_name


def parse_code_blocks(code: str) -> Optional[List[Dict[str, str]]]:
    """
    Given a code block, parse it and return the information in list of dictionaries format.

    :param code: Code block to parse
    :return: List of dictionaries containing the parsed information
    """
    lines: List[str] = code.split("\n")
    parsed_blocks: List[Dict[str, str]] = []
    current_block: List[str] = []
    current_format: str | None = None
    inside_block: bool = False

    for line in lines:
        if line.startswith("```"):
            if inside_block:
                parsed_blocks.append(
                    {
                        "format": current_format or "",
                        "content": "\n".join(current_block).rstrip(),
                    }
                )
                current_block = []
                inside_block = False
                current_format = None
            else:
                current_format = line.strip("`")
                inside_block = True
        elif inside_block:
            current_block.append(line)

    if inside_block:
        parsed_blocks.append(
            {
                "format": current_format or "",
                "content": "\n".join(current_block).rstrip(),
            }
        )

    return parsed_blocks if parsed_blocks else None
