"""
Shared embedding utility using Google Generative AI via google-genai client.
"""

from google import genai
from google.genai import types as genai_types
from app.core.config.settings import settings

# Single shared async-capable genai client
_client = genai.Client(api_key=settings.google_api_key)


async def get_embedding(text: str) -> list[float]:
    """
    Generate an embedding for the given document text.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the text embedding.
    """
    response = await _client.aio.models.embed_content(
        model=settings.embedding_model,
        contents=text,
        config=genai_types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
        ),
    )
    return response.embeddings[0].values


async def get_query_embedding(text: str) -> list[float]:
    """
    Generate an embedding optimised for query/retrieval use.

    Args:
        text: The query text to embed.

    Returns:
        A list of floats representing the query embedding.
    """
    response = await _client.aio.models.embed_content(
        model=settings.embedding_model,
        contents=text,
        config=genai_types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
        ),
    )
    return response.embeddings[0].values
