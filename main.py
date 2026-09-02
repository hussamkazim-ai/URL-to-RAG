from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import router
from app.url_processor import(
    load_firecrawl,
    ensure_temp_folder
)
from app.rag_chain import load_rag_resources
from app.rag_chat import load_chat_resources
import logging

# -------------------------------------------------------------------------------------------------
# Setting up the logger
# -------------------------------------------------------------------------------------------------

logger = logging.getLogger("logger")
file_handler = logging.FileHandler("logs.log", "a")
ch = logging.StreamHandler()
format = logging.Formatter("%(asctime)s - %(message)s")

file_handler.setFormatter(format)
ch.setFormatter(format)
ch.setLevel(logging.DEBUG)

logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -------------------------------------------------------------------------------------------------
    # Startup Tasks
    # -------------------------------------------------------------------------------------------------
    app.state.rag_resources = load_rag_resources()
    load_chat_resources(app.state.rag_resources)

    logger.info("Loaded the dependencies succesfully")
    
    yield

    # -------------------------------------------------------------------------------------------------
    # Shutdown Tasks
    # -------------------------------------------------------------------------------------------------


app = FastAPI(
    title="URL to RAG",
    description="Turn any URL into a vector store and chat with it",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)