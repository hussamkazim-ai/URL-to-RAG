from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models import (
    URLRequest,
    ChatRequest,
    DeleteRequest
)
from app.url_processor import(
    is_valid_url,
    scrape_sitemap,
    scrape_links
)
from app.rag_chat import chat, stream
from app.rag_chain import process_rag
from app.delete_data import delete
from app.config import settings

# ------------------------------------------------------------------------------------------------------------
# Scraping the Site, creating & storing the vector stores in Qdrant
# ------------------------------------------------------------------------------------------------------------
async def process_url(request: Request, body: URLRequest):
    url = body.url
    domain = url.replace("https://", "")
    domain = domain.replace("/", "")

    if not is_valid_url(url):
        raise HTTPException(400, detail="Invalid URL")

    rag_resources = request.app.state.rag_resources
    # pages = await scrape_sitemap(url)
    # await scrape_links(url, domain, pages)

    process_rag(rag_resources, domain, f"{settings.temp_dir}/{domain}")
    
# ------------------------------------------------------------------------------------------------------------
# Responding to user queries
# ------------------------------------------------------------------------------------------------------------
async def answer_query(body: ChatRequest):
    query = body.query
    response = await chat(query)
    return {"response": response}

async def stream_query(body: ChatRequest):
    query = body.query
    generator = await stream()

    return StreamingResponse(generator(query), media_type="text/plain")

# ------------------------------------------------------------------------------------------------------------
# Deleting Website Data
# ------------------------------------------------------------------------------------------------------------
def delete_data(request: Request, body: DeleteRequest):
    domain = body.domain
    delete(request.app.state.rag_resources, domain)
    