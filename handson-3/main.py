import os
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Handson3", json_response=True)

@mcp.prompt()
def review_diff() -> str:
    """Review a code diff"""
    with open(os.path.join(os.path.dirname(__file__), 'review.md'), 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
def count_files(path: str) -> int:
    """Count the number of files in a directory"""
    return len(os.listdir(path))

@mcp.tool()
def get_yahoo_news() -> dict:
    """Get the latest news headlines from Yahoo! JAPAN"""
    try:
        # Yahoo! JAPANのトップページにアクセス
        response = requests.get("https://www.yahoo.co.jp/", timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # HTMLをパース
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 「主要 ニュース」セクションを探す
        # Yahoo! JAPANのHTML構造に応じてセレクタを調整
        news_items = []
        
        # ニュース項目を取得（実際のHTML構造に合わせて調整が必要）
        news_elements = soup.select('#tabpanelTopics1 article>a')
        
        for element in news_elements:
            text = element.get_text(strip=True)
            if text and len(text) > 5:  # 空でない、かつある程度の長さがあるもののみ
                # リンクがあれば取得
                link = element.get('href', '')
                if link and not link.startswith('http'):
                    link = f"https://www.yahoo.co.jp{link}"
                
                news_items.append({
                    "title": text,
                    "url": link if link else None
                })
        
        if news_items:
            return {
                "status": "success",
                "count": len(news_items),
                "news": news_items
            }
        else:
            return {
                "status": "error",
                "message": "ニュースが見つかりませんでした。HTML構造が変更されている可能性があります。"
            }
            
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"リクエストエラー: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"エラーが発生しました: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
