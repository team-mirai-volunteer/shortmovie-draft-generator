"""
ツール実行結果の表示ユーティリティ関数
"""

import re


def display_tool_start(tool_name: str, tool_description: str = "No description available") -> str:
    """
    ツール実行開始時の表示用HTML文字列を生成します。

    Args:
        tool_name: ツール名
        tool_description: ツールの説明

    Returns:
        表示用のHTML文字列
    """
    html_contents = f"""
    <div style="
        background: #e2e8f0;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
        border: 1px solid #e0e4e9;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    ">
        <div style="
            display: flex;
            align-items: center;
            color: #2d3748;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 10px;
        ">
            <div style="
                background: #f7fafc;
                border-radius: 4px;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                border: 1px solid #e2e8f0;
            ">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" fill="#718096"/>
                </svg>
            </div>
            <span>ツール実行中: {tool_name}</span>
        </div>
        <div style="
            background: #f7fafc;
            padding: 8px 12px;
            border-radius: 3px;
            color: #4a5568;
            font-size: 13px;
            border: 1px solid #e2e8f0;
        ">
            {tool_description}
        </div>
    </div>
    """
    # 空白を除去してエラーを回避
    html_contents = " ".join(html_contents.split())
    return html_contents


def display_generic_tool_result(result: str, tool_name: str) -> str:
    """
    汎用的なツール実行結果の表示用HTML文字列を生成します。

    Args:
        result: ツールの実行結果
        tool_name: ツール名

    Returns:
        表示用のHTML文字列
    """
    result_preview = str(result)

    html_contents = f"""
    <div style="
        background: #ffffff;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
        border: 1px solid #e0e4e9;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    ">
        <div style="
            display: flex;
            align-items: center;
            color: #2d3748;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 10px;
        ">
            <div style="
                background: #f7fafc;
                border-radius: 4px;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                border: 1px solid #e2e8f0;
            ">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="#718096"/>
                </svg>
            </div>
            <span>ツール完了: {tool_name}</span>
        </div>
        <div style="
            background: #f7fafc;
            padding: 10px 12px;
            border-radius: 3px;
            color: #2d3748;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 13px;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-word;
            border: 1px solid #e2e8f0;
        ">{result_preview}</div>
    </div>
    """
    # 空白を除去してエラーを回避
    html_contents = " ".join(html_contents.split())
    return html_contents


# 共通HTMLコンポーネント生成関数
def create_result_container(
    title: str,
    icon: str,
    background_color: str = "#ffffff",
    scrollable: bool = False,
    max_height: str = "400px",
) -> str:
    """
    結果コンテナの開始部分を生成します。

    Args:
        title: 表示するタイトル
        icon: 表示するアイコン (例: "📄")
        background_color: 背景色（デフォルトは白）
        scrollable: スクロール可能にするかどうか（デフォルトはFalse）
        max_height: スクロール可能な場合の最大高さ（デフォルトは400px）

    Returns:
        HTMLコンテナの開始部分
    """
    # 統一されたグレー系の枠線色
    border_color = "#e2e8f0"

    # メインコンテナ（常に固定表示）
    html_content = f"""
    <div style="
        background: {background_color};
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
        border: 1px solid #e0e4e9;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    ">
        <div style="
            display: flex;
            align-items: center;
            color: #2d3748;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
        ">
            <div style="
                background: #f7fafc;
                border-radius: 4px;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                border: 1px solid {border_color};
            ">
                {icon}
            </div>
            <span>{title}</span>
        </div>"""

    # スクロール可能な場合は、コンテンツエリア用のdivを追加
    if scrollable:
        html_content += f"""
        <div style="
            max-height: {max_height};
            overflow-y: auto;
            padding-right: 5px;
        ">"""

    return html_content


def create_result_item_container() -> str:
    """
    結果アイテムコンテナの開始部分を生成します。

    Returns:
        HTMLアイテムコンテナの開始部分
    """
    return """
    <div style="
        background: #f7fafc;
        padding: 12px;
        border-radius: 3px;
        margin-bottom: 10px;
        border: 1px solid #e2e8f0;
    ">
    """


def create_item_title(title: str, index: int, auto_link: bool = True) -> str:
    """
    アイテムタイトルを生成します。

    Args:
        title: 表示するタイトル
        index: アイテムのインデックス
        auto_link: URLを自動的にリンク化するかどうか（デフォルトはTrue）

    Returns:
        HTMLタイトル要素
    """
    # HTMLエスケープを適用
    import html

    escaped_title = html.escape(title)

    # URLを自動リンク化
    display_title = auto_linkify_urls(escaped_title) if auto_link else escaped_title

    return f"""
    <div style="
        color: #1a202c;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 6px;
        line-height: 1.4;
    ">
        {index}. {display_title}
    </div>
    """


def auto_linkify_urls(text: str) -> str:
    """
    テキスト内のURLを自動検出してクリック可能なリンクに変換します。

    Args:
        text: 変換対象のテキスト

    Returns:
        URL部分がリンク化されたHTML文字列
    """
    # URLパターンを定義（http://, https://, www.で始まるもの）
    url_pattern = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'

    def replace_url(match):
        url = match.group(1)
        # www.で始まる場合はhttps://を追加
        href_url = url if url.startswith(("http://", "https://")) else f"https://{url}"
        return f"""<a href="{href_url}" target="_blank" 
        style="color: #2563eb; text-decoration: underline; font-weight: 500;
        transition: color 0.2s ease-in-out;"
        onmouseover="this.style.color='#1d4ed8'"
        onmouseout="this.style.color='#2563eb'">{url}</a>"""

    # URLをリンクに置換
    return re.sub(url_pattern, replace_url, text)


def create_item_detail(label: str, value: str, emoji: str = None, auto_link: bool = True) -> str:
    """
    アイテム詳細を生成します。

    Args:
        label: 詳細ラベル（表示しない、内部処理用）
        value: 表示する値
        emoji: 詳細の前に表示する絵文字（省略可能）
        auto_link: URLを自動的にリンク化するかどうか（デフォルトはTrue）

    Returns:
        HTML詳細要素
    """
    emoji_prefix = f"{emoji} " if emoji else ""

    # HTMLエスケープを適用（リンク化前に）
    import html

    escaped_value = html.escape(value)

    if label in ["abstract", "snippet"]:
        # 長文は省略表示
        display_value = escaped_value[:200] + ("..." if len(escaped_value) > 200 else "")
        # URLを自動リンク化
        if auto_link:
            display_value = auto_linkify_urls(display_value)

        return f"""
        <div style="
            color: #4a5568;
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 8px;
        ">
            {emoji_prefix}{display_value}
        </div>
        """
    elif label == "link":
        # リンクの場合（既存のロジック）
        return f"""
        <div style="
            color: #4a5568;
            font-size: 13px;
            margin-bottom: 8px;
            word-break: break-all;
        ">
            {emoji_prefix}<a href="{value}" target="_blank" 
                            style="color: #2563eb; text-decoration: underline; font-weight: 500;
                            transition: color 0.2s ease-in-out;"
                            onmouseover="this.style.color='#1d4ed8'"
                            onmouseout="this.style.color='#2563eb'">{escaped_value}</a>
        </div>
        """
    else:
        # 通常の詳細
        display_value = escaped_value
        # URLを自動リンク化
        if auto_link:
            display_value = auto_linkify_urls(display_value)

        return f"""
        <div style="
            color: #4a5568;
            font-size: 13px;
            margin-bottom: 6px;
        ">
            {emoji_prefix}{display_value}
        </div>
        """


def create_detail_content(content: str, auto_link: bool = True) -> str:
    """
    詳細コンテンツを生成します。

    Args:
        content: 表示するコンテンツ
        auto_link: URLを自動的にリンク化するかどうか（デフォルトはTrue）

    Returns:
        HTML詳細コンテンツ要素
    """
    # HTMLエスケープを適用
    import html

    escaped_content = html.escape(content)

    # URLを自動リンク化
    display_content = auto_linkify_urls(escaped_content) if auto_link else escaped_content

    return f"""
    <div style="
        background: #ffffff;
        padding: 12px;
        border-radius: 3px;
        color: #2d3748;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 13px;
        max-height: 200px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-word;
        border: 1px solid #e2e8f0;
    ">{display_content}</div>
    """


def close_container(scrollable: bool = False) -> str:
    """
    コンテナを閉じるHTMLを生成します。

    Args:
        scrollable: スクロール可能コンテナの場合はTrue（デフォルトはFalse）

    Returns:
        HTML閉じタグ
    """
    if scrollable:
        # スクロール可能コンテナの場合は2つのdivを閉じる
        return "</div></div>"
    else:
        # 通常のコンテナの場合は1つのdivを閉じる
        return "</div>"


def clean_html(html_content: str) -> str:
    """
    HTMLコンテンツから不要な空白や改行を削除し、表示用に最適化します。

    Args:
        html_content: 元のHTMLコンテンツ

    Returns:
        最適化されたHTMLコンテンツ
    """
    # 複数の空白や改行を単一の空白に変換
    cleaned = "".join([line for line in html_content.split("\n") if line.strip()])
    return cleaned


def format_context_update_result(result: str, tool_name: str) -> str:
    """
    Context更新系ツールの実行結果をフォーマットします。

    Args:
        result: ツールの実行結果
        tool_name: ツール名

    Returns:
        フォーマットされたHTML文字列
    """
    # update_*やsave_*ツールのアイコンマッピング
    icon_map = {
        "update_project_info": "📝",
        "update_tpp_data": "🎯",
        "update_phase1_data": "🧪",
        "update_operations_data": "🏥",
        "update_ddi_data": "⚗️",
        "save_competitive_analysis": "📊",
        "add_cro_requirements": "📋",
        "add_recommendation": "💡",
    }

    icon = icon_map.get(tool_name, "✅")

    html_contents = f"""
    <div style="
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #cbd5e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    ">
        <div style="
            display: flex;
            align-items: center;
            color: #2d3748;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
        ">
            <div style="
                background: #ffffff;
                border-radius: 6px;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                font-size: 14px;
            ">
                {icon}
            </div>
            <span>データ更新完了: {tool_name}</span>
        </div>
        <div style="
            background: #ffffff;
            padding: 12px 15px;
            border-radius: 6px;
            color: #2d3748;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid #e2e8f0;
            white-space: pre-wrap;
            word-break: break-word;
        ">{result}</div>
    </div>
    """
    return clean_html(html_contents)


def format_context_get_result(result: str, tool_name: str) -> str:
    """
    Context取得系ツールの実行結果をフォーマットします。

    Args:
        result: ツールの実行結果
        tool_name: ツール名

    Returns:
        フォーマットされたHTML文字列
    """
    # get_*ツールのアイコンマッピング
    icon_map = {
        "get_project_status": "📊",
        "get_current_tpp_data": "🎯",
        "get_current_phase1_data": "🧪",
        "get_current_operations_data": "🏥",
        "get_current_ddi_data": "⚗️",
        "get_context_json_dump": "📄",
    }

    icon = icon_map.get(tool_name, "📋")

    html_contents = f"""
    <div style="
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #b3d9ff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    ">
        <div style="
            display: flex;
            align-items: center;
            color: #1a365d;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
        ">
            <div style="
                background: #ffffff;
                border-radius: 6px;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                border: 1px solid #b3d9ff;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                font-size: 14px;
            ">
                {icon}
            </div>
            <span>データ取得完了: {tool_name}</span>
        </div>
        <div style="
            background: #ffffff;
            padding: 12px 15px;
            border-radius: 6px;
            color: #1a365d;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 12px;
            line-height: 1.4;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #b3d9ff;
            white-space: pre-wrap;
            word-break: break-word;
        ">{result}</div>
    </div>
    """
    return clean_html(html_contents)


def format_agent_tool_result(result: str, tool_name: str) -> str:
    """
    エージェントツール（専門分析ツール）の実行結果をフォーマットします。

    Args:
        result: ツールの実行結果
        tool_name: ツール名

    Returns:
        フォーマットされたHTML文字列
    """
    # エージェントツールのアイコンマッピング
    icon_map = {"tpp_strategy_analysis": "🎯", "phase1_trial_design": "🧪", "clinical_operations_planning": "🏥", "ddi_risk_assessment": "⚗️"}

    # エージェントツールの名前マッピング
    name_map = {
        "tpp_strategy_analysis": "TPP戦略分析",
        "phase1_trial_design": "Phase1試験設計",
        "clinical_operations_planning": "臨床運営計画",
        "ddi_risk_assessment": "DDIリスク評価",
    }

    icon = icon_map.get(tool_name, "🤖")
    display_name = name_map.get(tool_name, tool_name)

    html_contents = f"""
    <div style="
        background: linear-gradient(135deg, #fef5e7 0%, #fed7aa 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #f6ad55;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    ">
        <div style="
            display: flex;
            align-items: center;
            color: #7b341e;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
        ">
            <div style="
                background: #ffffff;
                border-radius: 6px;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                border: 1px solid #f6ad55;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                font-size: 14px;
            ">
                {icon}
            </div>
            <span>専門分析完了: {display_name}</span>
        </div>
        <div style="
            background: #ffffff;
            padding: 12px 15px;
            border-radius: 6px;
            color: #7b341e;
            font-size: 13px;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #f6ad55;
            white-space: pre-wrap;
            word-break: break-word;
        ">{result}</div>
    </div>
    """
    return clean_html(html_contents)
