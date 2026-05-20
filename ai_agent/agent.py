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
from contextlib import AsyncExitStack

SERVER_PATH = os.path.join(PROJECT_ROOT, 'mcp_server', 'server.py')

GMAIL_MCP_DIR = "/home/biswajitshaw/Documents/gmail-mcp" 
GMAIL_SERVER_SCRIPT = f"{GMAIL_MCP_DIR}/src/gmail/server.py"
GMAIL_VENV_PYTHON = f"{GMAIL_MCP_DIR}/.venv/bin/python"
CREDS_JSON = f"{GMAIL_MCP_DIR}/credentials.json"
TOKEN_JSON = f"{GMAIL_MCP_DIR}/token.json"

async def run_ai_command(user_prompt: str) -> str:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    todo_server_params = StdioServerParameters(command="python", args=[SERVER_PATH])
    gmail_server_params = StdioServerParameters(
        command=GMAIL_VENV_PYTHON,
        args=[GMAIL_SERVER_SCRIPT, "--creds-file-path", CREDS_JSON, "--token-path", TOKEN_JSON]
    )

    async with AsyncExitStack() as stack:
        # Establish connections to both streams concurrently over stdio channels
        todo_transport = await stack.enter_async_context(stdio_client(todo_server_params))
        gmail_transport = await stack.enter_async_context(stdio_client(gmail_server_params))

        todo_session = await stack.enter_async_context(ClientSession(todo_transport[0], todo_transport[1]))
        gmail_session = await stack.enter_async_context(ClientSession(gmail_transport[0], gmail_transport[1]))

        await todo_session.initialize()
        await gmail_session.initialize()

        todo_tools = await todo_session.list_tools()
        gmail_tools = await gmail_session.list_tools()

        tools_description = "--- SQLITE TODO LIST TOOLS ---\n"
        for tool in todo_tools.tools:
            tools_description += f"- Name: {tool.name}\n  Desc: {tool.description}\n"
            
        tools_description += "\n--- GOOGLE GMAIL API TOOLS ---\n"
        for tool in gmail_tools.tools:
            tools_description += f"- Name: {tool.name}\n  Desc: {tool.description}\n"

        system_instruction = (
            "You are an intelligent AI Workflow Coordinator managing a user's Gmail and local To-Do database via MCP.\n"
            "You must handle three primary email features natively based on user instructions:\n\n"
            
            "1. EMAIL SUMMARY FEATURE:\n"
            "   - When asked to summarize, list, or check recent emails, select a Gmail retrieval tool (e.g., 'search-emails' or 'list-messages').\n"
            "   - Return the tool name and arguments cleanly. Once the tool returns the data, it will be displayed.\n\n"
            
            "2. Q&A BASED ON EMAILS FEATURE:\n"
            "   - When the user asks a specific question about email details (e.g., 'What time is my exam according to the email?'), "
            "     first call the appropriate Gmail tool to gather information. Do not guess information or assume data.\n\n"
            
            "3. CREATING TASK FROM EMAILS FEATURE:\n"
            "   - When the user requests to create a task, note down, or generate a to-do entry based on an email thread or ID, "
            "     you MUST select 'create_todo_task'.\n"
            "   - CRITICAL: Do NOT pass raw email IDs into the title argument field. Instead, construct a professional, meaningful "
            "     'title' (e.g., 'Infosys Exam Preparation') and provide a clear context summary for the 'description' argument field.\n\n"
            
            "GENERAL CONSTRAINTS:\n"
            "- If the message is simple conversational text ('hi', 'thank you'), return tool_name as 'none'.\n"
            "- You MUST respond with a single, valid raw JSON object string using double quotes only. No markdown formatting wrapper blocks.\n\n"
            "JSON Formatting Templates:\n"
            '{"tool_name": "none", "arguments": {"reply": "Hello! Ready to manage your emails and tasks."}}\n'
            '{"tool_name": "create_todo_task", "arguments": {"title": "Task Title Here", "description": "Context Description Here"}}\n\n'
            f"Available Multi-System Tool Catalog:\n{tools_description}"
        )

        messages = [("system", system_instruction), ("user", user_prompt)]
        ai_response = await llm.ainvoke(messages)
        clean_content = ai_response.content.strip().strip("```json").strip("```").strip()

        try:
            tool_call = json.loads(clean_content)
            t_name = tool_call.get("tool_name", "").strip().lower()
            t_args = tool_call.get("arguments", {})

            if t_name == "none" or not t_name:
                return t_args.get("reply", "Hello! How can I assist you with your system workflow today?")

            print(f"AI System routed event to tool: '{t_name}'")

            todo_match = next((t for t in todo_tools.tools if t.name.lower() == t_name), None)
            gmail_match = next((t for t in gmail_tools.tools if t.name.lower() == t_name), None)

            if todo_match:
                result = await todo_session.call_tool(todo_match.name, arguments=t_args)
            elif gmail_match:
                result = await gmail_session.call_tool(gmail_match.name, arguments=t_args)
            else:
                return f"AI selected unknown tool '{t_name}'."

            if result.content and len(result.content) > 0:
                return result.content[0].text
            return "Multi-System pipeline executed successfully."

        except json.JSONDecodeError:
            return f"Failed to align JSON sequence. Model said: {ai_response.content}"
        except Exception as e:
            return f"Execution pipeline failure: {str(e)}"

async def run_test():
    print("Initializing upgraded multi-feature MCP ecosystem...")
    user_prompt = "hi"
    response = await run_ai_command(user_prompt)
    print(f"\nAgent Response:\n{response}")

if __name__ == "__main__":
    asyncio.run(run_test())