"""
Simple Chat Model Switching Example

This script demonstrates how to use the OCI Generative AI LangChain integration
to swap between multiple generative chat models using the ChatOCIGenAI class.

- It defaults to the `openai.gpt-4o` model, sending a prompt ("Share a surprising fact about the Moon.")
  to demonstrate how to obtain responses.
- Alternative model IDs are provided as commented options so you can experiment quickly.

Note:
- This example is meant for demonstration purposes; error handling is minimal.

---
"""

from oci_config_loader import get_compartment_id, get_service_endpoint
from oci_generative_ai import ChatOCIGenAI  # this is the newest library where tooling works


# OCI service endpoint for the Generative AI inference service
service_endpoint = get_service_endpoint()

# Compartment OCID where models are deployed/available
compartment_id = get_compartment_id()

if __name__ == "__main__":

    model_id = "openai.gpt-4o"
    # Alternative models to try:
    # model_id = "cohere.command-a-03-2025"
    # model_id = "meta.llama-4-maverick-17b-128e-instruct-fp8"
    # model_id = "xai.grok-3-fast"
    # model_id = "openai.gpt-5"

    # Instantiate the chat model with specified model_id, endpoint, and compartment.
    llm = ChatOCIGenAI(
        model_id=model_id,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id,
        provider="cohere" if "cohere" in model_id else "meta"
    )
    # Send a prompt and get the model's response.
    response = llm.invoke("Share a surprising fact about the Moon.")
    # Print the model used and its response.
    print(f"Model: {model_id}, Response: {response.content}")

    '''
    output:
    Model: openai.gpt-4o, Response: A surprising fact about the Moon is that it has "moonquakes." Much like earthquakes on Earth, moonquakes are seismic activities that occur on the Moon. They are believed to be caused by tidal stresses connected to the gravitational interaction between the Earth and the Moon. Interestingly, moonquakes can be quite powerful, lasting up to an hour, which is significantly longer than typical earthquakes on Earth.
    '''
