# ハンズオン

## 準備

- コーディングツール
  - [Visual Studio Code](https://code.visualstudio.com/)
  - [IntelliJ](https://www.jetbrains.com/ja-jp/idea/)
  - [Claude Code](https://code.claude.com/docs/ja/overview)
  - その他
- [uv](https://docs.astral.sh/uv/)
  - macOSの場合はHomebrewからでもインストール可能: `brew install uv`

以下コマンドはUNIX環境を想定して記載します。

## handson-1

MCPサーバの作成から利用までの流れを体験し、基本的な仕組みを理解を目指します。

1. **MCPサーバのセットアップ** - FastMCPで最小構成のサーバを作成
2. **Toolの定義** - 簡単な関数（足し算）を`@mcp.tool()`で登録
3. **サーバの起動** - Streamable HTTPで起動
4. **コーディングツールからの利用** - 接続設定を行い、実際にtoolを呼び出して動作確認

### ディレクトリの作成

まずは作業用のディレクトリを作成します。
作成するディレクトリ名を `mcp-sample` とします。

```bash
uv init mcp-sample
```

MCPはPython **3.10** 以上を必要とすることに注意してください。

`mcp-sample` をお好きなコーディングツールで開いてください。

次のコマンドでMCPのPython SDKをインストールします。

```bash
uv add "mcp[cli]"
```

### MCPサーバの作成

`main.py` に次のように記述します。

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("handson", json_response=True)
```

これにより、MCPサーバの設定ができるようになります。
ここにMCPサーバの機能を追加していきます。

関数を作成し、その関数に `@mcp.tool()` とアノテーションを付与することでMCPサーバにtoolとして定義することができます。

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

最後に、`main.py` の実行時にMCPサーバを起動します。

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### MCPサーバの実行

MCPサーバの準備ができたので、実際に起動してみます。

```bash
uv run --with mcp main.py
```

MCPサーバの起動に成功すると、以下のようなログが表示されます。

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

ここでは **Streamable HTTP** を使ってMCPサーバを起動しました。
従来の **stdio** での起動をしたい場合は、`mcp.run(transport="stdio")` と指定してください。
ただし、Streamable HTTPを使うことが現在では推奨されているため、特別な理由がない限りはStreamable HTTPを使って起動してください。

### MCPサーバへの接続

コーディングツールごとに接続する設定方法は異なるため、適宜読み替えてください。

#### Visual Studio Codeの場合

MCPサーバの設定は `.vscode/mcp.json` に記述します。

```json
{
  "servers": {
    "mcp-sample": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

#### IntelliJの場合

[GitHub Copilotプラグイン](https://docs.github.com/ja/copilot/how-tos/set-up/install-copilot-extension?tool=jetbrains) を使った実行になります。

GitHub Copilot Chatを開き、実行モードを **Agent** に変更します。
するとツールアイコンが表示され、MCPツール設定のウィンドウが開きます。
ウィンドウ内左下の `Add MCP Tools...` をクリックすると、`mcp.json` が開きます。

```json
{
  "servers": {
    "mcp-sample": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

#### Claude Codeの場合

Claude Codeではファイルの編集は不要で、コマンドから設定可能です。

```bash
claude mcp add --transport http mcp-sample http://127.0.0.1:8000/mcp
```

### MCPサーバを利用した実行

必要に応じてコンテキストでMCPサーバのツールを指定し、チャットに以下を送信してみてください。

```text
1+1は？
```

MCPサーバの利用を許可することで、実行されていることが確認できるはずです。

## handson-2

MCPサーバでプロンプト機能を実装し、定型プロンプトを提供する方法を学びます。

1. **プロンプトの概念理解** - ToolとPromptの違いを理解
2. **プロンプトの定義** - `@mcp.prompt()`を使って定型プロンプトを登録
3. **パラメータ付きプロンプト** - 動的に内容を変更できるプロンプトを作成
4. **プロンプトの利用** - コーディングツールからプロンプトを呼び出して動作確認

handson-1で作成した `mcp-sample` ディレクトリをそのまま使用します。

### プロンプトの概念理解

handson-1では `@mcp.tool()` を使って関数をtoolとして登録しましたが、handson-2では `@mcp.prompt()` を使ってプロンプトを登録します。

ToolとPromptの違いは以下の通りです：
- **Tool**: 関数を実行して結果を返す（例：計算、API呼び出し）
- **Prompt**: 定型プロンプトテキストを返す（例：コードレビュー用のプロンプト、テンプレート）

プロンプトには、パラメータを受け取って動的に内容を変更できるものと、固定のテキストを返すものの2種類があります。

### プロンプトの実装

まずは、固定のテキストを返すプロンプトを作成します。

handson-1で作成した `main.py` を開き、既存のコードの下に以下の関数を追加します。

```python
@mcp.prompt()
def review_diff() -> str:
    """Review a code diff"""
    return (
        'あなたは優秀なテックリードであり、コードレビューの責任者です。\n' +
        '以下に貼り付けるテキストは、開発中のソースコードに対する `git diff` の出力結果です。\n' +
        'これらを解析し、コミットする前に修正すべき点がないかレビューしてください。'
    )
```

このプロンプトは以下の特徴があります：
- パラメータを受け取らない
- 常に同じ定型プロンプトテキストを返す
- コードレビュー用のテンプレートとして使用できる

### パラメータ付きプロンプトの実装

次に、パラメータを受け取って動的に内容を変更できるプロンプトを作成します。

同じく `main.py` に、以下の関数を追加します。

```python
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "温かく親しみやすい挨拶を書いてください",
        "formal": "正式でプロフェッショナルな挨拶を書いてください",
        "casual": "カジュアルでリラックスした挨拶を書いてください",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."
```

このプロンプトは以下の特徴があります：
- `name` パラメータで挨拶する相手の名前を指定
- `style` パラメータで挨拶のスタイルを選択（デフォルトは "friendly"）
- パラメータの値に応じて、異なるプロンプトテキストを生成

### MCPサーバを利用した実行

プロンプトを利用する前に、MCPサーバを再起動してください。

```bash
uv run --with mcp main.py
```

プロンプトを利用する際は、コーディングツールのプロンプト機能から呼び出します。

例えば、`greet_user` プロンプトを使用する場合：
- プロンプトを選択すると、`name` と `style` のパラメータを入力できます
- プロンプトが生成され、それをチャットに送信して利用できます

`review_diff` プロンプトを使用する場合：
- プロンプトを選択すると、定型プロンプトが生成されます
- そのプロンプトにコード差分を追加して、コードレビューを依頼できます

MCPサーバのプロンプト機能が正常に動作していることが確認できるはずです。

## handson-3

MCPサーバでローカルファイルやWebリクエストを使った処理を実装し、実用的なツールやプロンプトを作成する方法を学びます。

1. **ローカルファイルの読み取り** - ファイルシステムからファイルを読み取ってプロンプトやツールで利用
2. **Webリクエストの処理** - HTTPリクエストを送信して外部APIからデータを取得

handson-1、handson-2で作成した `mcp-sample` ディレクトリをそのまま使用します。

### ローカルファイルを使った処理

MCPサーバでは、ローカルファイルシステムにアクセスしてファイルを読み取ることができます。これにより、設定ファイルの読み取り、ログファイルの解析、プロジェクト構造の把握などが可能になります。

handson-2では、プロンプトの内容を直接コード内に記述しましたが、より長いプロンプトやテンプレート化したい場合は、外部ファイルとして保存して読み取る方法が便利です。

まず、プロンプトの内容をファイルとして保存します。`review.md` というファイルを作成し、コードレビュー用のプロンプトテンプレートを記述します。

次に、`main.py` にローカルファイルを読み取るプロンプトを追加します。

```python
@mcp.prompt()
def review_diff() -> str:
    """Review a code diff"""
    with open(os.path.join(os.path.dirname(__file__), 'review.md'), 'r', encoding='utf-8') as f:
        return f.read()
```

このプロンプトは以下の特徴があります：
- `os.path.join(os.path.dirname(__file__), 'review.md')` で、`main.py` と同じディレクトリにある `review.md` ファイルのパスを取得
- `open()` でファイルを開き、`read()` で内容を読み取る
- ファイルの内容をそのままプロンプトとして返す
- プロンプトの内容をファイルで管理できるため、長いテンプレートや複数のバージョンを管理しやすい

### Webリクエストを使った処理

外部APIにHTTPリクエストを送信することで、天気情報の取得、データベースへの問い合わせ、外部サービスの利用などが可能になります。これにより、MCPサーバの機能を大幅に拡張できます。

WebページのHTMLを取得して解析する場合、HTTPリクエストを送信するためのライブラリとHTMLをパースするためのライブラリが必要です。

まず、必要なライブラリをインストールします。

```bash
uv add requests beautifulsoup4
```

次に、Yahoo! JAPANのトップページから「主要 ニュース」セクションのニュース一覧を取得するツールを実装します。

まず、必要なライブラリをインポートします。

```python
import requests
from bs4 import BeautifulSoup
```

次に、Yahoo! JAPANのニュースを取得するツールを実装します。

`mcp.tool()` は文字列だけでなく、JSONシリアライズ可能なデータ構造（辞書、リストなど）を返すこともできます。構造化されたデータを返すことで、AIアシスタントがより効率的にデータを処理できます。

```python
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
        
        for element in news_elements[:10]:  # 最大10件まで取得
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
```

このツールは以下の特徴があります：
- `requests.get()` でYahoo! JAPANのトップページにHTTPリクエストを送信
- `BeautifulSoup` でHTMLをパースし、ニュース項目を抽出
- エラーハンドリングを実装し、リクエスト失敗時やパースエラー時に適切なメッセージを返す
- **辞書形式で構造化されたデータを返す**ことで、AIアシスタントが各ニュースのタイトルやURLを個別に処理できる
- 各ニュース項目にタイトルとURLを含めることで、より詳細な情報を提供

**注意**: 実際のYahoo! JAPANのHTML構造に合わせて、セレクタ（`soup.select()` の引数）を調整する必要があります。ブラウザの開発者ツールでHTML構造を確認し、適切なセレクタを指定してください。

以下のようにチャットに送信して作成したツールを実行すると、Yahoo! JAPANのトップページの主要タブのニュースの一覧が取得できます。

```text
最新のニュースを教えて
```
