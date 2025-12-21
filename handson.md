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
