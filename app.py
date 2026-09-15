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

# Sidebar de Configuração e Contexto
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("Contexto Obsidian (.md)")
    uploaded_files = st.file_uploader(
        "Carregar notas do cofre", 
        type=["md", "txt"], 
        accept_multiple_files=True
    )

if not api_key:
    st.info("Insira sua Gemini API Key na barra lateral para iniciar.")
    st.stop()

# Leitura e concatenação dos arquivos do Obsidian carregados
vault_context = ""
if uploaded_files:
    vault_context = "\n\n--- NOTAS DO OBSIDIAN CARREGADAS ---\n"
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        vault_context += f"\n[Arquivo: {file.name}]\n{content}\n"

genai.configure(api_key=api_key)
full_system_instruction = SYSTEM_PROMPT + vault_context
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=full_system_instruction
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
