import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent


def _extract_text(result) -> str:
    text_blocks = [block.text for block in result.content if isinstance(block, TextContent)]
    return "\n".join(text_blocks).strip()


def _print_preview(prefix: str, text: str) -> None:
    print(prefix)
    print(text[:500])


async def main() -> int:
    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
    query = os.getenv("KAGI_LIVE_TEST_QUERY", "site:kagi.com Kagi search")
    summary_url = os.getenv("KAGI_LIVE_TEST_SUMMARY_URL", "https://www.kagi.com")
    mode = os.getenv("KAGI_LIVE_TEST_MODE", "auto").strip().lower()

    if mode not in {"auto", "search", "summarizer"}:
        print("KAGI_LIVE_TEST_MODE must be one of: auto, search, summarizer")
        return 1

    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            if mode in {"auto", "search"}:
                search_result = await session.call_tool("kagi_search_fetch", {"queries": [query]})
                search_text = _extract_text(search_result)

                if not search_result.isError and search_text:
                    _print_preview("Live search tool call succeeded. First 500 chars:", search_text)
                    return 0

                if mode == "search":
                    print("Live search tool call failed.")
                    print(search_text or "No text returned")
                    return 1

                unauthorized = "401" in search_text or "Unauthorized" in search_text
                if not unauthorized:
                    print("Search failed for a non-auth reason in auto mode.")
                    print(search_text or "No text returned")
                    return 1

                print("Search API unauthorized; falling back to summarizer tool test.")

            summary_result = await session.call_tool(
                "kagi_summarizer",
                {
                    "url": summary_url,
                    "summary_type": "takeaway",
                },
            )
            summary_text = _extract_text(summary_result)
            if summary_result.isError or not summary_text:
                print("Live summarizer tool call failed.")
                print(summary_text or "No text returned")
                return 1

            _print_preview("Live summarizer tool call succeeded. First 500 chars:", summary_text)
            return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
