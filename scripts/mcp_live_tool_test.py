import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent


async def main() -> int:
    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
    query = os.getenv("KAGI_LIVE_TEST_QUERY", "site:kagi.com Kagi search")

    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("kagi_search_fetch", {"queries": [query]})

            if result.isError:
                print("Live tool call returned an MCP error.")
                for block in result.content:
                    if isinstance(block, TextContent):
                        print(block.text)
                return 1

            text_blocks = [block.text for block in result.content if isinstance(block, TextContent)]
            combined = "\n".join(text_blocks).strip()
            if not combined:
                print("Live tool call succeeded but returned empty text content.")
                return 1

            print("Live tool call succeeded. First 500 chars:")
            print(combined[:500])
            return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
