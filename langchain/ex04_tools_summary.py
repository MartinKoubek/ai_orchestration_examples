"""
At a high level, the script compares ways to define LangChain tools and
how each produces a parameters schema. It shows that docstring parsing,
type annotations, and Pydantic models all affect clarity of that schema.
Net takeaway: use Annotated[...] or parse_docstring=True, for simple tools,
and a Pydantic args_schema for richer, validated inputs; avoid unparsed “Args:” text.
"""
import json
from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool

@tool
def tool_plain(name: str) -> str:
    """
    Extract user information.
    """
    return name


@tool
def tool_args(name: str) -> str:
    """
    Extract user information.

    Args:
        name: Person's full name
    """
    return name


@tool(parse_docstring=True)
def tool_docstring(name: str) -> str:
    """
    Extract user information.

    Args:
        name: Person's full name
    """
    return name

@tool
def tool_annotated(name: Annotated[str, "Person's full name"]) -> str:
    """
    Extract user information.
    """
    return name

@tool
def tool_args_docstring_annotated(name: Annotated[str, "Person's full name"]) -> str:
    """
    Extract user information.

    Args:
        name: Person's full name
    """
    return name




@tool(parse_docstring=True)
def tool_args_decorating_docstring_annotated(name: Annotated[str, "Person's full name"]) -> str:
    """
    Extract user information.

    Args:
        name: Person's full name
    """
    return name



class ClassTool(BaseModel):
    """Extract user information.
    """
    name: str = Field(..., description="Person's full name")


@tool(args_schema=ClassTool, parse_docstring=False)
def tool_pydantic(name: str) -> str:
    return name


for tool in [tool_plain, tool_args, tool_docstring, tool_annotated, tool_args_docstring_annotated,
             tool_args_decorating_docstring_annotated, tool_pydantic]:
    full_schema = tool.args_schema.model_json_schema()
    print(f"{tool.name}:\n{json.dumps(full_schema, indent=2)}\n\n\n")


"""
tool_plain:
{
  "description": "Extract user information.",
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "tool_plain",
  "type": "object"
}



tool_args:
{
  "description": "Extract user information.\n\nArgs:\n    name: Person's full name",
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "tool_args",
  "type": "object"
}



tool_docstring:
{
  "description": "Extract user information.",
  "properties": {
    "name": {
      "description": "Person's full name",
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "tool_docstring",
  "type": "object"
}



tool_annotated:
{
  "description": "Extract user information.",
  "properties": {
    "name": {
      "description": "Person's full name",
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "tool_annotated",
  "type": "object"
}



tool_args_docstring_annotated:
{
  "description": "Extract user information.\n\nArgs:\n    name: Person's full name",
  "properties": {
    "name": {
      "description": "Person's full name",
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "tool_args_docstring_annotated",
  "type": "object"
}



tool_args_decorating_docstring_annotated:
{
  "description": "Extract user information.",
  "properties": {
    "name": {
      "description": "Person's full name",
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "tool_args_decorating_docstring_annotated",
  "type": "object"
}



tool_pydantic:
{
  "description": "Extract user information.\n    ",
  "properties": {
    "name": {
      "description": "Person's full name",
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "title": "ClassTool",
  "type": "object"
}




Process finished with exit code 0

"""