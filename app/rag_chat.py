from app.config import settings
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
# ---------------------------------------------------------------------------------------------------------------------------------
# Loading Retriever on Startup
# ---------------------------------------------------------------------------------------------------------------------------------
retriever = None
prompt = None
llm = None
parser = None

def load_chat_resources(resources):
    global retriever
    global prompt
    global llm
    global parser

    client = QdrantClient(url="http://localhost:6333/")
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=settings.collection_name,
        embedding=resources.embedding,
        sparse_embedding=resources.sparse_embedding,
        vector_name="dense",
        sparse_vector_name="sparse",
        retrieval_mode=RetrievalMode.HYBRID
    )
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant and your job is to answer user queries from the given context.
        If the context doesn't contain a right answer to user query, then just say 'I don't have enough information'
        context: {context}
        query: {query}"""
    )
    llm = resources.llm
    parser = StrOutputParser()


# ---------------------------------------------------------------------------------------------------------------------------------
# Main Chatting Logic
# ---------------------------------------------------------------------------------------------------------------------------------
async def chat(query):

    chain = prompt | llm | parser

    retrieved_docs = _format_docs(retriever.invoke(query))
    response = chain.invoke({"context": retrieved_docs, "query": query})

    return response

async def stream():
    async def generator(query):
        retrieved_docs = _format_docs(retriever.invoke(query))
        llm.streaming = True
        chain = prompt | llm | parser
        for token in chain.stream({"context": retrieved_docs, "query": query}):
            if token:
                yield json.dumps({"type": "content", "text": token})
    
    return generator

def _format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])