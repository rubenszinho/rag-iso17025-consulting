# RAG Laboratory Quality Consulting System

Sistema de Recuperação Aumentada por Geração (RAG) para consultoria em qualidade laboratorial, baseado na norma ISO/IEC 17025:2017.

## 📁 Estrutura do Projeto

```
rag-iso17025-consulting/
├── api/                    # Backend FastAPI
│   ├── Dockerfile
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py             # API endpoints
│   ├── create_vector_store.py
│   └── iso17025.json   # Base de dados normativa
├── frontend/               # Frontend Streamlit
│   ├── Dockerfile
│   ├── .env.example
│   └── app_streamlit.py
├── docker-compose.yml      # Orquestração local
└── README.md
```

## 🚀 Deploy

### Containers Individuais (Cloud)

**API Service:**
```bash
cd api
docker build -t rag-api:latest .
docker run -d -p 8000:8000 --env-file .env rag-api:latest
```

**Frontend Service:**
```bash
cd frontend
docker build -t rag-frontend:latest .
docker run -d -p 8501:8501 --env-file .env rag-frontend:latest
```

### Docker Compose (Local)

```bash
# Criar arquivos .env a partir dos exemplos
cp api/.env.example api/.env
cp frontend/.env.example frontend/.env

# Editar os arquivos .env com suas configurações

# Subir os serviços
docker-compose up -d
```

## ⚙️ Variáveis de Ambiente

### API Service (`api/.env`)

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | ✅ |
| `MODEL_NAME` | Modelo GPT (default: gpt-4o-mini) | ❌ |
| `TEMPERATURE` | Temperatura do modelo (default: 0.2) | ❌ |
| `MAX_TOKENS` | Máximo de tokens (default: 800) | ❌ |
| `K_DOCUMENTS` | Documentos recuperados (default: 5) | ❌ |

### Frontend Service (`frontend/.env`)

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `API_URL` | URL da API RAG | ✅ |

## 🔗 Endpoints

### API (porta 8000)

- `GET /health` - Health check
- `POST /ask` - Consulta RAG

### Frontend (porta 8501)

- Interface web Streamlit

## 🛠️ Tecnologias

- **Backend**: FastAPI, LangChain, FAISS, OpenAI
- **Frontend**: Streamlit
- **Embeddings**: all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **LLM**: GPT-4o-mini
