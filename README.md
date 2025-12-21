# handson-mcp-server

ハンズオン「MCPサーバを作って、コーディングツールから使ってみよう」

## 内容

- handson-1
  - 簡単なMCPサーバを起動してみる
- handson-2
  - promptとして使う
- handson-3
  - ローカルファイルやWebリクエストを使った処理を行う

## 使い方

### 初期設定

```
uv sync
```

### MCPサーバの設定

各種コーディングツールに合わせて以下の内容を利用してください。

```.json
{
	"mcpServers": {
		"handson": {
			"type": "http",
			"url": "http://127.0.0.1:8000/mcp"
		}
	}
}
```
