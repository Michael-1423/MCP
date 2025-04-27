import asyncio 
from typing import Optional 
from contextlib import AsyncExitStack 
import asyncio 
from mcp import ClientSession, StdioServerParameters 
from mcp.client.stdio  import stdio_client 
# from anthropic import Anthropic 
from dotenv import load_dotenv 
import ollama

from google import genai
from google.genai import types
from google.generativeai.types import FunctionDeclaration, Tool

import os

load_dotenv() 
# load environment variables from .env 



class MCPClient: 
    def __init__(self): 
        # Initialize session and client objects 
        self.session: Optional[ClientSession] = None 
        self.exit_stack = AsyncExitStack() 
        # # self.anthropic = Anthropic() 
        # # methods will go here 
        # print(os.getenv("API_KEY"))
        self.client = genai.Client(api_key=os.getenv("API_KEY"))

    async def connect_to_server(self, server_script_path: str): 
        """Connect to an MCP server 
        Args: server_script_path: Path to the server script (.py or .js) """ 
        
        is_python = server_script_path.endswith('.py') 
        is_js = server_script_path.endswith('.js') 
        if not (is_python or is_js): 
            raise ValueError("Server script must be a .py or .js file") 
        
        command = "python" if is_python else "node" 
        server_params = StdioServerParameters( 
            command=command, 
            args=[server_script_path], 
            env=None 
            ) 
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params)) 
        self.stdio, self.write = stdio_transport 
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write)) 
        
        await self.session.initialize() 
        
        # List available tools 
        response = await self.session.list_tools() 
        tools = response.tools 
        print("\nConnected to server with tools:", [tool.name for tool in tools]) 
    
    
    
    def clean_input_schema(self, input_schema: dict) -> dict:
    # Remove top-level title and keep only the allowed top-level fields
        allowed_top_keys = {"type", "properties", "required"}
        schema = {k: v for k, v in input_schema.items() if k in allowed_top_keys}

        # If properties exist, remove "title" from each property too
        if "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                schema["properties"][prop] = {
                    k: v for k, v in prop_schema.items() if k != "title"
                }

        return schema
    
    async def process_query(self, query: str) -> str: 
        """Process a query using Claude and available tools""" 
        # messages = [ 
        #     { 
        #         "role": "user", 
        #         "content": query 
        #     } 
        #         ] 


        contents = [
            types.Content(
                role="user", parts=[types.Part(text=query)]
            )
        ]

        model_name = "llama3.1:latest"
        response = await self.session.list_tools() 
        # print(dict(response.tools[0]))
        print(response.tools[0])

        function_declarations = []
        function_declarations = [
            FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=self.clean_input_schema(tool.inputSchema)
            ).to_proto()
            for tool in response.tools
        ]


        tools = [Tool(function_declarations=function_declarations)]

        config = types.GenerateContentConfig(tools=tools)
        

        response = self.client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=config,
        )

       


        # Initial Claude API call 
        # 
        # response = self.anthropic.messages.create( model="claude-3-5-sonnet-20241022", max_tokens=1000, messages=messages, tools=available_tools ) 
        

        # response = ollama.chat(
        #     model_name,
        #     messages=messages,
        #     tools=available_tools, # Actual function reference
        #     )
        print(response)

        # Process response and handle tool calls 
        # 
        final_text = [] 
        
        assistant_message_content = [] 


        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print(f"Function to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")

            tool_name = function_call.name
            tool_args = function_call.args

            result = await self.session.call_tool(tool_name, tool_args) 
                
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]") 
            
            assistant_message_content.append(response.message.content) 
            
            contents.append(types.Content(
                role="user", parts=[types.Part(text=assistant_message_content)]
            )) 
            
            contents.append(types.Content(
                role="user", parts=[types.Part(text=result.content)]
            )) 
            #  In a real app, you would call your function here:
            #  result = schedule_meeting(**function_call.args)
        else:
            # print("No function call found in the response.")
            # print(response.text)

            final_text.append(response.text)
            assistant_message_content.append(response.text)

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
            )
        final_text.append(response.text)

        # for tool in response.message.tool_calls or []:
        #     function_to_call = available_functions.get(tool.function.name)
        #     if function_to_call == requests.request:
        #         # Make an HTTP request to the URL specified in the tool call
        #         resp = function_to_call(
        #         method=tool.function.arguments.get('method'),
        #         url=tool.function.arguments.get('url'),
        #         )
        #         print(resp.text)
        #     else:
        #         print('Function not found:', tool.function.name)
        


        # if response.message.content=='':
        #     for tool in response.message.tool_calls:
                
        #         print(tool)
        #         tool_name = tool.function.name
        #         tool_args = tool.function.arguments

        #         result = await self.session.call_tool(tool_name, tool_args) 
                    
        #         final_text.append(f"[Calling tool {tool_name} with args {tool_args}]") 
                
        #         assistant_message_content.append(response.message.content) 
                
        #         messages.append({ "role": "assistant", "content": assistant_message_content}) 
                
        #         messages.append({ "role": "user", "content": [ { "type": "tool_result", "content": result.content } ] }) 
            
        #         # Get next response from Claude 
        #         # 
        #         # response = self.anthropic.messages.create( model="claude-3-5-sonnet-20241022", max_tokens=1000, messages=messages, tools=available_tools ) 
        
        # else:
        #     final_text.append(response.message.content)
        #     assistant_message_content.append(response.message)


        # response = ollama.chat(
        #         model_name,
        #         messages=messages,
        #         tools=available_tools, # Actual function reference
        #         )

        # final_text.append(response.message.content) 

        # for content in response.content: 
        #     if content.type == 'text': 
        #         final_text.append(content.text) 
                
        #         assistant_message_content.append(content) 
            
        #     elif content.type == 'tool_use': 
        #         tool_name = content.name 
        #         tool_args = content.input 
                
        #         # Execute tool call 
        #         # 
        #         result = await self.session.call_tool(tool_name, tool_args) 
                
        #         final_text.append(f"[Calling tool {tool_name} with args {tool_args}]") 
                
        #         assistant_message_content.append(content) 
                
        #         messages.append({ "role": "assistant", "content": assistant_message_content}) 
                
        #         messages.append({ "role": "user", "content": [ { "type": "tool_result", "tool_use_id": content.id, "content": result.content } ] }) 
                
        #         # Get next response from Claude 
        #         # 
        #         response = self.anthropic.messages.create( model="claude-3-5-sonnet-20241022", max_tokens=1000, messages=messages, tools=available_tools ) 
                
        #         final_text.append(response.content[0].text) 
        
        
        
        return "\n".join(final_text) 
    
    async def chat_loop(self): 
        
        """Run an interactive chat loop""" 
        
        print("\nMCP Client Started!") 
        print("Type your queries or 'quit' to exit.") 
        while True: 
            try: 
                query = input("\nQuery: ").strip() 
                
                if query.lower() == 'quit': 
                    break 
                
                response = await self.process_query(query) 
                
                print("\n" + response) 
            
            except Exception as e: 
                print(f"\nError: {str(e)}") 
    
    async def cleanup(self): 
        
        """Clean up resources""" 
        await self.exit_stack.aclose() 
        
async def main(): 
        
    client = MCPClient() 
    # try: 
    await client.connect_to_server(server_script_path="github_server.py") 
    # await client.process_query("what is the sum of 5 and 6?")
        # await client.chat_loop() 
    
    # except Exception as e: 
        
    #     print("EROR" ,e ) 
        
    # finally: 
        
    await client.cleanup() 
    print("shutdown") 
        
if __name__ == "__main__": 
    import sys 
    # print("start")
    asyncio.run(main()) 
    # print("now")