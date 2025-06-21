import sys, os
import streamlit as st
from collections import defaultdict
from typing import Dict, List, Any, Union
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.streamlit.components.base import init_page_config, header
from src.lib.logger import configure_logger

init_page_config()
header()
configure_logger()

st.markdown(
    """
<style>
.st-emotion-cache-oq308l.eczjsme2 {
    font-family: 'Arial', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: #333;
    padding: 10px 15px;
    border-left: 4px solid black;
    background-color: #f8f8f8;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

</style>
""",
    unsafe_allow_html=True,
)

PAGES_DIR = "src/streamlit/pages"


def trim_initial_number(file_name: str) -> str:
    """ファイル名/ディレクトリ名の先頭の番号を除去"""
    if "_" not in file_name:
        return file_name
    return file_name.split("_", 1)[1]


def has_streamlit_import(file_path: str) -> bool:
    """
    ファイルがstreamlitをimportしているかチェック

    Args:
        file_path: チェックするPythonファイルのパス

    Returns:
        bool: streamlitをimportしている場合True
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # streamlitのimportパターンを検索
        import_patterns = [
            r"^\s*import\s+streamlit\b",  # import streamlit
            r"^\s*import\s+streamlit\s+as\s+\w+",  # import streamlit as st
            r"^\s*from\s+streamlit\b",  # from streamlit import ...
        ]

        for pattern in import_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True

        return False

    except (FileNotFoundError, UnicodeDecodeError, PermissionError) as e:
        # print(f"Error reading file {file_path}: {str(e)}")
        return False


def build_pages_recursively(directory_path: str, relative_path: str = "", level: int = 0) -> Dict[str, Any]:
    """
    ディレクトリを再帰的に処理してページ構造を構築（streamlitをimportするファイルのみ）

    Args:
        directory_path: 絶対パス
        relative_path: pagesからの相対パス
        level: 階層レベル（0が最上位）

    Returns:
        dict: ネストしたページ構造
    """
    pages_structure: Dict[str, Any] = {}

    if not os.path.exists(directory_path):
        return pages_structure

    items = os.listdir(directory_path)
    items = sorted(items)

    # 現在のレベルのページリスト
    current_level_pages: List[Any] = []

    for item in items:
        item_path = os.path.join(directory_path, item)

        if os.path.isdir(item_path):
            # ディレクトリの場合：再帰的に処理
            trimmed_dir_name = trim_initial_number(item)
            relative_subpath = os.path.join(relative_path, item) if relative_path else item

            # サブディレクトリを再帰的に処理
            subdirectory_pages = build_pages_recursively(item_path, relative_subpath, level + 1)

            if subdirectory_pages:
                pages_structure[trimmed_dir_name] = subdirectory_pages

        elif item.endswith(".py"):
            # Pythonファイルの場合：streamlitをimportしているかチェック
            if not has_streamlit_import(item_path):
                # print(f"Skipping {item_path}: No streamlit import found")
                continue

            file_name = os.path.splitext(item)[0]
            trimmed_file_name = trim_initial_number(file_name)

            # pagesからの相対パスを構築
            if relative_path:
                page_path = f"pages/{relative_path}/{item}"
            else:
                page_path = f"pages/{item}"

            try:
                current_level_pages.append(st.Page(page_path, title=trimmed_file_name))
                # print(f"Added page: {page_path} (title: {trimmed_file_name})")
            except Exception as e:
                # print(f"Error creating page for {page_path}: {str(e)}")
                pass

    # 現在のレベルにページがある場合は追加
    if current_level_pages:
        pages_structure["_pages"] = current_level_pages
        pages_structure["_level"] = level

    return pages_structure


def flatten_pages_structure(structure: Dict[str, Any], parent_key: str = "", level: int = 0) -> Dict[str, List[Any]]:
    """
    ネストした構造をStreamlitのnavigationに適した形式に変換（階層レベル情報付き）
    """
    flattened: Dict[str, List[Any]] = {}

    for key, value in structure.items():
        if key == "_pages":
            # ページリストの場合
            if parent_key:
                # 階層レベル情報をプレフィックスとして追加
                level_prefix = f"[LEVEL{level}]"
                display_name = f"{level_prefix}{parent_key}"
                flattened[display_name] = value
            else:
                flattened["[LEVEL0]ルート"] = value
        elif key == "_level":
            # レベル情報はスキップ
            continue
        elif isinstance(value, dict):
            # ネストした辞書の場合
            current_level = value.get("_level", level)

            if "_pages" in value:
                # このレベルにページがある場合
                level_prefix = f"[LEVEL{current_level}]"
                display_name = f"{level_prefix}{key}"
                flattened[display_name] = value["_pages"]

                # サブディレクトリも処理
                sub_structure = {k: v for k, v in value.items() if k not in ["_pages", "_level"]}
                if sub_structure:
                    sub_flattened = flatten_pages_structure(sub_structure, "", current_level + 1)
                    flattened.update(sub_flattened)
            else:
                # ページがない場合はサブディレクトリのみ処理
                sub_flattened = flatten_pages_structure(value, key, current_level)
                flattened.update(sub_flattened)

    return flattened


# ページ構造を構築
# print("Building pages structure...")
pages_structure = build_pages_recursively(PAGES_DIR)
pages = flatten_pages_structure(pages_structure)

# ナビゲーションを作成
if pages:
    pg = st.navigation(pages)
    pg.run()
else:
    st.error("StreamlitをimportするPythonファイルが見つかりませんでした。")
    st.write(f"検索ディレクトリ: {PAGES_DIR}")
    st.write("次のパターンでstreamlitをimportしているファイルのみが対象です：")
    st.code(
        """
import streamlit
import streamlit as st
from streamlit import ...
from streamlit.components import ...
    """
    )
