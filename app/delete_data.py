from qdrant_client.models import FieldCondition, MatchValue, Filter, PointIdsList
from app.config import settings
import os

# ------------------------------------------------------------------------------------------------------------
# Main Deleting Logic
# ------------------------------------------------------------------------------------------------------------
def delete(resources, domain):
    # Removing the local directory containing the scraped data of a website
    local_path=f"{settings.temp_dir}/{domain}"
    if os.path.exists(local_path):
        for file_name in os.listdir(local_path):
            os.remove(f"{local_path}/{file_name}")
            
    # Removing the vector stores from qdrant
    client = resources.qdrant_client
    points, offset = client.scroll(
        collection_name=settings.collection_name,
        limit=100000,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.source",
                    match=MatchValue(value=domain)
                )
            ]
        )
    )
    if points:
        ids = PointIdsList(points=[point.id for point in points])
        client.delete(
            collection_name=settings.collection_name,
            points_selector=ids
        )
