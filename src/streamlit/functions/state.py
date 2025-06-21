import streamlit as st
import os
from typing import Any, TypeVar
import inspect

T = TypeVar("T")


def add_session_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value
    return st.session_state.get(key, None)


def get_page_key(key: str) -> str:
    """Page固有のセッションステートキーを生成する"""
    # 呼び出し元のフレームを取得
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    # 呼び出し元のファイルパスを取得
    caller_path = frame.f_code.co_filename  # type: ignore
    # ファイル名（拡張子なし）を取得
    page_name = os.path.splitext(os.path.basename(caller_path))[0]
    return f"{page_name}_{key}"


def get_page_state(key: str, default: T = None) -> T:
    """Page固有のセッションステート値を取得する"""
    return st.session_state.get(get_page_key(key), default)


def set_page_state(key: str, value: Any) -> None:
    """Page固有のセッションステート値を設定する"""
    st.session_state[get_page_key(key)] = value
