import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain_core.documents import Document
from openai import OpenAI
import numpy as np

# === 1. Carregar variáveis de ambiente ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"🔹 OPENAI_API_KEY encontrada: {'sim' if api_key else 'não'}")
if not api_key:
    raise ValueError("❌ Nenhuma chave OPENAI_API_KEY encontrada no arquivo .env")

FAISS_PATH = "iso17025_faiss_qwen"

# === 2. Definir wrapper para embeddings CPU ===
class CPUEmbeddings(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Força uso de CPU para compatibilidade
        import torch
        torch.cuda.is_available = lambda : False
        self.model = SentenceTransformer(model_name, device='cpu')

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.model.encode(t, convert_to_numpy=True).tolist() for t in texts]

# === 3. Inicializar embeddings e FAISS ===
print("🔹 Carregando modelo de embeddings (CPU)...")
embeddings = CPUEmbeddings()

print("🔹 Carregando índice FAISS...")
faiss_index = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

# === 4. Inicializar cliente da API OpenAI ===
print("🔹 Inicializando cliente OpenAI (responses API)...")
client = OpenAI(api_key=api_key)

# === 5. Configurar FastAPI ===
app = FastAPI(
    title="Assistente RAG para Consultoria em Qualidade Laboratorial",
    description="Sistema RAG aplicado à norma ISO/IEC 17025:2017 para consultoria técnica",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_rag(req: QueryRequest):
    """
    Endpoint principal do sistema RAG para consultoria em qualidade laboratorial.
    Recebe uma consulta, faz busca semântica na base ISO 17025 e gera resposta fundamentada.
    """
    question = req.question.strip()
    if not question:
        return {"error": "Consulta vazia"}

    # === Recuperar requisitos mais relevantes da ISO 17025 ===
    retrieved_docs = faiss_index.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # === Montar prompt contextualizado para consultoria ===
    prompt = f"""
Você é um consultor técnico especializado em qualidade laboratorial que utiliza a norma ISO/IEC 17025:2017.
Responda à consulta usando APENAS as informações do contexto fornecido dos requisitos da norma.

Instruções:
- Seja preciso e técnico
- Cite os números das seções quando relevante (ex: "conforme item 6.2.5", "seção 7.4.1")
- Mantenha o foco na aplicação prática para laboratórios
- Se a informação não estiver no contexto, indique claramente

Contexto da ISO/IEC 17025:2017:
{context}

Consulta do cliente: {question}

Resposta técnica:
"""

    # === Chamar o modelo GPT para gerar resposta de consultoria ===
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"❌ Erro ao gerar resposta de consultoria: {str(e)}"

    # === Retornar resultado da consultoria ===
    return {
        "question": question,
        "answer": answer,
        "context_used": [doc.page_content[:250] for doc in retrieved_docs],
        "documents_retrieved": len(retrieved_docs),
        "system_info": {
            "scenario": "Consultoria em Qualidade Laboratorial",
            "standard": "ISO/IEC 17025:2017",
            "method": "RAG (Retrieval-Augmented Generation)"
        }
    }

@app.get("/")
async def root():
    return {
        "message": "Assistente RAG para Consultoria em Qualidade Laboratorial está online! 🚀",
        "scenario": "Consultoria técnica especializada",
        "standard": "ISO/IEC 17025:2017",
        "technology": "RAG (Retrieval-Augmented Generation)",
        "endpoints": ["/ask", "/health"],
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do sistema."""
    return {
        "status": "healthy",
        "faiss_index": "loaded",
        "embeddings_model": "Qwen3-Embedding-0.6B",
        "llm_model": "gpt-4o-mini",
        "documents_indexed": "156 requisitos ISO 17025"
    }
