import os
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain_core.documents import Document
from openai import OpenAI
import numpy as np

# === Configurar logging detalhado ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('rag_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Dicionário para armazenar estatísticas de requisições
query_stats = {
    'total_queries': 0,
    'total_response_time_ms': 0,
    'min_response_time_ms': float('inf'),
    'max_response_time_ms': 0,
    'queries': []
}

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
    query_start_time = time.time()
    
    question = req.question.strip()
    if not question:
        logger.warning("❌ Consulta vazia recebida")
        return {"error": "Consulta vazia"}

    logger.info(f"🔍 Nova consulta recebida: '{question}'")
    
    try:
        # === Recuperar requisitos mais relevantes da ISO 17025 ===
        retrieval_start = time.time()
        retrieved_docs = faiss_index.similarity_search(question, k=5)
        retrieval_time = (time.time() - retrieval_start) * 1000  # em ms
        
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        logger.info(f"Recuperados {len(retrieved_docs)} documentos em {retrieval_time:.2f}ms")
        
        # Registrar documentos recuperados
        doc_refs = [doc.metadata.get('section', 'Unknown') if hasattr(doc, 'metadata') else f'Doc {i}' 
                   for i, doc in enumerate(retrieved_docs)]
        logger.info(f"📚 Documentos: {', '.join(doc_refs)}")

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
        logger.info("🤖 Gerando resposta com GPT-4o-mini...")
        generation_start = time.time()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        generation_time = (time.time() - generation_start) * 1000  # em ms
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"Resposta gerada em {generation_time:.2f}ms")
        
        # === Calcular tempo total ===
        total_time = (time.time() - query_start_time) * 1000  # em ms
        
        # === Atualizar estatísticas ===
        query_stats['total_queries'] += 1
        query_stats['total_response_time_ms'] += total_time
        query_stats['min_response_time_ms'] = min(query_stats['min_response_time_ms'], total_time)
        query_stats['max_response_time_ms'] = max(query_stats['max_response_time_ms'], total_time)
        
        query_info = {
            'timestamp': datetime.now().isoformat(),
            'query': question,
            'total_time_ms': round(total_time, 2),
            'retrieval_time_ms': round(retrieval_time, 2),
            'generation_time_ms': round(generation_time, 2),
            'documents_retrieved': len(retrieved_docs),
            'document_refs': doc_refs,
            'answer_length': len(answer),
            'status': 'success'
        }
        query_stats['queries'].append(query_info)
        
        # Log das métricas
        logger.info(f"⏱️  Tempo total: {total_time:.2f}ms (Recuperação: {retrieval_time:.2f}ms + Geração: {generation_time:.2f}ms)")
        logger.info(f"📊 Estatísticas acumuladas - Consultas: {query_stats['total_queries']}, "
                   f"Tempo médio: {query_stats['total_response_time_ms']/query_stats['total_queries']:.2f}ms")

        # === Retornar resultado da consultoria ===
        return {
            "question": question,
            "answer": answer,
            "context_used": [doc.page_content[:250] for doc in retrieved_docs],
            "documents_retrieved": len(retrieved_docs),
            "metrics": {
                "total_time_ms": round(total_time, 2),
                "retrieval_time_ms": round(retrieval_time, 2),
                "generation_time_ms": round(generation_time, 2)
            },
            "system_info": {
                "scenario": "Consultoria em Qualidade Laboratorial",
                "standard": "ISO/IEC 17025:2017",
                "method": "RAG (Retrieval-Augmented Generation)"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar consulta: {str(e)}", exc_info=True)
        error_query = {
            'timestamp': datetime.now().isoformat(),
            'query': question,
            'status': 'error',
            'error': str(e)
        }
        query_stats['queries'].append(error_query)
        return {"error": str(e), "status": "failed"}

@app.get("/")
async def root():
    return {
        "message": "Assistente RAG para Consultoria em Qualidade Laboratorial está online! 🚀",
        "scenario": "Consultoria técnica especializada",
        "standard": "ISO/IEC 17025:2017",
        "technology": "RAG (Retrieval-Augmented Generation)",
        "endpoints": ["/ask", "/health", "/stats"],
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do sistema."""
    return {
        "status": "healthy",
        "faiss_index": "loaded",
        "embeddings_model": "all-MiniLM-L6-v2",
        "llm_model": "gpt-4o-mini",
        "documents_indexed": "156 requisitos ISO 17025",
        "total_queries_processed": query_stats['total_queries']
    }

@app.get("/stats")
async def get_statistics():
    """
    Endpoint para coletar estatísticas de desempenho do sistema.
    Útil para análise e geração de relatórios.
    """
    if query_stats['total_queries'] == 0:
        return {
            "message": "Nenhuma consulta processada ainda",
            "total_queries": 0
        }
    
    avg_response_time = query_stats['total_response_time_ms'] / query_stats['total_queries']
    
    stats = {
        "summary": {
            "total_queries": query_stats['total_queries'],
            "avg_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(query_stats['min_response_time_ms'], 2),
            "max_response_time_ms": round(query_stats['max_response_time_ms'], 2),
            "total_response_time_ms": round(query_stats['total_response_time_ms'], 2),
        },
        "queries": query_stats['queries'],
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"📊 Estatísticas solicitadas - Total de consultas: {query_stats['total_queries']}")
    return stats

@app.get("/export-metrics")
async def export_metrics():
    """
    Endpoint para exportar métricas em JSON para uso em relatórios.
    """
    if query_stats['total_queries'] == 0:
        return {"error": "Sem dados para exportar"}
    
    avg_response_time = query_stats['total_response_time_ms'] / query_stats['total_queries']
    
    metrics = {
        "generated_at": datetime.now().isoformat(),
        "system": {
            "name": "Assistente RAG para Consultoria em Qualidade Laboratorial",
            "standard": "ISO/IEC 17025:2017",
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimensions": 384,
            "documents_indexed": 156,
            "llm_model": "gpt-4o-mini",
            "temperature": 0.2
        },
        "performance": {
            "total_queries_processed": query_stats['total_queries'],
            "avg_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(query_stats['min_response_time_ms'], 2),
            "max_response_time_ms": round(query_stats['max_response_time_ms'], 2),
            "std_deviation_ms": round(
                np.std([q['total_time_ms'] for q in query_stats['queries'] if q.get('status') == 'success']),
                2
            ) if query_stats['queries'] else 0
        },
        "queries_detail": [q for q in query_stats['queries'] if q.get('status') == 'success']
    }
    
    logger.info("📤 Métricas exportadas para relatório")
    return metrics
