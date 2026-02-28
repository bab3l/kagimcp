import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


EXPECTED_TOOLS = {"kagi_search_fetch", "kagi_summarizer"}


async def main() -> int:
    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")

    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()
            tool_names = {tool.name for tool in response.tools}
            print(f"Discovered tools: {sorted(tool_names)}")

            missing = EXPECTED_TOOLS - tool_names
            if missing:
                print(f"Missing expected tools: {sorted(missing)}")
                return 1

    print("MCP streamable-http handshake + tool discovery succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
