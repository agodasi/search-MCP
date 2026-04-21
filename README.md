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
- **Windows インストーラー対応**: `installer.iss` を使用して簡単に配布可能な `.exe` 形式にパッケージ化可能。

## 🏗 アーキテクチャ

1.  **MCPサーバー (`main.py --mode mcp`)**: 実際のサーチ・スクレイピング処理。
2.  **通信ブリッジ (`main.py --mode bridge`)**: 各プロセス間の通知をブロードキャストする中継器。
3.  **モニタリングGUI (`main.py --mode gui`)**: 設定変更とリアルタイム表示を行うフロントエンド。

## 🚀 実行方法

### 依存関係のインストール
```bash
uv sync
```

### システムの一括起動（推奨）
すべてを一度に起動し、統合的に管理します：
```bash
uv run python main.py --mode all
```

*(個別に起動する場合は、`--mode bridge`, `--mode mcp`, `--mode gui` をそれぞれ指定して実行してください)*

## 🤖 Claude Desktop / Cursor での使用

`config.json` を開いて、以下の実行ファイルを指定してください：

```json
{
  "mcpServers": {
    "search-mcp": {
      "command": "path/to/search-mcp.exe",
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
- **Windows Packaging**: Includes Inno Setup scripts to build a standalone `.exe` installer.

## 🏗 Architecture

1.  **MCP Server (`main.py --mode mcp`)**: Handles tool execution and sends events to the bridge.
2.  **Bridge (`main.py --mode bridge`)**: Acts as a hub, broadcasting events via WebSockets.
3.  **GUI (`main.py --mode gui`)**: Displays real-time data and manages settings (saved in `config.json`).

## 🚀 Execution

### Setup
```bash
uv sync
```

### Launch Everything (Recommended)
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
      "command": "path/to/search_mcp.exe",
      "args": ["--mode", "mcp"]
    }
  }
}
```
