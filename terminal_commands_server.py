import mcp
from mcp.client.websocket import websocket_client
import json
import base64
import asyncio
import os
import dotenv
from autogen_core.tools import BaseTool
# from autogen_ext.tools.mcp import McpTool
from typing import cast
from openai.types.chat import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition, FunctionParameters
from autogen_core.utils import schema_to_pydantic_model


from autogen_agentchat.agents import AssistantAgent

from autogen_agentchat.messages import TextMessage

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams,mcp_server_tools,SseServerParams,SseMcpToolAdapter
from autogen_agentchat.ui import Console


dotenv.load_dotenv()




github_api_key = os.environ['github_token']
smithery_api_key = os.environ['smithey-key']
gemini_api_key = os.environ['API_KEY']


# config = {
#   "githubPersonalAccessToken": github_api_key
# }
config={
  "type": "object",
  "properties": {}
}
# Encode config in base64
config_b64 = base64.b64encode(json.dumps(config).encode())
smithery_api_key = smithery_api_key


# server_params = StdioServerParams(
#     param1="value1",  # Replace with actual parameters
#     param2="value2"
# )


# server_params = StdioServerParams(
#         command="your_server_command_here",  # Replace with the actual command
#         # Add any other necessary parameters here
#     )


# Create server URL
url = f"wss://server.smithery.ai/@wonderwhy-er/desktop-commander/ws?config={config_b64}&api_key={smithery_api_key}"
# headers: {
#     'Authorization'= smithery_api_key
# }

server_params = SseServerParams(
    url=url,
)



class MCP2AUTO(BaseTool):

    def __init__(
        self,
        args_type,
        return_type,
        name: str,
        description: str,
        strict: bool = False,
    ):
        super().__init__(
            args_type=args_type,
            return_type=return_type,
            name=name,
            description=description,
            strict=strict
        )
        self._url = f"wss://server.smithery.ai/@wonderwhy-er/desktop-commander/ws?config={config_b64}&api_key={smithery_api_key}"
    
    async def run(self, args, cancellation_token):
        ##how to call the mcp tool
        print(args)
        async with websocket_client(url) as streams:
            async with mcp.ClientSession(*streams) as session:

                await session.initialize()

                
                result = await session.call_tool(self.name, arguments=args)
        print(result)
        return result

async def main():
    # Connect to the server using websocket client
    async with websocket_client(url) as streams:
        async with mcp.ClientSession(*streams) as session:
            # Initialize the connection
            print("i am here")
            await session.initialize()
            print("i am here")
            # List available tools
            tools_result = await session.list_tools()
            tools = await mcp_server_tools(server_params=server_params, session=session)

            # adapter = await SseMcpToolAdapter.from_server_params(
            #     server_params,
            #     "list_directory",
            # )
            # tools = [adapter]
            print(tools_result.tools[0])
            # return
            # tools = [McpTool(session=session, tool=t) for t in tools_result.tools]

            # tools = [MCP2AUTO(
            #     args_type=schema_to_pydantic_model(t.inputSchema),
            #     name=t.name,
            #     return_type=object,
            #     description=t.description,
            #     strict=False
            # ) for t in tools_result.tools]

            # tools = [
            #     ChatCompletionToolParam(
            #         type='function',
            #         function=FunctionDefinition(
            #             name=t.name,
            #             description=t.description,  # Fixed the syntax here
            #             parameters=cast(FunctionParameters, t.inputSchema),  # Corrected parameters line
            #             strict=False,
            #         ),
            #     )
            #     for t in tools_result.tools
            # ]



            print(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")

            model_client = OpenAIChatCompletionClient(
            model="gemini-2.0-flash",
            api_key=gemini_api_key ,
            api_type='google'
            )
            print("model client loaded")
            fetch_agent = AssistantAgent(
                name="fetcher", model_client=model_client, tools=tools, reflect_on_tool_use=True
            )
            print("fetcher agent defined")
            # Let the agent fetch the content of a URL and summarize it.
            # result = await fetch_agent.run(task="give me a list of my repositories")
            result = await Console(fetch_agent.run_stream(task="give me a list of my repositories"))
            # result = await console.run()

            assert isinstance(result.messages[-1], TextMessage)
            print(result.messages[-1].content)

            # Close the connection to the model client.
            await model_client.close()
                # Example of calling a tool:
                # result = await session.call_tool("tool-name", arguments={"arg1": "value"})

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


