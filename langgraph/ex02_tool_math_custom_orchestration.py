"""
This demo extends the previous math example (ex01_tool_math_reactagent)
by routing tool execution through a dedicated **LangGraph node** instead
of relying on a **prebuilt ReAct agent**. It defines a custom tool,
`add_two_numbers`, and integrates it as a `ToolNode` within a
**custom LangGraph workflow**.

## Key Difference

- In the **prebuilt ReAct agent** approach (`create_react_agent`),
  tool calling is **implicit**, delegated to the LLM itself.
- In this **custom LangGraph workflow**, the tool is invoked through a
  dedicated `ToolNode`. This makes tool usage **explicitly orchestrated**
  in the graph rather than fully controlled by the LLM.
- Both approaches produce similar results, but the workflow style offers
  more transparency and fine-grained control.

Results remain consistent with the expected output in the earlier
  **ReAct agent** demo.

"""


from typing import Literal, Annotated

from langgraph.constants import START, END
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode


from ex01_tool_math_reactagent import add_two_numbers, MODELS, USER_PROMPT
from llm_factory import get_llm


def should_call_tool(state: list) -> Literal["add_two_numbers", "__end__"]:
    last = state[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "add_two_numbers"
    return END

if __name__ == "__main__":
    for model_id in MODELS:
        print(f"\n-------------------\nModel: {model_id}")
        llm = get_llm(model_id).bind_tools([add_two_numbers])

        tool_nodes = ToolNode([add_two_numbers])
        state_graph = StateGraph(Annotated[list, add_messages])
        state_graph.add_node("ai_model", llm)
        state_graph.add_node("add_two_numbers", tool_nodes)

        state_graph.add_edge(START, "ai_model")
        state_graph.add_conditional_edges("ai_model", should_call_tool)
        state_graph.add_edge("add_two_numbers", "ai_model")

        compiled_graph = state_graph.compile()
        graph = compiled_graph.get_graph()

        #Note: graph.draw_mermaid_png(output_file_path=f"{__file__}.png")  this need access to internet
        with open(f"{__file__}.txt", "w") as fd:
            fd.write(graph.draw_ascii())


        # Run the agent
        response = compiled_graph.invoke(
            ("user", USER_PROMPT)
        )

        for msg in response:
            print(f"[{type(msg).__name__}] {msg.content}")


'''
-------------------
Model: openai.gpt-4o
[HumanMessage] What is 3.5 plus 7.2 and 1.1?
[AIMessage] 
[ToolMessage] 10.7
[ToolMessage] 8.3
[AIMessage] 
[ToolMessage] 11.799999999999999
[AIMessage] 3.5 plus 7.2 and 1.1 equals approximately 11.8.

'''
