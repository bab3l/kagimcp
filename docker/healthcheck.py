import http.client
import os
import sys


def main() -> int:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    if host == "0.0.0.0":
        host = "127.0.0.1"

    port_raw = os.getenv("MCP_PORT", "8000")
    try:
        port = int(port_raw)
    except ValueError:
        return 1

    transport = os.getenv("MCP_TRANSPORT", "streamable-http").strip().lower()
    if transport == "streamable-http":
        path = os.getenv("MCP_PATH", "/mcp")
    elif transport == "sse":
        path = os.getenv("MCP_PATH", "/sse")
    else:
        return 1

    try:
        conn = http.client.HTTPConnection(host, port, timeout=4)
        conn.request("GET", path)
        response = conn.getresponse()
        status = response.status
        response.read()
        conn.close()
    except Exception:
        return 1

    return 0 if status < 500 else 1


if __name__ == "__main__":
    sys.exit(main())
