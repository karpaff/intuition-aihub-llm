import streamlit as st
from typing import List, Dict
from config import EXAMPLE_QUESTIONS, API_URL


def render_sidebar():
    with st.sidebar:
        st.header("💡 Примеры вопросов")
        st.markdown("Нажмите на вопрос, чтобы задать его:")

        for i, question in enumerate(EXAMPLE_QUESTIONS):
            if st.button(question, key=f"example_{i}", use_container_width=True):
                st.session_state.selected_question = question

        st.divider()

        if st.button("🗑️ Очистить историю чата", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        st.markdown("### ⚙️ Настройки")
        st.text_input("URL API:", value=API_URL, disabled=True)


def render_message(message: Dict):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and "sources" in message:
            render_sources(message["sources"])


def render_sources(sources: List[Dict]):
    if not sources:
        return

    with st.expander("📖 Источники"):
        for source in sources:
            st.markdown(f"**Глава {source['chapter_n']}:**")
            st.text(source['text_chunk'])
            st.divider()


def render_chat_history(messages: List[Dict]):
    for message in messages:
        render_message(message)
