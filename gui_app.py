import flet as ft
import asyncio
import websockets
import json
import httpx
import os
import sys
from datetime import datetime

# --- Theme Colors ---
BG_COLOR = "#0F172A"  # Deep Slate
PANEL_COLOR = "white10"
ACCENT_COLOR = "#38BDF8"  # Cyan
SECONDARY_COLOR = "#A855F7"  # Purple
SUCCESS_COLOR = "#4ADE80"
ERROR_COLOR = "#F87171"

class ModernCard(ft.Container):
    def __init__(self, content, title=None, icon=None, expand=False):
        super().__init__(
            expand=expand,
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=ACCENT_COLOR, size=20) if icon else ft.Container(),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE) if title else ft.Container(),
                ], alignment=ft.MainAxisAlignment.START) if title else ft.Container(),
                ft.Container(content=content, expand=True) if expand else content
            ], spacing=10, expand=expand),
            padding=20,
            border_radius=15,
            bgcolor=PANEL_COLOR,
            blur=ft.Blur(10, 10),
            border=ft.Border.all(1, "white10"),
        )

class ResultCard(ft.Container):
    def __init__(self, title, url, snippet, on_click):
        super().__init__(
            content=ft.Column([
                ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=ACCENT_COLOR, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(url, size=11, color=ft.Colors.BLUE_300, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(snippet, size=12, color=ft.Colors.WHITE70, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ], spacing=5),
            padding=15,
            border_radius=10,
            bgcolor="white05",
            on_click=lambda _: on_click(url),
            on_hover=self._on_hover
        )

    def _on_hover(self, e):
        e.control.bgcolor = "white12" if e.data == "true" else "white05"
        e.control.update()

class Dashboard(ft.Container):
    def __init__(self, websocket_url, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.websocket_url = websocket_url
        self.expand = True
        self.bgcolor = BG_COLOR
        self.image = ft.DecorationImage(
            src="https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=2029&auto=format&fit=crop",
            opacity=0.05,
            fit=ft.BoxFit.COVER,
        )
        self.history = []
        
        # --- UI Elements ---
        self.status_lamp = ft.Container(width=12, height=12, border_radius=6, bgcolor=ft.Colors.GREY_600)
        self.status_text = ft.Text("Disconnected", size=14, color=ft.Colors.WHITE70)
        self.progress_bar = ft.ProgressBar(color=ACCENT_COLOR, bgcolor=ft.Colors.TRANSPARENT, visible=False)
        
        self.current_query = ft.Text("No active query", size=18, weight=ft.FontWeight.W_500, color=ACCENT_COLOR)
        self.results_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)
        self.content_viewer = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.history_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
        
        # Initial view
        self.results_column.controls.append(ft.Text("Execute a search to see results...", color=ft.Colors.WHITE30))
        self.content_viewer.controls.append(ft.Text("Extracted content will appear here...", color=ft.Colors.WHITE30))
        
        self.content = self._build_content()

    async def connect_websocket(self):
        while True:
            try:
                async with websockets.connect(self.websocket_url) as websocket:
                    self.status_lamp.bgcolor = SUCCESS_COLOR
                    self.status_text.value = "Connected to Bridge"
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
                self.status_text.value = f"Connection Lost"
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
            self.status_text.value = "Searching..."
            self.progress_bar.visible = True
            
            if query not in self.history:
                self.history.insert(0, query)
                self.history_list.controls.insert(0, ft.ListTile(
                    title=ft.Text(query, size=13, color=ft.Colors.WHITE70),
                    on_click=lambda e, q=query: self.set_query(q)
                ))
            self.update()

        elif event_type == "search_results":
            print(f"DEBUG: Received search_results with {len(data.get('results', []))} items")
            self.status_lamp.bgcolor = SUCCESS_COLOR
            self.status_text.value = "Results Loaded"
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
                self.results_column.controls.append(ft.Text("No results found.", color=ft.Colors.WHITE30))
            self.update()

        elif event_type == "fetch_url" or event_type == "fetch_url_request":
            self.status_text.value = "Fetching Page..."
            target_url = data.get('url', 'Unknown')
            self.content_viewer.controls = [
                ft.Text(f"Target: {target_url}", size=12, color=ACCENT_COLOR),
                ft.ProgressBar(color=SECONDARY_COLOR)
            ]
            self.update()

        elif event_type == "content_extracted":
            self.status_text.value = "Content Ready"
            content = data.get("content", "No content text available.")
            self.content_viewer.controls = [
                ft.Text("PAGE CONTENT", weight=ft.FontWeight.BOLD, color=SECONDARY_COLOR),
                ft.Text(data.get("url"), size=11, color=ft.Colors.WHITE30, selectable=True),
                ft.Divider(color=ft.Colors.WHITE10),
                ft.Text(content, size=13, color=ft.Colors.WHITE, selectable=True)
            ]
            self.update()

        elif event_type == "error":
            self.status_lamp.bgcolor = ERROR_COLOR
            self.status_text.value = "Error Occurred"
            self.progress_bar.visible = False
            
            error_msg = data.get("error", "Unknown error")
            source = data.get("source", "search")
            
            if source == "fetch":
                self.content_viewer.controls = [
                    ft.Text("FETCH ERROR", weight=ft.FontWeight.BOLD, color=ERROR_COLOR),
                    ft.Text(data.get("url", "Unknown URL"), size=11, color=ft.Colors.WHITE30),
                    ft.Divider(color=ft.Colors.WHITE10),
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

    def _build_content(self):
        header = ft.Row([
            ft.Row([
                ft.Column([
                    ft.Text("SEARCH-MCP", size=24, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                    ft.Text("Intelligent Web Monitoring System", size=12, color=ft.Colors.WHITE30, italic=True),
                ]),
                ft.VerticalDivider(width=20),
                ft.Column([
                    ft.Row([self.status_lamp, self.status_text], spacing=10),
                    self.progress_bar,
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER if sys.platform != "web" else ft.MainAxisAlignment.START),
            ]),
            ft.FilledButton(
                "システム停止", 
                icon=ft.Icons.STOP_ROUNDED, 
                color=ft.Colors.WHITE, 
                bgcolor=ERROR_COLOR,
                on_click=self.stop_app,
                visible=not self.page_ref.web # Hide on web
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        sidebar = ft.Container(
            content=ft.Column([
                ft.Text("HISTORY", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE30),
                self.history_list,
            ], scroll=ft.ScrollMode.AUTO),
            width=250,
            padding=20,
            bgcolor="black12",
            border_radius=ft.BorderRadius.only(top_left=20, bottom_left=20)
        )

        main_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(color="white10", height=10),
                ModernCard(
                    content=self.current_query,
                    title="ACTIVE QUERY",
                    icon=ft.Icons.SEARCH_ROUNDED,
                    expand=False
                ),
                ft.Row([
                    ft.Container(
                        content=ModernCard(
                            content=self.results_column,
                            title="SEARCH RESULTS",
                            icon=ft.Icons.LIST_ALT_ROUNDED,
                            expand=True
                        ),
                        expand=2
                    ),
                    ft.Container(
                        content=ModernCard(
                            content=self.content_viewer,
                            title="PAGE VIEWER",
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

        return ft.Row([sidebar, main_content], spacing=0, expand=True)


async def main(page: ft.Page):
    page.title = "Search-MCP Premium Monitor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.window_width = 1400
    page.window_height = 900
    page.padding = 0
    page.spacing = 0
    
    dashboard = Dashboard("ws://localhost:8002/ws", page)
    page.add(dashboard)
    
    asyncio.create_task(dashboard.connect_websocket())

if __name__ == "__main__":
    # Check for WEB mode via environment variable or argument
    if os.getenv("FLET_WEB_PORT") or "--web" in sys.argv:
        port = int(os.getenv("FLET_WEB_PORT", 8550))
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
    else:
        ft.app(target=main)