from agents import function_tool, RunContextWrapper
from src.agent_sdk.context.clinical_development import ClinicalDevelopmentContext
from typing import List


@function_tool
def add_reference_urls(context: RunContextWrapper[ClinicalDevelopmentContext], domain: str, urls: List[str], descriptions: List[str] = None) -> str:
    """指定された領域に複数の参照URLを追加します。

    Args:
        domain: 追加先領域 ('project', 'tpp', 'phase1', 'operations', 'ddi', 'analysis')
        urls: 参照URLのリスト
        descriptions: URLの説明のリスト（オプション）

    Returns:
        追加結果のメッセージ
    """
    try:
        if not urls:
            return "URLが指定されていません"

        if descriptions is None:
            descriptions = [""] * len(urls)
        else:
            # descriptionsがurlsより短い場合は空文字で埋める
            descriptions = descriptions + [""] * (len(urls) - len(descriptions))

        added_urls = []

        for i, url in enumerate(urls):
            desc = descriptions[i] if i < len(descriptions) else ""
            url_with_desc = f"{url} ({desc})" if desc else url

            if domain == "project":
                if url_with_desc not in context.context.project_info.reference_urls:
                    context.context.project_info.reference_urls.append(url_with_desc)
                    added_urls.append(url_with_desc)
            elif domain == "tpp":
                if url_with_desc not in context.context.tpp_data.reference_urls:
                    context.context.tpp_data.reference_urls.append(url_with_desc)
                    added_urls.append(url_with_desc)
            elif domain == "phase1":
                if url_with_desc not in context.context.phase1_data.reference_urls:
                    context.context.phase1_data.reference_urls.append(url_with_desc)
                    added_urls.append(url_with_desc)
            elif domain == "operations":
                if url_with_desc not in context.context.operations_data.reference_urls:
                    context.context.operations_data.reference_urls.append(url_with_desc)
                    added_urls.append(url_with_desc)
            elif domain == "ddi":
                if url_with_desc not in context.context.ddi_data.reference_urls:
                    context.context.ddi_data.reference_urls.append(url_with_desc)
                    added_urls.append(url_with_desc)
            elif domain == "analysis":
                if url_with_desc not in context.context.analysis_results.reference_urls:
                    context.context.analysis_results.reference_urls.append(url_with_desc)
                    added_urls.append(url_with_desc)
            else:
                return f"無効な領域が指定されました: {domain}"

        context.context.update_timestamp()

        if len(added_urls) == 0:
            return f"{domain}領域に新しい参照URLはありませんでした（重複のため）"
        elif len(added_urls) == 1:
            return f"{domain}領域に参照URLを追加しました: {added_urls[0]}"
        else:
            return f"{domain}領域に{len(added_urls)}個の参照URLを追加しました: {', '.join(added_urls)}"

    except Exception as e:
        return f"参照URL追加中にエラーが発生しました: {str(e)}"
