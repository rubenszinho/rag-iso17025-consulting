import os
import requests
import streamlit as st

# API URL configurável via variável de ambiente para deploy em containers
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = f"{API_BASE_URL}/ask"

st.set_page_config(page_title="Consultoria RAG", page_icon="📋", layout="centered")
st.title("� Assistente RAG para Consultoria em Qualidade Laboratorial")
st.write("Sistema de Recuperação Aumentada por Geração aplicado à norma ISO/IEC 17025:2017")

# Informações do sistema
with st.sidebar:
    st.header("ℹ️ Sobre o Sistema")
    st.write("**Cenário**: Consultoria em Qualidade Laboratorial")
    st.write("**Base documental**: ISO/IEC 17025:2017")
    st.write("**Tecnologia**: RAG (Retrieval-Augmented Generation)")
    st.write("**Embeddings**: Qwen3-0.6B")
    st.write("**Vector Store**: FAISS")
    
    st.header("📊 Estatísticas")
    st.metric("Documentos indexados", "156 requisitos")
    st.metric("Seções cobertas", "4-8 (Completas)")

# Seção de exemplos de consultas
st.subheader("💡 Exemplos de Consultas")
col1, col2 = st.columns(2)

with col1:
    if st.button("Procedimentos obrigatórios"):
        st.session_state.example_question = "Quais procedimentos são obrigatórios segundo a norma?"
    if st.button("Calibração de equipamentos"):
        st.session_state.example_question = "Quando devo calibrar equipamentos de medição?"

with col2:
    if st.button("Retenção de registros"):
        st.session_state.example_question = "Por quanto tempo devo reter registros de ensaio?"
    if st.button("Manuseio de amostras"):
        st.session_state.example_question = "Onde encontro informações sobre manuseio de amostras?"

# Campo de entrada
question = st.text_input("Digite sua consulta sobre qualidade laboratorial:", 
                        value=st.session_state.get('example_question', ''))

if st.button("🔍 Consultar Sistema RAG", type="primary"):
    if not question.strip():
        st.warning("Por favor, digite uma consulta.")
    else:
        with st.spinner("🔄 Processando consulta RAG..."):
            try:
                response = requests.post(API_URL, json={"question": question})
                if response.status_code == 200:
                    data = response.json()
                    
                    # Exibir resposta
                    st.subheader("📝 Resposta do Sistema")
                    st.success(data["answer"])
                    
                    # Exibir documentos recuperados
                    with st.expander("📚 Documentos Recuperados (Contexto Utilizado)"):
                        st.write("**Trechos da norma ISO/IEC 17025 utilizados para gerar a resposta:**")
                        for i, context in enumerate(data["context_used"], 1):
                            st.markdown(f"**Documento {i}:**")
                            st.markdown(f"🔹 {context}...")
                            st.markdown("---")
                    
                    # Limpar pergunta de exemplo após usar
                    if 'example_question' in st.session_state:
                        del st.session_state.example_question
                        
                else:
                    st.error(f"Erro na API ({response.status_code})")
            except Exception as e:
                st.error(f"Erro ao conectar à API: {e}")
                st.info("Verifique se a API está rodando em http://localhost:8000")
