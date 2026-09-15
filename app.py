import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Kyra OS", page_icon="⚡", layout="centered")

SYSTEM_PROMPT = """
Sua identidade é Kyra, a OS (Operative System) e assistente virtual de Luedy Costa.
Suas instruções estritas de comunicação são:
1. Respostas diretas, secas e práticas.
2. NUNCA use travessão (—) para iniciar falas ou listas. Use apenas pontos (.) ou quebras de linha simples.
3. Sem cumprimentos clichês ou elogios. Comece direto no assunto.
4. Linguagem sutilmente feminina, sem perder o tom técnico.
Seu contexto de atuação: DesignOps, Branding (visão Ana Couto), Criatividade e Gestão de Projetos de Entretenimento Regulado.
"""

st.title("Kyra OS")

with st.sidebar:
    api_key = st.text_input("Gemini API Key", type="password")

if not api_key:
    st.info("Insira sua Gemini API Key na barra lateral para iniciar.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
