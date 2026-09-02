from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter
from app.config import settings
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from langchain_qdrant.fastembed_sparse import FastEmbedSparse
from qdrant_client.models import (
    PointStruct, 
    SparseVector, 
    VectorParams, 
    SparseVectorParams, 
    Distance, 
    SparseIndexParams
)
import os
from uuid import uuid4
from dataclasses import dataclass

# -----------------------------------------------------------------------------------------------------------
# Startup Tasks
# -----------------------------------------------------------------------------------------------------------
@dataclass
class RagResources:
    llm: ChatOpenAI
    qdrant_client: QdrantClient
    embedding: FastEmbedEmbeddings
    sparse_embedding: FastEmbedSparse
    md_splitter: MarkdownTextSplitter
    splitter: RecursiveCharacterTextSplitter

def load_qdrant():
    qdrant_client = QdrantClient(url="http://localhost:6333")

    if not qdrant_client.collection_exists(settings.collection_name): # Creating qdrant collection if it doesn't exist
        qdrant_client.create_collection(
            collection_name=settings.collection_name,
            vectors_config={
                "dense": VectorParams(
                size=384,
                distance=Distance.COSINE
            )},
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                index=SparseIndexParams(
                    on_disk=False
                )
            )}
        )

    return qdrant_client

def load_embedding():
    cache_path = os.path.expanduser("~/.cache/fastembed")
    embedding = FastEmbedEmbeddings(cache_dir=cache_path)
    sparse_embedding = FastEmbedSparse("Qdrant/bm25", cache_dir=cache_path)
    return embedding, sparse_embedding

def load_splitters():
    md_splitter = MarkdownTextSplitter()
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return md_splitter, splitter


def load_rag_resources():
    embedding, sparse_embedding = load_embedding()
    md_splitter, splitter = load_splitters()
    return RagResources(
        llm=ChatOpenAI(
            base_url=settings.base_url,
            api_key=settings.openai_api_key,
            model=settings.openai_model
        ),
        qdrant_client=load_qdrant(),
        embedding=embedding,
        sparse_embedding=sparse_embedding,
        md_splitter=md_splitter,
        splitter=splitter
    )
# -----------------------------------------------------------------------------------------------------------
# RAG Chain
# -----------------------------------------------------------------------------------------------------------

def process_rag(resources, domain, dir: str):
    directory = Path(dir)
    loader = DirectoryLoader(directory)
    documents = loader.load()

    chunks = _split_documents(resources, documents)
    for chunk in chunks:
        chunk.metadata["source"] = domain

    _create_vectorstore(resources, domain, chunks)

def _split_documents(resources, documents):
    splits = resources.md_splitter.split_documents(documents)
    chunks = resources.splitter.split_documents(splits)

    return chunks

def _create_vectorstore(resources, domain, chunks):
    global uuid4
    texts = [chunk.page_content for chunk in chunks]
    embeddings = resources.embedding.embed_documents(texts)
    sparse_embeddings = list(resources.sparse_embedding.embed(texts))

    points = []

    # Constructing Points
    for idx, emb in enumerate(embeddings):
        point = PointStruct(
            id=str(uuid4()),
            vector={
                "dense":emb,
                "sparse": SparseVector(
                    indices=sparse_embeddings[idx].indices.tolist(),
                    values=sparse_embeddings[idx].values.tolist()
                )
            },
            payload={
                 "page_content": chunks[idx].page_content,
                 "metadata": {"source": domain}
            }
        )
        points.append(point)

    # Uploading points to Qdrant
    resources.qdrant_client.upsert(settings.collection_name, points)

