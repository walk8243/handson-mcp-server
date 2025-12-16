import os
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Handson2", json_response=True)

# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "温かく親しみやすい挨拶を書いてください",
        "formal": "正式でプロフェッショナルな挨拶を書いてください",
        "casual": "カジュアルでリラックスした挨拶を書いてください",
        "humorous": "ユーモアのある楽しい挨拶を書いてください",
        "enthusiastic": "熱心でエネルギッシュな挨拶を書いてください",
        "polite": "丁寧で礼儀正しい挨拶を書いてください",
        "warm": "心温まる親切な挨拶を書いてください",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

@mcp.prompt()
def review_diff() -> str:
    """Review a code diff"""
    with open(os.path.join(os.path.dirname(__file__), 'review.md'), 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
