from datetime import datetime

from agents.lifecycle import AgentHooks

# PDF処理用のライブラリ

import streamlit as st
from src.agent_sdk.tools.display_utils import display_generic_tool_result, display_tool_start
from src.streamlit.functions.state import get_page_state, set_page_state


class StreamlitAgentHooks(AgentHooks):
    """Streamlitでツールの実行結果を表示し、messages_historyに保存するためのエージェントフック"""

    def __init__(self):
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def on_tool_start(self, context, agent, tool):
        """ツール実行開始時の処理"""
        tool_description = getattr(tool, "description", "No description available")
        html_contents = display_tool_start(tool.name, tool_description)

        messages_history = get_page_state("messages_history", [])
        tool_start_entry = {
            "type": "tool_start",
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "tool_description": tool_description,
            "agent_name": agent.name,
            "html_contents": html_contents,
        }
        messages_history.append(tool_start_entry)
        set_page_state("messages_history", messages_history)

        st.markdown(html_contents, unsafe_allow_html=True)

    async def on_tool_end(self, context, agent, tool, result):
        """ツール実行終了時の処理"""
        html_contents = None

        if html_contents is None:
            html_contents = display_generic_tool_result(result, tool.name)

        messages_history = get_page_state("messages_history", [])
        tool_end_entry = {
            "type": "tool_end",
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "result": str(result)[:1000] if result else "No result",
            "html_contents": html_contents,
            "agent_name": agent.name,
        }
        messages_history.append(tool_end_entry)
        set_page_state("messages_history", messages_history)

        st.markdown(html_contents, unsafe_allow_html=True)
