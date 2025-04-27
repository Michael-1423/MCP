from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams,mcp_server_tools,SseServerParams,SseMcpToolAdapter
import os
import dotenv
import asyncio
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console

dotenv.load_dotenv()

gemini_api_key = os.environ['API_KEY']


# Get the fetch tool from mcp-server-fetch.
fetch_mcp_server = StdioServerParams(command=".venv/bin/python3", args=["filesystem/filesystem_server.py"])


async def main():
    # Create an MCP workbench which provides a session to the mcp server.
    # async with McpWorkbench(fetch_mcp_server) as workbench:  # type: ignore
        # Create an agent that can use the fetch tool.
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key ,
        api_type='google'
        )
    # print("model client loaded")

    tools =  await mcp_server_tools(fetch_mcp_server)
    file_agent = AssistantAgent(
        name="file_agent", model_client=model_client, tools=tools, reflect_on_tool_use=True
    )

    team = MagenticOneGroupChat([file_agent], model_client=model_client)

    # print("fetcher agent defined")
    # Let the agent fetch the content of a URL and summarize it.
    # result = await fetch_agent.run(task="give me a list of my repositories")
    result =   await Console(team.run_stream(task="List the contents at path home/jatin/Documents"))
    # assert isinstance(result.messages[-1], TextMessage)
    # print(result.messages[-1].content)

    # Close the connection to the model client.
    await model_client.close()

if __name__=='__main__':
    asyncio.run(main())