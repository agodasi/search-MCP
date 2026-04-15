# 1. OBJECTIVE
DuckDuckGo検索とURLのテキスト抽出機能を持つMCPサーバーを構築し、その動作状況（検索クエリ、取得結果、ログなど）をリアルタイムでモニタリングできるモダンなデスクトップGUIアプリを提供します。

# 2. CONTEXT SUMMARY
* **Backend:** Python (MCP SDK, `duckduckgo-search`, `beautifulsoup4`, `requests`)
* **Communication:** FastAPI + WebSockets (MCPサーバーからGUIへのリアルタイム通知用)
* **Frontend (GUI):** Flet (FlutterベースのPythonライブラリ。モダンなデスクトップUIを提供)
* **Architecture:** 
    * `MCP Server`: ツール実行時にWebSocket経由でログを送信。
    * `Bridge (FastAPI)`: MCPサーバーとGUIの仲介役。
    * `GUI (Flet)`: WebSocketでデータを受け取り、ダッシュボードとして表示。

# 3. APPROACH OVERVIEW
MCPサーバー単体ではGUIを持てない（LLMのプロセスとして動作するため）という制約を解決するため、「サイドカー・アーキテクチャ」を採用します。
1. MCPサーバーがツールを呼び出されるたびに、ローカルのWebSocketサーバーに「検索クエリ」や「抽出結果」を送信します。
2. GUIアプリは常にそのWebSocketを監視しており、データが届くたびに画面を自動更新します。
3. これにより、LLMが裏側で何をしているかを、ユーザーは視覚的に把握できます。

# 4. IMPLEMENTATION STEPS

## Phase 1: プロジェクト基盤の構築
* **Goal:** 開発環境のセットアップとディレクトリ構造の定義
* **Method:** `venv`による仮想環境作成、必要なライブラリ（`mcp`, `flet`, `fastapi`, `uvicorn`, `duckduckgo-search`, `beautifulsoup4`）のインストール。

## Phase 2: コアロジックの実装
* **Goal:** 検索と抽出の基本機能の実装
* **Method:** 
    * `search_engine.py`: `duckduckgo-search` を使用した検索関数の作成。
    * `content_extractor.py`: `requests` と `BeautifulSoup` を使用したテキスト抽出関数の作成。

## Phase 3: MCPサーバーと通信層の実装
* **Goal:** MCPツールの定義と、GUIへの通知メカニズムの構築
* **Method:**
    * `mcp_server.py`: `mcp` ライブラリを使用して `search` と `fetch_content` ツールを実装。
    * `bridge.py`: FastAPIを使用して、WebSocketエンドポイントを持つ軽量な通信サーバーを実装。MCPサーバーからログを受け取り、接続されているGUIへブロードキャストする機能を持たせる。

## Phase 4: モダンGUIの開発
* **Goal:** 検索プロセスを可視化するデスクトップアプリの作成
* **Method:**
    * `gui_app.py`: Fletを使用してUIを構築。
    * **UIデザイン:** 
        * 左サイドバー：検索履歴のリスト
        * メインエリア：現在の検索クエリ、実行ステータス（実行中/完了）、抽出されたテキストのプレビューを表示。
        * ダークモード対応のモダンなカード型デザイン。

## Phase 5: 統合テストと検証
* **Goal:** 全システムの連携確認
* **Method:** MCP InspectorまたはClaude Desktopを使用してツールを実行し、GUIに正しくログが表示されるかを確認する。

# 5. TESTING AND VALIDATION
* **検証方法:**
    1. MCPサーバーを起動し、FastAPI/WebSocketサーバーが動作していることを確認。
    2. GUIアプリを起動し、接続が確立されることを確認。
    3. MCPツール（検索）を呼び出し、GUI上の「検索履歴」と「ステータス」がリアルタイムで更新されるか。
    4. URLのテキスト抽出を実行し、GUIに抽出されたテキストの一部が表示されるか。
* **成功の定義:** LLMがツールを使った際、ユーザーはGUIを見るだけで「今何を検索し、どのサイトから何を取得したか」を直感的に把握できること。


