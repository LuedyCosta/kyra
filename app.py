import os
import glob
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

# Leitura automatica do Cofre Fixo no GitHub (pasta /vault)
github_vault_context = ""
vault_files = glob.glob("vault/*.md")

if vault_files:
    github_vault_context += "\n\n--- BASE DE CONHECIMENTO FIXA (VAULT) ---\n"
    for file_path in vault_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_name = os.path.basename(file_path)
                github_vault_context += f"\n[Nota Fixa: {file_name}]\n{content}\n"
        except Exception as e:
            pass

# Sidebar para Credenciais e Uploads Temporarios
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("Cofre do Obsidian (Fixos)")
    if vault_files:
        st.caption("Notas ativas no servidor:")
        for vf in vault_files:
            st.text(f"• {os.path.basename(vf)}")
    else:
        st.caption("Nenhuma nota fixa encontrada na pasta /vault.")

    st.divider()
    st.header("Contexto Adicional (Sessão)")
    uploaded_files = st.file_uploader(
        "Carregar notas temporárias", 
        type=["md", "txt"], 
        accept_multiple_files=True
    )

if not api_key:
    st.info("Insira sua Gemini API Key na barra lateral para iniciar.")
    st.stop()

# Concatenação das notas dinâmicas enviadas pelo uploader
session_vault_context = ""
if uploaded_files:
    session_vault_context = "\n\n--- NOTAS TEMPORÁRIAS DA SESSÃO ---\n"
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        session_vault_context += f"\n[Arquivo Temporário: {file.name}]\n{content}\n"

# Injeção completa de instrução do sistema
full_system_instruction = SYSTEM_PROMPT + github_vault_context + session_vault_context

genai.configure(api_key=api_key)
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
