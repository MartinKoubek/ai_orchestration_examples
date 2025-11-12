"""
This demo showcases how to use LangGraph for a simple math workflow.
It defines a custom tool, `add_two_numbers`, and integrates it into an
agent powered by an AI model. The agent processes a user prompt and
returns both the original question and the computed result. It relays
on Prebuilt ReAct Agent (implicit orchestration)

**User Prompt**
What is 3.5 plus 7.2 and 1.1?

The correct execution requires the agent to call the `add_two_numbers`
tool **twice**:
1. First to add 3.5 + 7.2
2. Then to add the result (10.7) + 1.1

**Expected Result**
11.8

## Model Behavior
- **Tool Support**: All tested models (except GPT-5) can call tools.
- **Llama Models**: Limited to a single tool call. This leads to incorrect
  results because the second `add_two_numbers` call cannot be made.
- **GPT-4o**: Occasionally hallucinates, invoking the tool three times
  instead of the expected two.
- **GPT-5**: Does not call tools
"""


from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

from llm_factory import get_llm

USER_PROMPT = "What is 3.5 plus 7.2 and 1.1?"


@tool(parse_docstring=True)
def add_two_numbers(x: float, y: float) -> float:
    """
    Adds two numbers and returns the result.

    Args:
        x: first int
        y: second int
    """
    return x + y


# Define available AI models
MODELS = [
    "openai.gpt-4o",
]


if __name__ == "__main__":
    for model_id in MODELS:
        print(f"\n-------------------\nModel: {model_id}")
        agent = create_react_agent(get_llm(model_id), tools=[add_two_numbers])
        graph = agent.get_graph()

        #Note: graph.draw_mermaid_png(output_file_path=f"{__file__}.png")  this need access to internet
        with open(f"{__file__}.txt", "w") as fd:
            fd.write(graph.draw_ascii())

        print(f"Question: {USER_PROMPT}")

        # Run the agent
        response = agent.invoke(
            {"messages": [{"role": "user", "content": USER_PROMPT}]}
        )

        for msg in response["messages"]:
            print(f"[{type(msg).__name__}] {msg.content}")

'''
-------------------
Model: openai.gpt-4o
Question: What is 3.5 plus 7.2 and 1.1?
[HumanMessage] What is 3.5 plus 7.2 and 1.1?
[AIMessage] 
[ToolMessage] 10.7
[ToolMessage] 8.3
[AIMessage] 
[ToolMessage] 11.799999999999999
[AIMessage] The result of 3.5 plus 7.2 plus 1.1 is approximately 11.8.
'''
