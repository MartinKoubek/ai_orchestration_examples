"""
Utility helpers for instantiating OCI-backed LLM clients used across demos.
"""

from oci_generative_ai import ChatOCIGenAI

from oci_settings import COMPARTMENT_ID, SERVICE_ENDPOINT


def get_llm(model_id: str) -> ChatOCIGenAI:
    """Return a configured OCI GenAI chat client for the requested model."""
    return ChatOCIGenAI(
        model_id=model_id,
        service_endpoint=SERVICE_ENDPOINT,
        compartment_id=COMPARTMENT_ID,
        model_kwargs={"max_tokens": 3000} if "gpt-5" not in model_id else {},
        provider="cohere" if "cohere" in model_id else "meta",
    )
