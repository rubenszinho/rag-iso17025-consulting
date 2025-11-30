# RAG Laboratory Quality Consulting System

Sistema de Recuperação Aumentada por Geração (RAG) para consultoria em qualidade laboratorial, baseado na norma ISO/IEC 17025:2017.

## Estrutura do Projeto

```
rag-iso17025-consulting/
├── api/                    # Backend FastAPI
│   ├── Dockerfile          # Otimizado com cache de dependências
│   ├── .dockerignore
│   ├── .env.example
│   ├── requirements.txt
│   ├── main.py
│   ├── create_vector_store.py
│   └── iso17025.json
├── frontend/               # Frontend Streamlit
│   ├── Dockerfile          # Otimizado com cache de dependências
│   ├── .dockerignore
│   ├── .env.example
│   └── app_streamlit.py
├── docker-compose.yml      # Orquestração local
├── build.sh                # Script de build otimizado
├── .dockerignore
└── README.md
```

## Deployment Rápido

### Docker Compose (Local/Desenvolvimento)

```bash
# Criar arquivos .env a partir dos exemplos
cp api/.env.example api/.env
cp frontend/.env.example frontend/.env

# Editar os arquivos .env com suas configurações
nano api/.env

# Subir os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Containers Individuais (Cloud/Produção)

**Build da API:**
```bash
# Build rápido (com cache de dependências)
docker build -t rag-api:latest -f api/Dockerfile api/

# Executar
docker run -d \
  -p 8000:8000 \
  --env-file api/.env \
  -v vector_store:/app/iso17025_faiss_qwen \
  rag-api:latest
```

**Build do Frontend:**
```bash
# Build rápido (com cache de dependências)
docker build -t rag-frontend:latest -f frontend/Dockerfile frontend/

# Executar
docker run -d \
  -p 8501:8501 \
  -e API_URL=http://api-service-url:8000 \
  --env-file frontend/.env \
  rag-frontend:latest
```

### Script de Build Otimizado

```bash
# Build de ambos os serviços
./build.sh all v1.0.0

# Build apenas da API
./build.sh api v1.0.0

# Build apenas do Frontend
./build.sh frontend v1.0.0

# Com registry customizado
REGISTRY=myregistry.azurecr.io/myproject/ ./build.sh all v1.0.0
```

## Otimizações de Build

Os Dockerfiles foram otimizados para:

1. **Caching eficiente**: `requirements.txt` copiado primeiro para reutilizar cache
2. **Multi-stage build**: Separa compilação de produção
3. **Layers limpas**: Remove dependências desnecessárias
4. **`.dockerignore`**: Reduz build context significativamente

**Resultado**: Builds ~70% mais rápidos em iterações

## Variáveis de Ambiente

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

## Endpoints

### API (porta 8000)

- `GET /health` - Health check
- `POST /ask` - Consulta RAG

### Frontend (porta 8501)

- Interface web Streamlit
## Tecnologias

- **Backend**: FastAPI, LangChain, FAISS, OpenAI
- **Frontend**: Streamlit
- **Embeddings**: all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **LLM**: GPT-4o-mini
- **Containerização**: Docker, Docker Compose
- **Orquestração**: Suporte para Kubernetes, Docker Swarm, ECS

## Performance

Benchmark de build (primeira vez vs iterações):

| Componente | Primeira vez | Iterações | Melhoria |
|-----------|-------------|-----------|----------|
| API | ~5-7min | ~30-45s | ~90% mais rápido |
| Frontend | ~4-5min | ~20-30s | ~85% mais rápido |

O cache de dependências é automaticamente reutilizado quando apenas os arquivos de código mudam.

## Troubleshooting

### Build lento

Verifique se o Docker está usando cache:

```bash
# Com build progress detalhado
docker build --progress=plain -t rag-api:latest -f api/Dockerfile api/
```

### Conexão entre serviços

Em Docker Compose, use `http://api:8000` como `API_URL`.

### API em produção

Certifique-se que o arquivo `.env` está configurado:

```bash
docker run -d --env-file api/.env -p 8000:8000 rag-api:latest
```
