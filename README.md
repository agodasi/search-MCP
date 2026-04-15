# Search-MCP (リアルタイム・モニタリングGUI付き)

Search-MCPは、DuckDuckGo検索とウェブコンテンツ抽出の2つの強力なツールを提供するModel Context Protocol (MCP) サーバーです。

このプロジェクトの最大の特徴は、**リアルタイム・モニタリング・ダッシュボード**を備えていることです。標準的なMCPサーバーはバックグラウンドで静かに動作しますが、Search-MCPにはモダンなデスクトップGUIが含まれており、LLMが何を検索し、ウェブからどのようなコンテンツを抽出しているかを、実行中の様子をそのまま視覚的に確認できます。

## ✨ 特徴

- **DuckDuckGo検索**: ウェブ上の情報を素早く検索。
- **コンテンツ抽出**: 任意のURLからクリーンなテキストコンテンツを抽出。
- **リアルタイム・モニタリング**: Fletで構築された、美しいダークモード対応のダッシュボード。
- **サイドカー・アーキテクチャ**: FastAPI/WebSocketブリッジを使用し、GUIがMCPサーバーから独立して動作することを保証。

## 🏗 アーキテクチャ

システムは主に3つのコンポーネントで構成されています：

1.  **MCPサーバー (\`mcp_server.py\`)**: 実際のツールを実装。ツールが呼び出されるたびにブリッジへ通知を送信します。
2.  **通信ブリッジ (\`bridge.py\`)**: 軽量なFastAPIサーバー。MCPサーバーからのイベントを受け取り、WebSocket経由でGUIへブロードキャストします。
3.  **モニタリングGUI (\`gui_app.py\`)**: Fletベースのダッシュボード。ブリッジに接続し、検索履歴やライブアクティビティを表示します。

## 🚀 はじめに

### 前提条件

- **Python 3.10以上**
- **\`uv\`** (高速な依存関係管理のために推奨)

### インストール

1. リポジトリをクローンします：
   \`\`\`bash
   git clone <your-repo-url>
   cd search-MCP
   \`\`\`

2. \`uv\` を使用して依存関係をインストールします：
   \`\`\`bash
   uv sync
   \`\`\`

### 実行方法

すべてのコンポーネントを一度に起動するには、`run_all.py` を使用してください。

\`\`\`bash
uv run python run_all.py
\`\`\`

個別に実行する場合は、以下の手順で行います：

**1. ブリッジの起動 (通信レイヤー)**
\`\`\`bash
uv run python bridge.py
\`\`\`
*ブリッジは \`http://localhost:8002\` で動作します。*

**2. MCPサーバーの起動**
\`\`\`bash
uv run python mcp_server.py
\`\`\`

**3. モニタリングGUIの起動**
\`\`\`bash
uv run python gui_app.py
\`\`\`
*GUIはデフォルトのウェブブラウザで開きます。*

## 🤖 Claude Desktopでの使用方法

Claude Desktopでツールを使用するには、\`claude_desktop_config.json\` に以下を追加してください：

\`\`\`json
{
  "mcpServers": {
    "search-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/search-MCP",
        "run",
        "python",
        "mcp_server.py"
      ]
    }
  }
}
\`\`\`

*注意: Claudeを起動する前に、必ず別のターミナルで**ブリッジ**が動作していることを確認してください。そうしないと、GUIが更新を受け取れません！*

## 🛠 ツール

### \`search\`
指定したクエリでDuckDuckGo検索を実行します。
- **引数**: \`query\` (string) - 検索語。
- **戻り値**: タイトル、URL、スニペットのフォーマット済みリスト。

### \`fetch_content\`
指定したURLからテキストコンテンツを抽出します。
- **引数**: \`url\` (string) - スクレイピングするURL。
- **戻り値**: ページのクリーンなテキストコンテンツ。

---

# Search-MCP with Real-time Monitoring GUI

Search-MCP is an Model Context Protocol (MCP) server that provides two powerful tools: DuckDuckGo search and web content extraction. 

What makes this project unique is its **real-time monitoring dashboard**. While standard MCP servers operate silently in the background, Search-MCP includes a modern desktop GUI that allows you to see exactly what the LLM is searching for and what content it is extracting from the web, as it happens.

## ✨ Features

- **DuckDuckGo Search**: Quickly find information across the web.
- **Content Extraction**: Scrape clean text content from any URL.
- **Real-time Monitoring**: A beautiful, dark-mode dashboard built with Flet.
- **Sidecar Architecture**: Uses a FastAPI/WebSocket bridge to ensure the GUI remains decoupled from the MCP server.

## 🏗 Architecture

The system consists of three main components working in harmony:

1.  **MCP Server (\`mcp_server.py\`)**: Implements the actual tools. Every time a tool is called, it sends a notification to the bridge.
2.  **Communication Bridge (\`bridge.py\`)**: A lightweight FastAPI server that receives events from the MCP server and broadcasts them via WebSockets.
3.  **Monitoring GUI (\`gui_app.py\`)**: A Flet-based dashboard that connects to the bridge and displays search history and live activity.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **\`uv\`** (recommended for fast dependency management)

### Installation

1. Clone this repository:
   \`\`\`bash
   git clone <your-repo-url>
   cd search-MCP
   \`\`\`

2. Install dependencies using \`uv\`:
   \`\`\`bash
   uv sync
   \`\`\`

### Running the System

To use the full monitoring experience, you need to run all three components in separate terminal windows (or in the background).

**1. Start the Bridge (Communication Layer)**
\`\`\`bash
uv run python bridge.py
\`\`\`
*The bridge will run on \`http://localhost:8002\`.*

**2. Start the MCP Server**
\`\`\`bash
uv run python mcp_server.py
\`\`\`

**3. Start the Monitoring GUI**
\`\`\`bash
uv run python gui_app.py
\`\`\`
*The GUI will open in your default web browser.*

## 🤖 Usage with Claude Desktop

To use the tools within Claude Desktop, add the following to your \`claude_desktop_config.json\`:

\`\`\`json
{
  "mcpServers": {
    "search-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/search-MCP",
        "run",
        "python",
        "mcp_server.py"
      ]
    }
  }
}
\`\`\`

*Note: Make sure the **Bridge** is running in a separate terminal before you start Claude, otherwise the GUI won't be able to receive updates!*

## 🛠 Tools

### \`search\`
Performs a DuckDuckGo search for a given query.
- **Parameter**: \`query\` (string) - The search term.
- **Returns**: A formatted list of titles, URLs, and snippets.

### \`fetch_content\`
Extracts the text content from a specific URL.
- **Parameter**: \`url\` (string) - The URL to scrape.
- **Returns**: The cleaned text content of the page.

## 📝 License
This project is open source.