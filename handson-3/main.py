import os
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Handson3", json_response=True)

@mcp.prompt()
def review_diff() -> str:
    """Review a code diff"""
    with open(os.path.join(os.path.dirname(__file__), 'review.md'), 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
