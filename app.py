import os
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client (reads API key from environment variable OPENAI_API_KEY)
client = OpenAI()

# ---------------------------
# Helpers
# ---------------------------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your programming joke bot. Ask me for a joke about any language, framework, or bug!"
            }
        ]
    if "style" not in st.session_state:
        st.session_state.style = "One-liner"
    if "topic" not in st.session_state:
        st.session_state.topic = "Python"
    if "length" not in st.session_state:
        st.session_state.length = "Short"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.8


def get_system_prompt(style: str, topic: str, length: str) -> str:
    length_guidance = {
        "Short": "Keep it to 1-2 lines.",
        "Medium": "Keep it to ~3-5 lines.",
        "Long": "You can go up to ~8 lines, but stay punchy."
    }.get(length, "Keep it concise.")
    return (
        "You are a witty, clean programming comedian. "
        f"Tell programming-related jokes only. Style preference: {style}. "
        f"If a topic is provided, focus on: {topic}. "
        f"{length_guidance} "
        "Avoid profanity, stereotypes, or sensitive content. "
        "Be clever, concise, and punchy. If the user asks for multiple jokes, number them."
    )


def build_api_messages(system_prompt: str, chat_history: list) -> list:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    return messages


def get_joke_reply(model: str, messages: list, temperature: float, max_tokens: int = 400) -> str:
    response = client.chat.completions.create(
        model=model,  # "gpt-4"
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def render_chat(chat_history: list):
    for msg in chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# ---------------------------
# Streamlit App
# ---------------------------
def main():
    st.set_page_config(page_title="Programming Joke Bot", page_icon="🃏")
    st.title("🃏 Programming Joke Bot")

    init_session()

    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        # Optional: allow user to paste API key (falls back to env var if empty)
        api_key_input = st.text_input("OpenAI API Key (optional)", type="password")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input

        st.session_state.style = st.selectbox(
            "Joke style",
            ["One-liner", "Pun", "Dad joke", "Knock-knock", "Story"],
            index=["One-liner", "Pun", "Dad joke", "Knock-knock", "Story"].index(st.session_state.style)
        )
        st.session_state.topic = st.text_input("Topic (e.g., Python, Git, regex)", st.session_state.topic)
        st.session_state.length = st.selectbox(
            "Length",
            ["Short", "Medium", "Long"],
            index=["Short", "Medium", "Long"].index(st.session_state.length)
        )
        st.session_state.temperature = st.slider("Creativity", 0.0, 1.0, st.session_state.temperature, 0.05)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("New Chat"):
                st.session_state.messages = [
                    {"role": "assistant", "content": "New chat started! What topic should the next joke be about?"}
                ]
        with col2:
            if st.button("Tell me a joke now"):
                user_prompt = f"Tell me a {st.session_state.style.lower()} joke about {st.session_state.topic}."
                st.session_state.messages.append({"role": "user", "content": user_prompt})
                system_prompt = get_system_prompt(st.session_state.style, st.session_state.topic, st.session_state.length)
                api_messages = build_api_messages(system_prompt, st.session_state.messages)
                try:
                    reply = get_joke_reply(
                        model="gpt-4",
                        messages=api_messages,
                        temperature=st.session_state.temperature
                    )
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.caption("Tip: Leave the API key blank if you already set OPENAI_API_KEY in your environment.")

    # Render chat history
    render_chat(st.session_state.messages)

    # Chat input
    user_input = st.chat_input("Ask for a programming joke or suggest a topic...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Crafting a brilliant punchline..."):
                try:
                    system_prompt = get_system_prompt(st.session_state.style, st.session_state.topic, st.session_state.length)
                    api_messages = build_api_messages(system_prompt, st.session_state.messages)
                    reply = get_joke_reply(
                        model="gpt-4",
                        messages=api_messages,
                        temperature=st.session_state.temperature
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
                    return
                st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()