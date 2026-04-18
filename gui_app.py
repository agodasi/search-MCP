import flet as ft
import asyncio
import websockets
import json

class SearchHistoryItem(ft.ListTile):
    def __init__(self, query, on_click):
        self.query = query
        self.title = ft.Text(query, weight=ft.FontWeight.W_500)
        self.on_click = on_click
        self.on_tap = lambda _: on_click(query)

class Dashboard(ft.Column):
    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.history = []
        self.current_query = ft.Text("No active search", size=20, weight=ft.FontWeight.BOLD)
        self.status_text = ft.Text("Idle", color=ft.Colors.GREY_500)
        self.preview_text = ft.Text("", size=14)
        self.history_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    async def did_mount(self):
        asyncio.create_task(self.connect_websocket())

    async def connect_websocket(self):
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.status_text.value = "Connected to bridge"
                self.status_text.color = ft.Colors.GREEN_400
                self.update()
                
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_event(data)
        except Exception as e:
            self.status_text.value = f"Connection Error: {str(e)}"
            self.status_text.color = ft.Colors.RED_400
            self.update()

    async def handle_event(self, event):
        event_type = event.get("type")
        data = event.get("data", {})

        if event_type == "search_query":
            query = data.get("query")
            self.current_query.value = f"Searching for: {query}"
            self.status_text.value = "Searching..."
            self.status_text.color = ft.Colors.BLUE_400
            # Add to history if not already there
            if query not in self.history:
                self.history.append(query)
                self.history_list.controls.append(SearchHistoryItem(query, self.on_history_click))
            self.update()

        elif event_type == "search_results":
            self.status_text.value = "Results found"
            self.status_text.color = ft.Colors.GREEN_400
            results = data.get("results", [])
            preview = "\n".join([f"• {res['title']} ({res['href']})" for res in results[:5]])
            self.preview_text.value = preview
            self.update()

        elif event_type == "fetch_url":
            url = data.get("url")
            self.current_query.value = f"Extracting: {url}"
            self.status_text.value = "Extracting content..."
            self.status_text.color = ft.Colors.BLUE_400
            self.update()

        elif event_type == "content_extracted":
            self.status_text.value = "Content extracted"
            self.status_text.color = ft.Colors.GREEN_400
            self.preview_text.value = "Content extracted successfully. Check tool output in MCP."
            self.update()

        elif event_type == "error":
            self.status_text.value = "Error occurred"
            self.status_text.color = ft.Colors.RED_400
            self.preview_text.value = f"Error: {data.get('error') or data.get('msg', 'Unknown error')}"
            self.update()

    async def on_history_click(self, query):
        self.current_query.value = f"History: {query}"
        self.status_text.value = "Selected from history"
        self.preview_text.value = ""
        self.update()

    def build(self):
        return ft.Row(
            [
                # Sidebar
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Search History", size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            self.history_list,
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=300,
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    padding=20,
                ),
                # Main Area
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Search-MCP Monitor", size=30, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        self.current_query,
                                        self.status_text,
                                    ]),
                                    padding=20,
                                )
                            ),
                            ft.Text("Preview / Log:", size=18, weight=ft.FontWeight.W_500),
                            ft.Container(
                                content=ft.Text(self.preview_text, size=14),
                                expand=True,
                                bgcolor=ft.Colors.BLACK12,
                                padding=15,
                                border_radius=10,
                            ),
                        ],
                        expand=True,
                    ),
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
        )

async def main(page: ft.Page):
    page.title = "Search-MCP Monitor"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    
    dashboard = Dashboard("ws://localhost:8002/ws")
    page.add(dashboard)

if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)