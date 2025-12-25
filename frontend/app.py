import streamlit as st
from config import PAGE_TITLE, PAGE_ICON
from chat_handler import ChatHandler
from ui_components import render_sidebar, render_chat_history, render_sources


def main():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="centered"
    )

    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.markdown("Задавайте вопросы по сюжету и персонажам романа Ф.М. Достоевского")

    chat_handler = ChatHandler()
    render_sidebar()
    render_chat_history(chat_handler.get_messages())

    prompt = None

    if "selected_question" in st.session_state:
        prompt = st.session_state.selected_question
        del st.session_state.selected_question

    if not prompt:
        prompt = st.chat_input("Ваш вопрос:")

    if prompt:
        chat_handler.add_user_message(prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Думаю..."):
                result = chat_handler.process_question(prompt)

                if result["success"]:
                    st.markdown(result["answer"])
                    render_sources(result["sources"])
                    chat_handler.add_assistant_message(
                        result["answer"],
                        result["sources"]
                    )
                else:
                    st.error(result["error"])
                    chat_handler.add_assistant_message(result["error"])


if __name__ == "__main__":
    main()
