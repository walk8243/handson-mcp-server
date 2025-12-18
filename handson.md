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
