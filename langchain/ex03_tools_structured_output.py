"""
Structured output demo for OCI LangChain models.

This script binds a Pydantic schema and uses `with_structured_output`
with the `openai.gpt-4o` model by default to extract key fields from a
short user bio. Swap in other models via the commented options.
"""


from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from langchain_oci import ChatOCIGenAI
from oci_config_loader import get_compartment_id, get_service_endpoint

class ExtractFields(BaseModel):
    """Extract important fields from text
    """
    name: str = Field(..., description="get a person's name")
    location: str = Field(..., description="get a person's location")
    years: str = Field(..., description="the number of years of professional experience from free-form text")

# Define the prompt template for the agent
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant which use tools to extract information and parse them to json format"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),  # do not forget to add this line
])


USER_PROMPT = "Hello, I'm Elena Novak based in Prague. You can reach me at elena.novak@example.com. I've worked in data science since 2014."

if __name__ == "__main__":

    print(f"Question: {USER_PROMPT}")
    compartment_id = get_compartment_id()
    service_endpoint = get_service_endpoint()

    model_id = "openai.gpt-4o"
    # Alternative models to try:
    # model_id = "cohere.command-a-03-2025"
    # model_id = "meta.llama-4-maverick-17b-128e-instruct-fp8"  # Parallel tool call not supported yet.
    # model_id = "xai.grok-3-fast"
    # model_id = "openai.gpt-5"

    # Set up the language model
    llm = ChatOCIGenAI(
        model_id=model_id,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id,
        model_kwargs={"max_tokens": 3000} if "gpt-5" not in model_id else {"max_completion_tokens": 3000},
        provider="cohere" if "cohere" in model_id else "meta",
    )

    # Bind tools to the language model (not implemented for Meta models)
    structured_llm = llm.with_structured_output(ExtractFields)
    response = structured_llm.invoke(USER_PROMPT)

    print(f"Model: {model_id}, response: {response.model_dump()}")

    """
    Question: Hello, I'm Elena Novak based in Prague. You can reach me at elena.novak@example.com. I've worked in data science since 2014.
    Model: openai.gpt-4o, response: {'name': 'Elena Novak', 'location': 'Prague', 'years': "I've worked in data science since 2014."}
    """
