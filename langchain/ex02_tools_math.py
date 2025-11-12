"""
LangChain Math Assistant with Tool Calling

This Python script demonstrates a simple math assistant agent powered
by the `openai.gpt-4o` model (swap in other providers via the commented options)
using the **LangChain** library.

## Tools

- **add_two_numbers** — sums two numbers.
- **check_math_result** — verifies the computed result.
  (included mainly to show that multiple tools can be invoked).


## Orchestration

- The agent is built with **create_tool_calling_agent**, which creates
  a **tool-calling agent** capable of selecting and invoking tools
  automatically.
- Tools are registered with the model using bind_tools
- The workflow is executed through an AgentExecutor, which handles
    the interaction loop between the LLM and the tools.

## Behavior

    The agent receives a math problem as a user prompt.

    It decides which tools to call (add_two_numbers,
    check_math_result) and in what order.

    The final output includes both the intermediate tool results and the
    assistant’s natural language explanation.
"""

from typing import Annotated
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# 0.1.3 version does not support tool calls in openai -> Invalid parameter: 'toolCallId' of ... not found in 'toolCalls' of previous message.
#from langchain_oci import ChatOCIGenAI

# this is the newest library (2025/9/3) where tool-calling works
from oci_generative_ai import ChatOCIGenAI
from oci_config_loader import get_compartment_id, get_service_endpoint


# Tool decorating with parse_docstring + Args
@tool(parse_docstring=True)
def add_two_numbers(x: float, y: float) -> float:
    """
    Adds two numbers and returns the result.

    Args:
        x: first int
        y: second int
    """
    return x + y


# Tool annotating
@tool
def check_math_result(
        input_text: Annotated[str, "The text containing a math result to check"]
        ) -> bool:
    """
    Checks if the provided math result is correct.
    """
    return "10.7" in input_text


# Tool decorating or annotating has the same effect - see ex04_tools_summarization
TOOLS = [add_two_numbers, check_math_result]

# Define the prompt template for the agent
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful math assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),  # do not forget to add this line
])


USER_PROMPT = "Compute 4.8 plus 5.9 and confirm the sum is correct."


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

    print(f"\nModel: {model_id}")
    # Set up the language model
    llm = ChatOCIGenAI(
        model_id=model_id,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id,
        model_kwargs={"max_tokens": 3000} if "gpt-5" not in model_id else {"max_completion_tokens": 3000},
        provider="cohere" if "cohere" in model_id else "meta"
    )

    # Bind tools to the language model
    # Llama is able to use only one tool per LLM call
    # What happens: This step tells the language model which external functions it is allowed to call.
    llm_with_tools = llm.bind_tools(TOOLS)

    # Create an agent with the language model and tools — a wrapper around the LLM that knows how to:
    #   Read user input,
    #   Decide (using the prompt & reasoning) whether to call a tool or answer directly.
    #   Format its tool requests and interpret tool outputs.
    agent = create_tool_calling_agent(llm=llm_with_tools,
                                      tools=TOOLS,
                                      prompt=PROMPT_TEMPLATE)

    # Wrap the agent in an executor
    # The AgentExecutor is the orchestrator:
    #   Runs the agent loop.
    #   Sends tool calls to the actual tool implementations.
    #   Feeds results back to the agent.
    #   Handles retries, parsing errors, and final output delivery.
    agent_executor = AgentExecutor(agent=agent,
                                   tools=TOOLS,
                                   handle_parsing_errors=True,
                                   verbose=False,
                                   return_intermediate_steps=False)

    # Invoke the agent with a sample input
    try:
        response = agent_executor.invoke({"input": USER_PROMPT}).get('output')
    except Exception as e:
        response = f"Not able to run due to {e}"
    print(f"Response: {response}")

    '''
    output:
    Model: openai.gpt-4o
    Response: The sum of 4.8 and 5.9 is 10.7, and this result is confirmed to be correct.
    '''
