# Search-MCP (リアルタイム・モニタリングGUI付き)

Search-MCPは、 DuckDuckGo検索とウェブコンテンツ抽出の2つのツールを提供するModel Context Protocol (MCP) サーバーです。
モダンなデスクトップGUI（Flet製）を備えており、LLMがバックグラウンドで行っている検索やコンテンツ抽出の様子をリアルタイムで視覚的に監視できます。

## ✨ 特徴

- **DuckDuckGo検索**: 最新のウェブ情報を検索。
- **コンテンツ抽出**: サイトからテキストを抽出。(User-Agentによる回避・文字コード自動判補正機能付き)
- **統合ダッシュボード**: 履歴・結果・コンテンツ閲覧を1画面に統合したモダンなレイアウト。
- **カスタマイズ機能**: 
    - **ダーク/ライトモード**: 外観の即時切り替え。
    - **多言語対応**: 日本語と英語をサポート。
    - **ポート設定**: 通信ポートの自由な変更。

## 🏗 アーキテクチャ

1.  **MCPサーバー (`main.py --mode mcp`)**: 実際のサーチ・スクレイピング処理。
2.  **通信ブリッジ (`main.py --mode bridge`)**: 各プロセス間の通知をブロードキャストする中継器。
3.  **モニタリングGUI (`main.py --mode gui`)**: 設定変更とリアルタイム表示を行うフロントエンド。

## 🚀 実行方法

### 1. インストーラーを使用する場合 (推奨)
配布されている `SearchMCP_Setup.exe` を実行してインストールしてください。
インストール後、スタートメニューまたはデスクトップのショートカットから起動すると、すべてのコンポーネント（Bridge, MCP, GUI）が自動的に開始されます。

### 2. `uv` を使用する場合 (開発者向け)
Python環境がインストールされている場合、以下の手順で実行できます。

**依存関係のインストール:**
```bash
uv sync
```

**システムの一括起動:**
```bash
uv run python main.py --mode all
```

*(個別に起動する場合は、`--mode bridge`, `--mode mcp`, `--mode gui` をそれぞれ指定してください)*

## 🤖 Claude Desktop / Cursor での使用

設定（`config.json` 等）で、以下の実行パスを指定してください：

```json
{
  "mcpServers": {
    "search-mcp": {
      "command": "C:/path/to/Search-MCP/search_mcp.exe",
      "args": ["--mode", "mcp"]
    }
  }
}
```

---

# Search-MCP with Real-time Monitoring GUI

Search-MCP is a Model Context Protocol (MCP) server providing DuckDuckGo search and web content extraction. 
It features a modern Flet-based desktop GUI, allowing you to visually monitor background LLM activity like search queries and scraped results in real-time.

## ✨ Features

- **DuckDuckGo Search**: Find the latest web information quickly.
- **Content Extraction**: Clean text extraction with bot-bypass (User-Agent) and auto-encoding detection.
- **Integrated Dashboard**: Single-pane layout for History, Results, and Page Content.
- **Customizable**: 
    - **Theme**: Instant toggle between Dark and Light modes.
    - **Localization**: Supports English (Default) and Japanese.
    - **Network**: Configurable communication ports.

## 🏗 Architecture

1.  **MCP Server (`main.py --mode mcp`)**: Handles tool execution and sends events to the bridge.
2.  **Bridge (`main.py --mode bridge`)**: Acts as a hub, broadcasting events via WebSockets.
3.  **GUI (`main.py --mode gui`)**: Displays real-time data and manages settings.

## 🚀 Execution

### 1. Using the Installer (Recommended)
Run the `SearchMCP_Setup.exe` to install the application.
Launch it via the Start Menu or Desktop shortcut. This will automatically start all components (Bridge, MCP, and GUI).

### 2. Using `uv` (For Developers)
If you have a Python environment setup, follow these steps:

**Install Dependencies:**
```bash
uv sync
```

**Launch Everything:**
```bash
uv run python main.py --mode all
```

*(To run individual components, use `--mode bridge`, `--mode mcp`, or `--mode gui` separately.)*

## 🤖 Usage with Claude / Cursor

Update your MCP configuration file to point to the executable:

```json
{
  "mcpServers": {
    "search-mcp": {
      "command": "C:/path/to/Search-MCP/search_mcp.exe",
      "args": ["--mode", "mcp"]
    }
  }
}
```
