from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.api import(
    process_url,
    answer_query,
    stream_query,
    delete_data
)
from app.models import (
    ChatResponse
)

router = APIRouter()

router.add_api_route("/process-url/",   process_url,    methods=["POST"],   description="e.g. https://hussamkazim.com/")
router.add_api_route("/query/",         answer_query,   methods=["POST"],   response_model=ChatResponse)
router.add_api_route("/stream/",        stream_query,   methods=["POST"],   response_class=StreamingResponse)
router.add_api_route("/delete-data/",   delete_data,    methods=["DELETE"], description="e.g. hussamkazim.com, seorank.com")