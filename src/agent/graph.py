"""LangGraph agent with markdown artifact support.

An agent that can interact via chat and edit a markdown document artifact.
The artifact is stored in the graph state and can be modified through tools.
Uses Generative UI to render the artifact in a side panel.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any, Sequence

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.ui import AnyUIMessage, push_ui_message, ui_message_reducer
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict


# =============================================================================
# State
# =============================================================================

class State(TypedDict):
    """Agent state with messages, artifact, and UI components."""
    messages: Annotated[Sequence[AnyMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    artifact: str


DEFAULT_ARTIFACT = """\
# Documento

Benvenuto! Questo e' il tuo documento markdown.

## Sezioni

Puoi chiedere all'agente di:
- Aggiungere nuove sezioni
- Modificare il contenuto
- Formattare il testo
- Creare liste e tabelle

Inizia a chattare per modificare questo documento!
"""


# =============================================================================
# Tools
# =============================================================================

@tool
def update_document(new_content: str) -> str:
    """Replace the entire markdown document with new content.

    Use this when you need to completely rewrite the document or make major changes.

    Args:
        new_content: The complete new markdown content for the document.
    """
    return "Document updated successfully."


@tool
def append_to_document(content_to_add: str) -> str:
    """Append content to the end of the markdown document.

    Use this when adding new sections or content at the end.

    Args:
        content_to_add: The markdown content to append at the end.
    """
    return "Content appended successfully."


@tool
def replace_text(old_text: str, new_text: str) -> str:
    """Replace specific text in the document.

    Use this for targeted edits where you want to replace one piece of text with another.

    Args:
        old_text: The exact text to find and replace.
        new_text: The new text to replace it with.
    """
    return "Text replaced successfully."


TOOLS = [update_document, append_to_document, replace_text]


# =============================================================================
# Model & Prompt
# =============================================================================

SYSTEM_PROMPT = """\
Sei un assistente che aiuta gli utenti a modificare un documento markdown.
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


def get_model():
    """Get the configured LLM with tools bound."""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7).bind_tools(TOOLS)


# =============================================================================
# Nodes
# =============================================================================

async def agent(state: State) -> dict[str, Any]:
    """Process user message and generate response."""
    artifact = state.get("artifact") or DEFAULT_ARTIFACT

    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(artifact=artifact)),
        *state["messages"],
    ]

    response = await get_model().ainvoke(messages)

    # Create message with explicit ID for UI association
    ai_message = AIMessage(
        id=str(uuid.uuid4()),
        content=response.content,
        tool_calls=response.tool_calls or [],
    )

    # Emit UI only on final response (no tool calls)
    if not ai_message.tool_calls:
        push_ui_message(
            "markdown_artifact",
            {"content": artifact, "title": "Documento Markdown"},
            message=ai_message,
        )

    return {"messages": [ai_message]}


async def apply_edits(state: State) -> dict[str, Any]:
    """Apply tool call edits to the artifact."""
    artifact = state.get("artifact") or DEFAULT_ARTIFACT

    # Find the most recent AI message with tool calls
    for msg in reversed(state["messages"]):
        if not isinstance(msg, AIMessage) or not msg.tool_calls:
            continue

        for call in msg.tool_calls:
            name = call.get("name", "")
            args = call.get("args", {})

            if name == "update_document" and args.get("new_content"):
                artifact = args["new_content"]
            elif name == "append_to_document" and args.get("content_to_add"):
                artifact = f"{artifact.rstrip()}\n\n{args['content_to_add']}"
            elif name == "replace_text":
                old, new = args.get("old_text", ""), args.get("new_text", "")
                if old and old in artifact:
                    artifact = artifact.replace(old, new)
        break  # Only process the most recent message

    return {"artifact": artifact}


def should_continue(state: State) -> str:
    """Route to tools or end based on last message."""
    last = state["messages"][-1] if state["messages"] else None
    if last and hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


# =============================================================================
# Graph
# =============================================================================

def build_graph():
    """Build and compile the agent graph."""
    graph = StateGraph(State)

    # Nodes
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("apply_edits", apply_edits)

    # Edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, ["tools", END])
    graph.add_edge("tools", "apply_edits")
    graph.add_edge("apply_edits", "agent")

    return graph.compile(name="Markdown Editor Agent")


graph = build_graph()
