import os
import json
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS

# === 1. Carregar JSON ===
# Tentar primeiro o arquivo com IDs e títulos, depois o arquivo simples
json_files = ["iso17025.json"]
data = None

for json_path in json_files:
    if os.path.exists(json_path):
        print(f"🔍 Carregando arquivo: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        break

if data is None:
    raise FileNotFoundError("Nenhum arquivo JSON da ISO 17025 encontrado!")

# Verificar a estrutura do JSON e processar adequadamente
if isinstance(data, list) and len(data) > 0:
    first_item = data[0]
    
    if "titulo" in first_item and "texto" in first_item:
        # Formato com título e texto separados
        texts = [f"{item['titulo']}. {item['texto']}" for item in data if item.get('texto', '').strip()]
        print(f"📄 Formato detectado: JSON estruturado com títulos")
    elif "texto" in first_item:
        # Formato apenas com texto
        texts = [item['texto'] for item in data if item.get('texto', '').strip()]
        print(f"📄 Formato detectado: JSON simples com textos")
    else:
        raise ValueError("Formato JSON não reconhecido!")
else:
    raise ValueError("Arquivo JSON vazio ou formato inválido!")
print(f"📄 Total de requisitos ISO 17025: {len(texts)}")

# === 2. Carregar modelo local de embeddings ===
print("🔄 Carregando modelo de embeddings (CPU only)...")
# Força uso de CPU para evitar problemas de CUDA
import torch
torch.cuda.is_available = lambda : False

# Usar modelo mais leve que funciona bem em CPU
embedder = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
print("✅ Modelo carregado com sucesso (CPU)")


# === 3. Gerar embeddings em lote ===
embeddings = []
batch_size = 16
for i in tqdm(range(0, len(texts), batch_size), desc="🔍 Gerando embeddings"):
    batch = texts[i:i+batch_size]
    batch_emb = embedder.encode(batch, show_progress_bar=False, convert_to_numpy=True)
    embeddings.extend(batch_emb)

embeddings = np.array(embeddings)
print(f"✅ Embeddings gerados: {embeddings.shape}")

# === 4. Criar índice FAISS para consultoria em qualidade laboratorial ===
text_embeddings = list(zip(texts, embeddings))
faiss_index = FAISS.from_embeddings(text_embeddings, embedder)
faiss_index.save_local("iso17025_faiss_qwen")

print("💾 Base vetorial salva em 'iso17025_faiss_qwen'")
print("✅ Sistema RAG para consultoria em qualidade laboratorial pronto!")
