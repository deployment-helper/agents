from typing import Annotated
import json

from typing_extensions import TypedDict

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

from pydantic import BaseModel

from app.services.llm import LLMService
from app.config import llm_config
from app.tools.video_creation_tool import create_video_tool

llm = LLMService(
    llm_config.provider,
    llm_config.model_name,
    llm_config.api_key,
)

llm_model = llm.model


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]


tools = [create_video_tool, human_assistance]

llm_with_tools = llm_model.bind_tools(tools)

memory = MemorySaver()


class TitleAndThumbnailTextLists(BaseModel):
    titles: list[str]
    thumbnail_text_list: list[str]


class BestTitleAndThumbnailText(BaseModel):
    best_thumbnail_text: str
    best_title: str


class Quotes(BaseModel):
    quotes: list[str]


class ThumbnailVisualDesc(BaseModel):
    thumbnail_visual_desc: str


class Description(BaseModel):
    description: str


class State(TypedDict):
    # Messages have the type "list". The `add_messages` is reducer function function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    topic: str
    titles: list
    thumbnail_text_list: list
    best_thumbnail_text: str
    best_title: str
    quotes: list[str]
    description: str
    thumbnail_visual_desc: str
    video_id: str
    video_url: str


graph_builder = StateGraph(State)


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            print(tool_call)
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=tools)


def create_titles_and_thumbnail_texts(state: State):
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                "you are expert youtube content creator specialized in creating quotes types of video data like, Generating good list of title and thumbnail text for given topics.",
            ),
            (
                "user",
                "create list of titles and a list of thumbnail texts for this  {topic}. each list should contains 10 items.",
            ),
        ]
    )
    structure_llm = llm_model.with_structured_output(TitleAndThumbnailTextLists)
    msg = prompt_template.invoke(state).to_messages()
    response = structure_llm.invoke(msg)

    return {
        "titles": response.titles,
        "thumbnail_text_list": response.thumbnail_text_list,
    }


def find_best_title_and_thumbnail_text(state: State):
    """
    Find the best title and thumbnail text based on the given criteria.
    """
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                "you are expert youtube content creator specialized in creating quotes types of video data like, selecting best title and thumbnail text for given list of titles and thumbnail texts for this {topic}.",
            ),
            (
                "user",
                "select best title and thumbnail text from given list of titles and thumbnail texts. \n\n **Title List:** {titles} \n\n **Thumbnail Text List:** {thumbnail_text_list}",
            ),
        ]
    )

    structured_llm = llm_model.with_structured_output(BestTitleAndThumbnailText)
    msg = prompt_template.invoke(state).to_messages()
    response = structured_llm.invoke(msg)
    return {
        "best_title": response.best_title,
        "best_thumbnail_text": response.best_thumbnail_text,
    }


def create_quotes(state: State):
    """
    Create a list of quotes based on the given topic.
    """
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                "you are expert youtube content creator specialized in creating quotes types of video data like, generating good list of quotes for given title and thumbnail text for this {topic}.",
            ),
            (
                "user",
                "create a list of 40-50 quotes for this **Title:** {best_title} and **Thumbnail_text:** {best_thumbnail_text}.",
            ),
        ]
    )
    structured_llm = llm_model.with_structured_output(Quotes)
    msg = prompt_template.invoke(state).to_messages()
    response = structured_llm.invoke(msg)
    return {"quotes": response.quotes}


def create_thumbnail_visual_desc(state: State):
    """
    Create a visual description for the thumbnail based on the given topic.
    """
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                "you are expert youtube content creator specialized in creating thumbnail image description to create a thumbnail image for given title and thumbnail text for this {topic}.",
            ),
            (
                "user",
                "create a image description for the thumbnail image for this **Title:** {best_title} and **Thumbnail_text:** {best_thumbnail_text}. Write thumbnail_text on top of the image.",
            ),
        ]
    )
    structured_llm = llm_model.with_structured_output(ThumbnailVisualDesc)
    msg = prompt_template.invoke(state).to_messages()
    response = structured_llm.invoke(msg)
    return {"thumbnail_visual_desc": response.thumbnail_visual_desc}


def create_description(state: State):
    """
    Create a description for the video based on the given topic.
    """
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                "you are expert youtube content creator specialized in creating description for given title and thumbnail text for this *{topic}* topic.",
            ),
            (
                "user",
                "create a description for the youtube video for this **Title: {best_title} ** and **Thumbnail_text: {best_thumbnail_text}**.",
            ),
        ]
    )
    structured_llm = llm_model.with_structured_output(Description)
    msg = prompt_template.invoke(state).to_messages()
    response = structured_llm.invoke(msg)
    return {"description": response.description}


def create_video(state: State):

    resp = create_video_tool.invoke(
        input={
            "title": state["best_title"],
            "desc": state["description"],
            "thumbnail_text": state["best_thumbnail_text"],
            "thumbnail_visual_desc": state["thumbnail_visual_desc"],
            "quotes": state["quotes"],
        }
    )

    return {
        "video_id": resp["video_id"],
        "video_url": resp["video_url"],
    }


def chatbot(state: State):
    print("State:", state)
    print("Messages:", state["messages"])
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node(
    "create_titles_thumbnails_list", create_titles_and_thumbnail_texts
)
graph_builder.add_node(
    "find_best_title_thumbnail_text", find_best_title_and_thumbnail_text
)

graph_builder.add_node("create_quotes", create_quotes)
graph_builder.add_node("create_thumbnail_visual_desc", create_thumbnail_visual_desc)
graph_builder.add_node("create_description", create_description)
graph_builder.add_node("create_video", create_video)


graph_builder.add_edge(START, "create_titles_thumbnails_list")
graph_builder.add_edge(
    "create_titles_thumbnails_list", "find_best_title_thumbnail_text"
)
graph_builder.add_edge("find_best_title_thumbnail_text", "create_quotes")
graph_builder.add_edge("find_best_title_thumbnail_text", "create_thumbnail_visual_desc")
graph_builder.add_edge("find_best_title_thumbnail_text", "create_description")
graph_builder.add_edge("create_quotes", "create_video")
graph_builder.add_edge("create_thumbnail_visual_desc", "create_video")
graph_builder.add_edge("create_description", "create_video")
graph_builder.add_edge("create_video", END)


graph = graph_builder.compile(checkpointer=memory)
print(graph.get_graph().draw_ascii())
