import os
import sys
import json
import asyncio

# Dynamically add the parent directory to the system path to allow imports from there
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = os.path.join(PROJECT_ROOT, 'mcp_server', 'server.py')

async def run_ai_command(user_prompt: str) -> str:
    """
    Spins up the native MCP Stdio client, discovers the database tools,
    and prompts Groq to execute transactions cleanly.
    """
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_PATH]
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            mcp_tools = await session.list_tools()
            
            tools_description = ""
            for tool in mcp_tools.tools:
                tools_description += f"- Tool Name: {tool.name}\n  Description: {tool.description}\n  Schema: {tool.inputSchema}\n\n"
               
            system_instruction = (
                "You are an AI Assistant that manages a To-Do list database via tool calling.\n"
                "Based on the user prompt, choose ONE appropriate tool from the list below.\n"
                "You MUST respond with a raw JSON object containing 'tool_name' and 'arguments'.\n"
                "Do not include any conversational text outside the JSON block.\n\n"
                f"Available Tools:\n{tools_description}"
            )

            messages = [
                ("system", system_instruction),
                ("user", user_prompt)
            ]
            ai_response = await llm.ainvoke(messages)
            
            clean_content = ai_response.content.strip().strip("```json").strip("```").strip()

            try:
                tool_call = json.loads(clean_content)
                t_name = tool_call.get("tool_name")
                t_args = tool_call.get("arguments", {})

                print(f"AI selected tool '{t_name}' with args: {t_args}")
                result = await session.call_tool(t_name, arguments=t_args)
                
                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "Tool executed with no return content."

            except json.JSONDecodeError:
                return f"Sorry, I couldn't format the execution sequence. Model replied: {ai_response.content}"
            except Exception as e:
                return f"Error executing database tool: {str(e)}" 

async def run_test():
    print("Initializing direct native MCP Session context wrapper...")
    user_prompt = "Hey! Add a task named 'Prepare MCA Project Abstract' with description 'Draft a 1 page word doc summary'."
    print(f"\nPrompting Agent: \"{user_prompt}\"")
    
    response_text = await run_ai_command(user_prompt)
    print(f"\nAI Agent Final Execution Response:\n{response_text}")
        
if __name__ == "__main__":
    asyncio.run(run_test())