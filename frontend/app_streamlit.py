import os
import requests
import streamlit as st
from datetime import datetime

# API URL configurável via variável de ambiente para deploy em containers
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = f"{API_BASE_URL}/ask"

# Page configuration
st.set_page_config(
    page_title="RAG Consulting - ISO 17025",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "RAG Laboratory Quality Consulting System powered by Rubrion"}
)

# Custom CSS styling with Rubrion colors
st.markdown("""
    <style>
    :root {
        --primary-color: #2596be;
        --dark-bg: #0f1419;
        --card-bg: #1a1f28;
        --border-color: #2a3142;
    }
    
    body {
        background-color: var(--dark-bg);
        color: #e0e0e0;
    }
    
    .main {
        background-color: var(--dark-bg);
    }
    
    .stApp {
        background-color: var(--dark-bg);
    }
    
    .header-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid var(--primary-color);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 1rem 0 0.5rem 0;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #b0b0b0;
        margin: 0.5rem 0;
    }
    
    .query-card {
        background-color: var(--card-bg);
        border-left: 4px solid var(--primary-color);
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .response-success {
        background-color: rgba(37, 150, 190, 0.1);
        border-left: 4px solid var(--primary-color);
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
    }
    
    .sidebar-info {
        background-color: var(--card-bg);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .metric-label {
        color: var(--primary-color);
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Header with logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div class="header-container">
            <img src="https://media.rubenszinho.dev/images/loading_rubrion.svg" width="120" style="margin: 0 auto; display: block; margin-bottom: 1rem;">
            <div class="header-title">RAG Consulting</div>
            <div class="header-subtitle">Assistente de Consultoria em Qualidade Laboratorial</div>
        </div>
    """, unsafe_allow_html=True)

# Informações do sistema - Sidebar
with st.sidebar:
    st.markdown("## Sobre o Sistema")
    
    # Health check
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("API Online", icon="✅")
        else:
            st.warning("⚠️ API com Problema", icon="⚠️")
    except:
        st.error("API Offline", icon="❌")
        st.caption(f"Não conseguiu conectar em: {API_BASE_URL}")
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown("""
            <div class="sidebar-info">
                <p><strong>Cenário</strong></p>
                <p style="font-size: 0.9rem; color: #b0b0b0;">Consultoria em Qualidade Laboratorial</p>
            </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown("""
            <div class="sidebar-info">
                <p><strong>Norma Base</strong></p>
                <p style="font-size: 0.9rem; color: #b0b0b0;">ISO/IEC 17025:2017</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="sidebar-info">
            <p><strong>Tecnologia: </strong>RAG (Retrieval-Augmented Generation)</p>
            <p><strong>Embeddings: </strong>all-MiniLM-L6-v2</p>
            <p><strong>Vector Store: </strong>FAISS</p>
            <p><strong>LLM: </strong>GPT-4o-mini</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Estatísticas")
    
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.metric("Documentos", "156", delta="requisitos")
    with stat_col2:
        st.metric("Seções", "4-8", delta="cobertas")


# Query examples section
st.markdown("### Exemplos de Consultas")
st.markdown("""
    <p style="color: #b0b0b0; font-size: 0.95rem;">Clique em qualquer exemplo abaixo para carregar a consulta</p>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Procedimentos Obrigatórios", use_container_width=True):
        st.session_state.example_question = "Quais procedimentos são obrigatórios segundo a norma?"

with col2:
    if st.button("Calibração de Equipamentos", use_container_width=True):
        st.session_state.example_question = "Quando devo calibrar equipamentos de medição?"

with col3:
    if st.button("Retenção de Registros", use_container_width=True):
        st.session_state.example_question = "Por quanto tempo devo reter registros de ensaio?"

with col4:
    if st.button("Manuseio de Amostras", use_container_width=True):
        st.session_state.example_question = "Onde encontro informações sobre manuseio de amostras?"

# Query input section
st.markdown("### Sua Consulta")
st.markdown("""
    <div class="query-card">
        Digite sua pergunta sobre qualidade laboratorial e o sistema recuperará informações relevantes da norma ISO 17025.
    </div>
""", unsafe_allow_html=True)

question = st.text_input(
    "Digite sua consulta:",
    value=st.session_state.get('example_question', ''),
    placeholder="Ex: Quais são os requisitos para competência do pessoal?",
    label_visibility="collapsed"
)

# Query button with improved styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit_button = st.button("Enviar Consulta", use_container_width=True, type="primary")

if submit_button:
    if not question.strip():
        st.warning("Por favor, digite uma consulta antes de enviar.")
    else:
        with st.spinner("Processando consulta..."):
            try:
                response = requests.post(API_URL, json={"question": question})
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display response with improved styling
                    st.markdown("### Resposta do Sistema")
                    st.markdown(f"""
                        <div class="response-success">
                            <p style="line-height: 1.8; color: #e0e0e0;">{data["answer"]}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Display retrieved documents
                    with st.expander("Documentos Recuperados", expanded=False):
                        st.markdown("""
                            <p style="color: #b0b0b0; font-size: 0.95rem;">
                            Trechos da norma ISO/IEC 17025 utilizados para gerar a resposta:
                            </p>
                        """, unsafe_allow_html=True)
                        
                        for i, context in enumerate(data["context_used"], 1):
                            st.markdown(f"""
                                <div style="background-color: var(--card-bg); padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 3px solid var(--primary-color);">
                                    <p style="margin: 0; color: var(--primary-color); font-weight: 600;">Documento {i}</p>
                                    <p style="margin: 0.5rem 0 0 0; color: #d0d0d0; font-size: 0.95rem;">{context}...</p>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Clear example question after use
                    if 'example_question' in st.session_state:
                        del st.session_state.example_question
                        
                else:
                    st.error(f"Erro na API: Status {response.status_code}")
                    st.info("Verifique se a API está disponível.")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Erro de Conexão")
                st.warning(f"Não foi possível conectar à API em: **{API_BASE_URL}**")
                st.info("""
                    **Possíveis causas:**
                    - API não está rodando
                    - Endereço da API incorreto
                    - Problema de rede/firewall
                    
                    **Soluções:**
                    1. Verifique se a API está em execução
                    2. Confirme o endereço em `API_URL`
                    3. Para desenvolvimento local: `http://localhost:8000`
                    4. Para Docker: `http://api:8000`
                """)
            except requests.exceptions.Timeout:
                st.error("❌ Tempo de Espera Excedido")
                st.warning("A API demorou muito para responder. Tente novamente.")
            except Exception as e:
                st.error(f"❌ Erro ao processar consulta: {str(e)}")
                st.debug(f"Detalhes: {type(e).__name__}")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #808080; font-size: 0.9rem;">
        <p>Desenvolvido por <strong>Rubrion</strong> | Powered by RAG Technology</p>
        <p>© 2024 - Todos os direitos reservados</p>
    </div>
""", unsafe_allow_html=True)
