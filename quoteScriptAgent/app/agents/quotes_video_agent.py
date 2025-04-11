from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.agents import create_openai_functions_agent, AgentExecutor

from app.config import llm_config
from app.services.llm import LLMService
from app.tools.video_creation_tool import create_video_tool

llm = LLMService(llm_config.provider,
                  llm_config.model_name,
                  llm_config.api_key,)

tools = [create_video_tool]

memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True
)


system_message = SystemMessage(
    content="""You are an expert content creator specializing in inspirational quotes and videos.
    Your task is to generate engaging and meaningful content for motivational quote videos.
    For each request, generate a compelling title, description, thumbnail text, visual description for the thumbnail, 
    and a list of 5-7 powerful quotes related to the requested topic.
    The quotes should be original, insightful, and impactful.
    The visual description should help in creating a thumbnail image that captures the essence of the quotes."""
)

messages = [
    system_message,
    # TODO: What is the use of this class
    MessagesPlaceholder(variable_name="chat_history"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
]

prompt = ChatPromptTemplate.from_messages(messages)

agent = create_openai_functions_agent(
    llm.model,
    tools=tools,
    prompt=prompt
)

# TODO: what is the use of AgentExecuter
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
)