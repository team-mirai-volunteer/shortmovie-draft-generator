import streamlit as st
import streamlit.components.v1 as components


def init_page_config():
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSSスタイル
    st.markdown(
        """
    <style>
    /* 基本のヘッダースタイル（レベル0） */
    .st-emotion-cache-oq308l.eczjsme2,
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #000000;
        padding: 8px 16px;
        border-left: 4px solid #000000;
        background-color: #ffffff;
        margin-bottom: 12px;
        margin-left: 0px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        cursor: pointer;
        position: relative;
        user-select: none;
        line-height: 1.2;
        transition: all 0.3s ease;
    }

    /* 階層レベル1（子セクション）のスタイル */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="1"] {
        font-size: 14px;
        font-weight: 600;
        padding: 6px 14px;
        margin-left: 20px;
        margin-right: 8px;
        border-left: 3px solid #666666;
        background-color: #f8f8f8;
        margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        color: #333333;
        border-radius: 0 4px 4px 0;
    }

    /* 階層レベル2（孫セクション）のスタイル */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="2"] {
        font-size: 12px;
        font-weight: 500;
        padding: 4px 12px;
        margin-left: 40px;
        margin-right: 16px;
        border-left: 2px solid #999999;
        background-color: #f0f0f0;
        margin-bottom: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        color: #555555;
        text-transform: none;
        letter-spacing: 0.4px;
        border-radius: 0 6px 6px 0;
    }

    /* 階層レベル3（ひ孫セクション）のスタイル */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="3"] {
        font-size: 11px;
        font-weight: 400;
        padding: 3px 10px;
        margin-left: 60px;
        margin-right: 24px;
        border-left: 1px solid #bbbbbb;
        background-color: #eeeeee;
        margin-bottom: 4px;
        box-shadow: 0 1px 1px rgba(0,0,0,0.03);
        color: #666666;
        text-transform: none;
        letter-spacing: 0.2px;
        border-radius: 0 8px 8px 0;
    }

    /* ホバーエフェクト */
    .st-emotion-cache-oq308l.eczjsme2:hover,
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header:hover {
        background-color: #f0f0f0;
        transform: translateX(2px);
    }

    /* 子セクションのホバー */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="1"]:hover {
        background-color: #e8e8e8;
        transform: translateX(3px);
    }

    /* 孫セクションのホバー */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="2"]:hover {
        background-color: #e0e0e0;
        transform: translateX(4px);
    }

    /* ひ孫セクションのホバー */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="3"]:hover {
        background-color: #d8d8d8;
        transform: translateX(5px);
    }

    /* 折り畳みインジケーター */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header:before {
        content: "▼";
        position: absolute;
        right: 16px;
        top: 50%;
        transform: translateY(-50%);
        transition: transform 0.3s ease;
        font-size: 12px;
    }

    /* 子セクションのインジケーター */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="1"]:before {
        right: 14px;
        font-size: 10px;
    }

    /* 孫セクションのインジケーター */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="2"]:before {
        right: 12px;
        font-size: 9px;
    }

    /* ひ孫セクションのインジケーター */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="3"]:before {
        right: 10px;
        font-size: 8px;
    }

    /* 折り畳み時のインジケーター */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header.collapsed:before {
        content: "▶";
        transform: translateY(-50%);
    }

    /* 折り畳まれたセクションのアイテムを非表示 */
    .section-item.hidden {
        display: none !important;
    }

    /* 親が折り畳まれた時の子セクションも非表示 */
    .child-section.parent-collapsed {
        display: none !important;
    }

    /* サイドバー内のli要素（ページリンク）も階層に応じてインデント */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > li {
        transition: all 0.3s ease;
    }

    /* レベル1セクション配下のページリンクインデント */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="1"] + li,
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > li[data-parent-level="1"] {
        margin-left: 24px;
    }

    /* レベル2セクション配下のページリンクインデント */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="2"] + li,
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > li[data-parent-level="2"] {
        margin-left: 44px;
    }

    /* レベル3セクション配下のページリンクインデント */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header[data-level="3"] + li,
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > li[data-parent-level="3"] {
        margin-left: 64px;
    }

    /* クリック時の視覚的フィードバック */
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stSidebar.st-emotion-cache-11ig4q4.edtmxes0 > div.st-emotion-cache-jx6q2s.edtmxes8 > div.st-emotion-cache-79elbk.edtmxes1 > ul > header:active {
        transform: translateY(1px);
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
    }
    
    </style>
    """,
        unsafe_allow_html=True,
    )

    # JavaScript機能
    components.html(
        """
    <script>
    // 階層レベルを検出する関数（[LEVEL]プレフィックスから判定）
    function detectHierarchyLevel(headerText) {
        const match = headerText.match(/^\[LEVEL(\d+)\]/);
        if (match) {
            return parseInt(match[1]);
        }
        return 0;
    }
    
    // ヘッダーテキストからレベルプレフィックスを除去
    function cleanHeaderText(headerText) {
        return headerText.replace(/^\[LEVEL\d+\]/, '');
    }
    
    // 親セクションを見つける関数
    function findParentHeader(currentHeader, currentLevel) {
        let previousElement = currentHeader.previousElementSibling;
        
        while (previousElement) {
            if (previousElement.tagName === 'HEADER') {
                const previousLevel = parseInt(previousElement.getAttribute('data-level') || '0');
                if (previousLevel < currentLevel) {
                    return previousElement;
                }
            }
            previousElement = previousElement.previousElementSibling;
        }
        return null;
    }
    
    // 子セクションを見つける関数
    function findChildHeaders(parentHeader, parentLevel) {
        const childHeaders = [];
        let nextElement = parentHeader.nextElementSibling;
        
        while (nextElement) {
            if (nextElement.tagName === 'HEADER') {
                const nextLevel = parseInt(nextElement.getAttribute('data-level') || '0');
                if (nextLevel > parentLevel) {
                    childHeaders.push(nextElement);
                } else {
                    // 同レベルまたは上位レベルに到達したら終了
                    break;
                }
            } else if (nextElement.tagName === 'LI') {
                // 現在のセクションのli要素はスキップ
            }
            nextElement = nextElement.nextElementSibling;
        }
        return childHeaders;
    }
    
    // 子セクションの直後にあるページリンクも取得
    function findChildElements(parentHeader, parentLevel) {
        const childElements = [];
        let nextElement = parentHeader.nextElementSibling;
        
        while (nextElement) {
            if (nextElement.tagName === 'HEADER') {
                const nextLevel = parseInt(nextElement.getAttribute('data-level') || '0');
                if (nextLevel > parentLevel) {
                    // 子ヘッダーとその後のli要素を追加
                    childElements.push(nextElement);
                    
                    // 子ヘッダーの後のli要素も追加
                    let childNext = nextElement.nextElementSibling;
                    while (childNext && childNext.tagName === 'LI') {
                        childElements.push(childNext);
                        childNext = childNext.nextElementSibling;
                    }
                } else {
                    // 同レベルまたは上位レベルに到達したら終了
                    break;
                }
            }
            nextElement = nextElement.nextElementSibling;
        }
        return childElements;
    }
    
    // 親が折り畳まれているかチェック
    function isParentCollapsed(header, level) {
        const parentHeader = findParentHeader(header, level);
        return parentHeader && parentHeader.classList.contains('collapsed');
    }
    
    // 子セクションと関連する要素の表示/非表示を制御
    function toggleChildSections(parentHeader, parentLevel, isCollapsed) {
        const childElements = findChildElements(parentHeader, parentLevel);
        
        childElements.forEach(element => {
            if (isCollapsed) {
                // 親が折り畳まれた場合：子要素を非表示
                element.classList.add('parent-collapsed');
                element.style.display = 'none';
            } else {
                // 親が展開された場合：子要素を表示
                element.classList.remove('parent-collapsed');
                element.style.display = '';
                
                // ただし、子ヘッダー自体が折り畳まれている場合は、そのli要素は非表示のまま
                if (element.tagName === 'LI') {
                    let prevHeader = element.previousElementSibling;
                    while (prevHeader && prevHeader.tagName !== 'HEADER') {
                        prevHeader = prevHeader.previousElementSibling;
                    }
                    if (prevHeader && prevHeader.classList.contains('collapsed')) {
                        element.style.display = 'none';
                    }
                }
            }
        });
    }

    // ページ読み込み完了後に実行
    function initCollapsibleHeaders() {
        // 親ウィンドウ（Streamlitアプリ）内のヘッダーを取得
        const parentDocument = window.top.document;
        const headers = parentDocument.querySelectorAll('[data-testid="stNavSectionHeader"]');
        
        if (headers.length === 0) return;
        
        headers.forEach(header => {
            // 既にイベントリスナーが追加されている場合はスキップ
            if (header.hasAttribute('data-collapse-initialized')) {
                return;
            }
            
            // ヘッダーテキストから階層レベルを検出
            const headerText = header.textContent || '';
            const level = detectHierarchyLevel(headerText);
            header.setAttribute('data-level', level.toString());
            
            // ヘッダーテキストをクリーンアップ（表示用）
            const cleanText = cleanHeaderText(headerText);
            if (cleanText !== headerText) {
                header.textContent = cleanText;
            }
            
            // このセクションのページリンク（li要素）にレベル情報を設定
            let nextElement = header.nextElementSibling;
            while (nextElement && nextElement.tagName === 'LI') {
                nextElement.setAttribute('data-parent-level', level.toString());
                nextElement = nextElement.nextElementSibling;
            }
            
            header.setAttribute('data-collapse-initialized', 'true');
            header.addEventListener('click', function() {
                const currentLevel = parseInt(this.getAttribute('data-level') || '0');
                
                // このヘッダーの後にある同じセクションのli要素を取得
                const sectionItems = [];
                let nextElement = this.nextElementSibling;
                
                while (nextElement && nextElement.tagName === 'LI') {
                    sectionItems.push(nextElement);
                    nextElement = nextElement.nextElementSibling;
                }
                
                // 折り畳み状態をトグル
                const isCollapsed = this.classList.contains('collapsed');
                
                if (isCollapsed) {
                    // 展開
                    this.classList.remove('collapsed');
                    sectionItems.forEach(item => {
                        item.classList.remove('hidden');
                        item.style.display = '';
                    });
                    
                    // 子セクションも展開（親が展開されたので）
                    toggleChildSections(this, currentLevel, false);
                } else {
                    // 折り畳み
                    this.classList.add('collapsed');
                    sectionItems.forEach(item => {
                        item.classList.add('hidden');
                        item.style.display = 'none';
                    });
                    
                    // 子セクションも折り畳み
                    toggleChildSections(this, currentLevel, true);
                }
            });
        });
        
        // 初期状態で親が折り畳まれている子セクションを非表示にする
        headers.forEach(header => {
            const level = parseInt(header.getAttribute('data-level') || '0');
            if (level > 0 && isParentCollapsed(header, level)) {
                header.classList.add('parent-collapsed');
                header.style.display = 'none';
                
                // 子セクションのli要素も非表示
                let nextElement = header.nextElementSibling;
                while (nextElement && nextElement.tagName === 'LI') {
                    nextElement.classList.add('parent-collapsed');
                    nextElement.style.display = 'none';
                    nextElement = nextElement.nextElementSibling;
                }
            }
        });
    }
    
    // 初回実行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCollapsibleHeaders);
    } else {
        initCollapsibleHeaders();
    }
    
    // Streamlitの動的な要素更新に対応するため、定期的にチェック
    setInterval(initCollapsibleHeaders, 1000);
    </script>
    """,
        height=0,
    )


def header():
    pass
