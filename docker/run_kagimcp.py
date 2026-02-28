import os

from kagimcp import server


VALID_TRANSPORTS = {"stdio", "sse", "streamable-http"}


def _as_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "streamable-http").strip().lower()
    if transport not in VALID_TRANSPORTS:
        raise ValueError(
            f"Invalid MCP_TRANSPORT='{transport}'. Supported: {sorted(VALID_TRANSPORTS)}"
        )

    mcp = server.mcp

    if transport != "stdio":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = _as_int(os.getenv("MCP_PORT", "8000"), 8000)

        mcp.settings.host = host
        mcp.settings.port = port

        path = os.getenv("MCP_PATH", "/mcp" if transport == "streamable-http" else "/sse")
        if transport == "streamable-http":
            mcp.settings.streamable_http_path = path
        elif transport == "sse":
            mcp.settings.mount_path = path

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
