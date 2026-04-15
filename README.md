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

1.  **MCP Server (`mcp_server.py`)**: Implements the actual tools. Every time a tool is called, it sends a notification to the bridge.
2.  **Communication Bridge (`bridge.py`)**: A lightweight FastAPI server that receives events from the MCP server and broadcasts them via WebSockets.
3.  **Monitoring GUI (`gui_app.py`)**: A Flet-based dashboard that connects to the bridge and displays search history and live activity.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **`uv`** (recommended for fast dependency management)

### Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd search-MCP
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

### Running the System

To use the full monitoring experience, you need to run all three components in separate terminal windows (or in the background).

**1. Start the Bridge (Communication Layer)**
```bash
uv run python bridge.py
```
*The bridge will run on `http://localhost:8002`.*

**2. Start the MCP Server**
```bash
uv run python mcp_server.py
```

**3. Start the Monitoring GUI**
```bash
uv run python gui_app.py
```
*The GUI will open in your default web browser.*

## 🤖 Usage with Claude Desktop

To use the tools within Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
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
```

*Note: Make sure the **Bridge** is running in a separate terminal before you start Claude, otherwise the GUI won't be able to receive updates!*

## 🛠 Tools

### `search`
Performs a DuckDuckGo search for a given query.
- **Parameter**: `query` (string) - The search term.
- **Returns**: A formatted list of titles, URLs, and snippets.

### `fetch_content`
Extracts the text content from a specific URL.
- **Parameter**: `url` (string) - The URL to scrape.
- **Returns**: The cleaned text content of the page.

## 📝 License
This project is open source.
EOF > /workspace/project/search-MCP/README.md
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

1.  **MCP Server (`mcp_server.py`)**: Implements the actual tools. Every time a tool is called, it sends a notification to the bridge.
2.  **Communication Bridge (`bridge.py`)**: A lightweight FastAPI server that receives events from the MCP server and broadcasts them via WebSockets.
3.  **Monitoring GUI (`gui_app.py`)**: A Flet-based dashboard that connects to the bridge and displays search history and live activity.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **`uv`** (recommended for fast dependency management)

### Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd search-MCP
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

### Running the System

To use the full monitoring experience, you need to run all three components in separate terminal windows (or in the background).

**1. Start the Bridge (Communication Layer)**
```bash
uv run python bridge.py
```
*The bridge will run on `http://localhost:8002`.*

**2. Start the MCP Server**
```bash
uv run python mcp_server.py
```

**3. Start the Monitoring GUI**
```bash
uv run python gui_app.py
```
*The GUI will open in your default web browser.*

## 🤖 Usage with Claude Desktop

To use the tools within Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
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
```

*Note: Make sure the **Bridge** is running in a separate terminal before you start Claude, otherwise the GUI won't be able to receive updates!*

## 🛠 Tools

### `search`
Performs a DuckDuckGo search for a given query.
- **Parameter**: `query` (string) - The search term.
- **Returns**: A formatted list of titles, URLs, and snippets.

### `fetch_content`
Extracts the text content from a specific URL.
- **Parameter**: `url` (string) - The URL to scrape.
- **Returns**: The cleaned text content of the page.

## 📝 License
This project is open source.
