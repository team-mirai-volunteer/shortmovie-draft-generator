# reasoning機能をサポートするモデルのリスト
REASONING_SUPPORTED_MODELS = ["o3", "o3-mini", "o4-mini"]


def create_reasoning_setting():
    """
    reasoning設定用のStreamlit UIを作成する

    Returns:
        tuple: (reasoning_effort, reasoning_summary)
    """
    import streamlit as st

    reasoning_effort = st.selectbox(
        "推論レベル",
        ["low", "medium", "high"],
        index=0,
        help="推論の深さを選択します。highほど時間がかかりますが、より詳細な推論を行います。",
    )

    reasoning_summary = st.selectbox(
        "推論サマリー",
        ["auto", "detailed", "none"],
        index=0,
        help="推論過程の表示レベルを選択します。",
    )

    return reasoning_effort, reasoning_summary


def create_model_settings(model: str, reasoning_effort: str = "medium", reasoning_summary: str = "detailed"):
    """
    モデルに応じて適切なModelSettingsを作成する

    Args:
        model: 使用するモデル名
        reasoning_effort: 推論レベル (low, medium, high)
        reasoning_summary: 推論サマリー (auto, detailed, none)

    Returns:
        ModelSettings: 適切に設定されたModelSettingsオブジェクト
    """
    from agents import ModelSettings

    # reasoning対応モデルの場合のみreasoningを指定
    if model in REASONING_SUPPORTED_MODELS:
        return ModelSettings(reasoning={"effort": reasoning_effort, "summary": reasoning_summary})
    else:
        return ModelSettings()


def create_model_selector():
    """
    標準的なモデル選択UIを作成する

    Returns:
        str: 選択されたモデル名
    """
    import streamlit as st

    MODELS = [
        "o3",
        "o3-mini",
        "o4-mini",
        "gpt-4o",
    ]
    return st.selectbox("モデルを選択してください", MODELS)
