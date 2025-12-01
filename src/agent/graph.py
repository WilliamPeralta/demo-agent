"""LangGraph agent with markdown artifact support.

An agent that can interact via chat and edit a markdown document artifact.
The artifact is stored in the graph state and can be modified through tools.
"""

from __future__ import annotations

from typing import Annotated, Any

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict


class State(TypedDict):
    """Agent state with messages and markdown artifact."""

    messages: Annotated[list[AnyMessage], add_messages]
    artifact: str


# Default initial markdown content
DEFAULT_MARKDOWN = """# Documento

Benvenuto! Questo e' il tuo documento markdown.

## Sezioni

Puoi chiedere all'agente di:
- Aggiungere nuove sezioni
- Modificare il contenuto
- Formattare il testo
- Creare liste e tabelle

Inizia a chattare per modificare questo documento!
"""


@tool
def update_document(new_content: str) -> str:
    """Replace the entire markdown document with new content.

    Use this when you need to completely rewrite the document or make major changes.

    Args:
        new_content: The complete new markdown content for the document.

    Returns:
        Confirmation message.
    """
    return f"Document updated successfully."


@tool
def append_to_document(content_to_add: str) -> str:
    """Append content to the end of the markdown document.

    Use this when adding new sections or content at the end.

    Args:
        content_to_add: The markdown content to append at the end.

    Returns:
        Confirmation message.
    """
    return f"Content appended successfully."


@tool
def replace_text(old_text: str, new_text: str) -> str:
    """Replace specific text in the document.

    Use this for targeted edits where you want to replace one piece of text with another.

    Args:
        old_text: The exact text to find and replace.
        new_text: The new text to replace it with.

    Returns:
        Confirmation message.
    """
    return f"Text replaced successfully."


tools = [update_document, append_to_document, replace_text]


def get_model():
    """Get the configured OpenAI model."""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


SYSTEM_PROMPT = """Sei un assistente che aiuta gli utenti a modificare un documento markdown.
Hai accesso a strumenti per modificare il documento.

DOCUMENTO ATTUALE:
```markdown
{artifact}
```

ISTRUZIONI:
1. Quando l'utente chiede di vedere il documento, mostra il contenuto attuale.
2. Quando l'utente chiede modifiche, usa gli strumenti appropriati:
   - update_document: per riscrivere completamente il documento
   - append_to_document: per aggiungere contenuto alla fine
   - replace_text: per sostituire parti specifiche del testo
3. Dopo ogni modifica, conferma cosa hai fatto.
4. Rispondi sempre in italiano.
"""


async def agent_node(state: State) -> dict[str, Any]:
    """Process the user message and potentially modify the document."""
    model = get_model()
    model_with_tools = model.bind_tools(tools)

    artifact = state.get("artifact") or DEFAULT_MARKDOWN
    system_message = SystemMessage(content=SYSTEM_PROMPT.format(artifact=artifact))

    messages = [system_message] + list(state["messages"])
    response = await model_with_tools.ainvoke(messages)

    return {"messages": [response]}


async def process_tool_result(state: State) -> dict[str, Any]:
    """Process tool results and update artifact based on tool calls."""
    messages = state["messages"]
    artifact = state.get("artifact") or DEFAULT_MARKDOWN

    # Look for recent tool calls and apply changes
    for msg in messages[-10:]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.get("name", "")
                args = tool_call.get("args", {})

                if name == "update_document":
                    new_content = args.get("new_content", "")
                    if new_content:
                        artifact = new_content
                elif name == "append_to_document":
                    content = args.get("content_to_add", "")
                    if content:
                        artifact = artifact.rstrip() + "\n\n" + content
                elif name == "replace_text":
                    old_text = args.get("old_text", "")
                    new_text = args.get("new_text", "")
                    if old_text and old_text in artifact:
                        artifact = artifact.replace(old_text, new_text)

    return {"artifact": artifact}


def should_continue(state: State) -> str:
    """Determine if we should continue to tools or end."""
    messages = state["messages"]
    if not messages:
        return END

    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# Build the graph
def build_graph():
    """Build and compile the agent graph."""
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("process_result", process_tool_result)

    # Add edges
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, ["tools", END])
    builder.add_edge("tools", "process_result")
    builder.add_edge("process_result", "agent")

    # Compile without checkpointer - LangGraph API handles persistence automatically
    return builder.compile(name="Markdown Editor Agent")


graph = build_graph()
