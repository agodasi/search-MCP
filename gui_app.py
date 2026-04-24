import flet as ft
import asyncio
import websockets
import json
import httpx
import os
import sys
from datetime import datetime
from config_manager import load_config, save_config

# --- Default Theme Colors (will be updated dynamically) ---
BG_COLOR_DARK = "#0F172A"  # Deep Slate
BG_COLOR_LIGHT = "#F1F5F9" # Light Slate
PANEL_COLOR_DARK = "white10"
PANEL_COLOR_LIGHT = "black05"
ACCENT_COLOR = "#38BDF8"  # Cyan
SECONDARY_COLOR = "#A855F7"  # Purple
SUCCESS_COLOR = "#4ADE80"
ERROR_COLOR = "#F87171"

I18N = {
    "en": {
        "title_sub": "Intelligent Web Monitoring System",
        "stop_btn": "System Stop",
        "disconnected": "Disconnected",
        "no_query": "No active query",
        "exe_search": "Execute a search to see results...",
        "content_wait": "Extracted content will appear here...",
        "connected": "Connected to Bridge",
        "conn_lost": "Connection Lost",
        "searching": "Searching...",
        "results_loaded": "Results Loaded",
        "no_results": "No results found.",
        "fetching": "Fetching Page...",
        "content_ready": "Content Ready",
        "page_content": "PAGE CONTENT",
        "error_occ": "Error Occurred",
        "fetch_err": "FETCH ERROR",
        "settings": "Settings",
        "appearance": "Appearance",
        "dark_mode": "Dark Mode",
        "network": "Network",
        "port_label": "MCP Bridge Port",
        "app_settings": "App Settings",
        "language": "Language",
        "restart_warn": "* Restart the app to apply port/lang changes",
        "cancel": "Cancel",
        "save": "Save",
        "history_title": "HISTORY",
        "query_title": "ACTIVE QUERY",
        "results_title": "SEARCH RESULTS",
        "viewer_title": "PAGE VIEWER",
        "restart_snack": "Restart the app to apply network or language settings"
    },
    "ja": {
        "title_sub": "インテリジェントWeb監視システム",
        "stop_btn": "システム停止",
        "disconnected": "切断されています",
        "no_query": "待機中",
        "exe_search": "検索を実行するとここに結果が表示されます...",
        "content_wait": "抽出されたコンテンツがここに表示されます...",
        "connected": "Bridgeに接続完了",
        "conn_lost": "接続が失われました",
        "searching": "検索中...",
        "results_loaded": "結果を取得しました",
        "no_results": "結果が見つかりませんでした。",
        "fetching": "ページを取得中...",
        "content_ready": "コンテンツ準備完了",
        "page_content": "ページコンテンツ",
        "error_occ": "エラーが発生しました",
        "fetch_err": "取得エラー",
        "settings": "設定",
        "appearance": "外観",
        "dark_mode": "ダークモード",
        "network": "ネットワーク",
        "port_label": "MCP Bridge ポート",
        "app_settings": "アプリ設定",
        "language": "言語",
        "restart_warn": "※ポート・言語設定はアプリの再起動後に反映されます",
        "cancel": "キャンセル",
        "save": "保存",
        "history_title": "履歴 (HISTORY)",
        "query_title": "現在の検索",
        "results_title": "検索結果",
        "viewer_title": "最新ページ",
        "restart_snack": "設定を反映させるにはアプリを再起動してください"
    }
}

class ModernCard(ft.Container):
    def __init__(self, content, title=None, icon=None, expand=False):
        super().__init__(
            expand=expand,
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=ACCENT_COLOR, size=20) if icon else ft.Container(),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE) if title else ft.Container(),
                ], alignment=ft.MainAxisAlignment.START) if title else ft.Container(),
                ft.Container(content=content, expand=True) if expand else content
            ], spacing=10, expand=expand),
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            blur=ft.Blur(10, 10),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

class ResultCard(ft.Container):
    def __init__(self, title, url, snippet, on_click):
        super().__init__(
            content=ft.Column([
                ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=ACCENT_COLOR, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(url, size=11, color=ft.Colors.BLUE_300, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(snippet, size=12, color=ft.Colors.ON_SURFACE_VARIANT, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ], spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            on_click=lambda _: on_click(url),
            on_hover=self._on_hover
        )

    def _on_hover(self, e):
        e.control.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST if e.data == "true" else ft.Colors.SURFACE
        e.control.update()

class Dashboard(ft.Container):
    def __init__(self, websocket_url, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.websocket_url = websocket_url
        self.expand = True
        
        self.config = load_config()
        self.is_dark = self.config.get("theme", "dark") == "dark"
        self.lang = self.config.get("language", "en")
        self._apply_theme_colors()
        self.image = ft.DecorationImage(
            src="https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=2029&auto=format&fit=crop",
            opacity=0.05,
            fit=ft.BoxFit.COVER,
        )
        self.history = []
        
        # --- UI Elements ---
        self.status_lamp = ft.Container(width=12, height=12, border_radius=6, bgcolor=ft.Colors.GREY_600)
        self.status_text = ft.Text(self.t("disconnected"), size=14, color=ft.Colors.ON_SURFACE_VARIANT)
        self.progress_bar = ft.ProgressBar(color=ACCENT_COLOR, bgcolor=ft.Colors.TRANSPARENT, visible=False)
        
        self.current_query = ft.Text(self.t("no_query"), size=18, weight=ft.FontWeight.W_500, color=ACCENT_COLOR)
        self.results_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)
        self.content_viewer = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.history_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
        
        # Initial view
        self.results_column.controls.append(ft.Text(self.t("exe_search"), color=ft.Colors.OUTLINE))
        self.content_viewer.controls.append(ft.Text(self.t("content_wait"), color=ft.Colors.OUTLINE))
        
        self.content = self._build_content()

    def t(self, key):
        return I18N.get(self.lang, I18N["en"]).get(key, key)

    async def connect_websocket(self):
        while True:
            try:
                async with websockets.connect(self.websocket_url) as websocket:
                    self.status_lamp.bgcolor = SUCCESS_COLOR
                    self.status_text.value = self.t("connected")
                    self.status_text.color = SUCCESS_COLOR
                    self.update()
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self.handle_event(data)
                        except Exception as e:
                            print(f"Error handling event: {e}")
            except Exception as e:
                self.status_lamp.bgcolor = ERROR_COLOR
                self.status_text.value = self.t("conn_lost")
                self.status_text.color = ERROR_COLOR
                try:
                    self.update()
                except:
                    pass
                await asyncio.sleep(3) # Retry

    async def handle_event(self, event):
        event_type = event.get("type")
        data = event.get("data", {})

        if event_type == "search_query":
            query = data.get("query")
            self.current_query.value = query
            self.status_lamp.bgcolor = ACCENT_COLOR
            self.status_text.value = self.t("searching")
            self.progress_bar.visible = True
            
            if query not in self.history:
                self.history.insert(0, query)
                self.history_list.controls.insert(0, ft.ListTile(
                    title=ft.Text(query, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                    on_click=lambda e, q=query: self.set_query(q)
                ))
            self.update()

        elif event_type == "search_results":
            print(f"DEBUG: Received search_results with {len(data.get('results', []))} items")
            self.status_lamp.bgcolor = SUCCESS_COLOR
            self.status_text.value = self.t("results_loaded")
            self.progress_bar.visible = False
            
            self.results_column.controls = []
            results = data.get("results", [])
            for res in results:
                title = res.get('title', 'No Title')
                url = res.get('href') or res.get('link') or '#'
                snippet = res.get('body') or res.get('snippet') or 'No snippet available.'
                
                self.results_column.controls.append(
                    ResultCard(title, url, snippet, self.on_result_click)
                )
            if not results:
                self.results_column.controls.append(ft.Text(self.t("no_results"), color=ft.Colors.OUTLINE))
            self.update()

        elif event_type == "fetch_url" or event_type == "fetch_url_request":
            self.status_text.value = self.t("fetching")
            self.content_viewer.controls = [
                ft.Text(f"Target: {data.get('url', 'Unknown')}", size=12, color=ACCENT_COLOR),
                ft.ProgressBar(color=SECONDARY_COLOR)
            ]
            self.update()

        elif event_type == "content_extracted":
            self.status_text.value = self.t("content_ready")
            content = data.get("content", "No content text available.")
            self.content_viewer.controls = [
                ft.Text(self.t("page_content"), weight=ft.FontWeight.BOLD, color=SECONDARY_COLOR),
                ft.Text(data.get("url"), size=11, color=ft.Colors.OUTLINE, selectable=True),
                ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
                ft.Text(content, size=13, color=ft.Colors.ON_SURFACE, selectable=True)
            ]
            self.update()

        elif event_type == "error":
            self.status_lamp.bgcolor = ERROR_COLOR
            self.status_text.value = self.t("error_occ")
            self.progress_bar.visible = False
            
            error_msg = data.get("error", "Unknown error")
            source = data.get("source", "search")
            
            if source == "fetch":
                self.content_viewer.controls = [
                    ft.Text(self.t("fetch_err"), weight=ft.FontWeight.BOLD, color=ERROR_COLOR),
                    ft.Text(data.get("url", "Unknown URL"), size=11, color=ft.Colors.OUTLINE),
                    ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
                    ft.Text(error_msg, size=13, color=ERROR_COLOR)
                ]
            else:
                self.results_column.controls.append(ft.Text(f"Error: {error_msg}", color=ERROR_COLOR))
            self.update()

    def set_query(self, query):
        self.current_query.value = query
        self.update()

    def on_result_click(self, url):
        print(f"DEBUG: Result clicked: {url}")
        asyncio.create_task(self.trigger_fetch(url))

    async def trigger_fetch(self, url):
        try:
            async with httpx.AsyncClient() as client:
                payload = {"type": "fetch_url_request", "data": {"url": url}}
                bridge_url = self.websocket_url.replace("ws://", "http://").replace("/ws", "/event")
                await client.post(bridge_url, json=payload)
        except Exception as e:
            print(f"Error triggering fetch: {e}")

    async def stop_app(self, e):
        try:
            if hasattr(self.page.window, "close_async"):
                await self.page.window.close_async()
            else:
                await self.page.window.close()
        except:
            pass

    def _apply_theme_colors(self):
        self.bgcolor = BG_COLOR_DARK if self.is_dark else BG_COLOR_LIGHT
        self.page_ref.bgcolor = self.bgcolor
        self.page_ref.theme_mode = ft.ThemeMode.DARK if self.is_dark else ft.ThemeMode.LIGHT
        try:
            self.page_ref.update()
        except:
            pass

    def open_settings(self, e):
        # UI controls for settings
        theme_switch = ft.Switch(
            label=self.t("dark_mode"), 
            value=self.is_dark,
            active_color=ACCENT_COLOR
        )
        port_field = ft.TextField(
            label=self.t("port_label"), 
            value=str(self.config.get("port", 8002)),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        lang_dropdown = ft.Dropdown(
            label=self.t("language"),
            value=self.lang,
            options=[
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ja", "日本語")
            ],
            width=150
        )
        
        def save_and_close(e):
            new_port = int(port_field.value) if port_field.value.isdigit() else 8002
            is_dark_new = theme_switch.value
            new_lang = lang_dropdown.value
            
            # Save to file
            self.config["theme"] = "dark" if is_dark_new else "light"
            self.config["language"] = new_lang
            
            port_changed = self.config.get("port") != new_port
            lang_changed = self.lang != new_lang
            self.config["port"] = new_port
            
            save_config(self.config)
            
            # Apply theme instantly
            self.is_dark = is_dark_new
            self._apply_theme_colors()
            
            dlg.open = False
            self.page_ref.update()
            
            if port_changed or lang_changed:
                # Capture the message in the CURRENT language before updating state
                restart_msg = self.t("restart_snack")
                self.lang = new_lang
                # Show snackbar info
                snack = ft.SnackBar(ft.Text(restart_msg, color=ft.Colors.WHITE), bgcolor=ERROR_COLOR)
                self.page_ref.overlay.append(snack)
                snack.open = True
                self.page_ref.update()

        def cancel_close(e):
            dlg.open = False
            self.page_ref.update()

        dlg = ft.AlertDialog(
            title=ft.Text(self.t("settings"), weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(self.t("appearance"), size=16, weight=ft.FontWeight.W_600),
                theme_switch,
                ft.Divider(),
                ft.Text(self.t("app_settings"), size=16, weight=ft.FontWeight.W_600),
                lang_dropdown,
                ft.Divider(),
                ft.Text(self.t("network"), size=16, weight=ft.FontWeight.W_600),
                port_field,
                ft.Text(self.t("restart_warn"), size=12, color=ft.Colors.RED_400)
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton(self.t("cancel"), on_click=cancel_close),
                ft.FilledButton(self.t("save"), on_click=save_and_close, bgcolor=ACCENT_COLOR, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.overlay.append(dlg)
        dlg.open = True
        self.page_ref.update()

    def _build_content(self):
        header = ft.Row([
            ft.Row([
                ft.IconButton(icon=ft.Icons.SETTINGS_ROUNDED, icon_color=ACCENT_COLOR, on_click=self.open_settings),
                ft.Column([
                    ft.Text("SEARCH-MCP", size=24, weight=ft.FontWeight.W_900, color=ft.Colors.ON_SURFACE),
                    ft.Text(self.t("title_sub"), size=12, color=ft.Colors.ON_SURFACE_VARIANT, italic=True),
                ]),
                ft.VerticalDivider(width=20),
                ft.Column([
                    ft.Row([self.status_lamp, self.status_text], spacing=10),
                    self.progress_bar,
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER if sys.platform != "web" else ft.MainAxisAlignment.START),
            ]),
            ft.FilledButton(
                self.t("stop_btn"), 
                icon=ft.Icons.STOP_ROUNDED, 
                color=ft.Colors.WHITE, 
                bgcolor=ERROR_COLOR,
                on_click=self.stop_app,
                visible=not self.page_ref.web # Hide on web
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        main_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(color=ft.Colors.OUTLINE_VARIANT, height=10),
                ModernCard(
                    content=self.current_query,
                    title=self.t("query_title"),
                    icon=ft.Icons.SEARCH_ROUNDED,
                    expand=False
                ),
                ft.Row([
                    ft.Container(
                        content=ModernCard(
                            content=self.history_list,
                            title=self.t("history_title"),
                            icon=ft.Icons.HISTORY_ROUNDED,
                            expand=True
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=ModernCard(
                            content=self.results_column,
                            title=self.t("results_title"),
                            icon=ft.Icons.LIST_ALT_ROUNDED,
                            expand=True
                        ),
                        expand=2
                    ),
                    ft.Container(
                        content=ModernCard(
                            content=self.content_viewer,
                            title=self.t("viewer_title"),
                            icon=ft.Icons.DOCUMENT_SCANNER_ROUNDED,
                            expand=True
                        ),
                        expand=3
                    ),
                ], expand=True, spacing=20)
            ], spacing=15, expand=True),
            expand=True,
            padding=25
        )

        return main_content


async def main(page: ft.Page):
    config = load_config()
    page.title = "Search-MCP Premium Monitor"
    page.theme_mode = ft.ThemeMode.DARK if config.get("theme", "dark") == "dark" else ft.ThemeMode.LIGHT
    page.bgcolor = BG_COLOR_DARK if page.theme_mode == ft.ThemeMode.DARK else BG_COLOR_LIGHT
    page.window.width = 1400
    page.window.height = 900
    
    # Set window icon with absolute path resolution for frozen mode
    if getattr(sys, 'frozen', False):
        # When frozen, assets are in sys._MEIPASS/assets
        icon_path = os.path.join(sys._MEIPASS, "assets", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(sys._MEIPASS, "assets", "icon.png")
    else:
        # In dev mode, flet handles relative paths via assets_dir
        icon_path = "icon.ico"
    
    page.window.icon = icon_path
    
    page.padding = 0
    page.spacing = 0
    
    port = config.get("port", 8002)
    dashboard = Dashboard(f"ws://localhost:{port}/ws", page)
    page.add(dashboard)
    
    asyncio.create_task(dashboard.connect_websocket())

if __name__ == "__main__":
    # Check for WEB mode via environment variable or argument
    if os.getenv("FLET_WEB_PORT") or "--web" in sys.argv:
        port = int(os.getenv("FLET_WEB_PORT", 8550))
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
    else:
        ft.app(target=main)