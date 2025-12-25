import streamlit as st
import requests
from typing import Dict, List
from api_client import RagApiClient


class ChatHandler:
    def __init__(self):
        self.api_client = RagApiClient()
        self._init_session_state()

    def _init_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def add_user_message(self, content: str):
        st.session_state.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content: str, sources: List[Dict] = None):
        message = {
            "role": "assistant",
            "content": content
        }
        if sources:
            message["sources"] = sources
        st.session_state.messages.append(message)

    def process_question(self, question: str) -> Dict:
        try:
            data = self.api_client.get_answer(question)
            return {
                "success": True,
                "answer": data["answer"],
                "sources": data.get("sources", [])
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка при обращении к API: {str(e)}"
            }

    def get_messages(self) -> List[Dict]:
        return st.session_state.messages
