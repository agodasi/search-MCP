import flet as ft
import asyncio
import websockets
import json

class SearchHistoryItem(ft.Container):
    def __init__(self, query, on_click):
        super().__init__(
            content=ft.ListTile(
                title=ft.Text(query, weight=ft.FontWeight.W_500),
                on_click=lambda e: on_click(query),
            )
        )

class Dashboard(ft.Container):
    def __init__(self, websocket_url):
        super().__init__()
        self.websocket_url = websocket_url
        self.history = []
        
        # Current status
        self.status_text = ft.Text("Idle", size=12, color=ft.Colors.GREY_500)
        
        # Input section
        self.input_label = ft.Text("Current Input", size=16, weight=ft.FontWeight.BOLD)
        self.input_text = ft.Text("No input yet", size=14, color=ft.Colors.GREY_400)
        
        # Output section
        self.output_label = ft.Text("Current Output", size=16, weight=ft.FontWeight.BOLD)
        self.output_text = ft.Text("No output yet", size=14, color=ft.Colors.GREY_400)
        
        # Current page URL section
        self.url_label = ft.Text("Currently Accessed Page", size=16, weight=ft.FontWeight.BOLD)
        self.url_text = ft.Text("No URL accessed", size=14, color=ft.Colors.BLUE_400, selectable=True)
        
        self.history_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

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
            self.input_text.value = query
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
            self.output_text.value = preview
            self.update()

        elif event_type == "fetch_url":
            url = data.get("url")
            self.url_text.value = url
            self.status_text.value = "Extracting content..."
            self.status_text.color = ft.Colors.BLUE_400
            self.update()

        elif event_type == "content_extracted":
            self.status_text.value = "Content extracted"
            self.status_text.color = ft.Colors.GREEN_400
            self.output_text.value = "Content extracted successfully. Check tool output in MCP."
            self.update()

        elif event_type == "error":
            self.status_text.value = "Error occurred"
            self.status_text.color = ft.Colors.RED_400
            self.output_text.value = f"Error: {data.get('error') or data.get('msg', 'Unknown error')}"
            self.update()

    async def on_history_click(self, query):
        self.input_text.value = query
        self.status_text.value = "Selected from history"
        self.output_text.value = ""
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
                    bgcolor=ft.Colors.SURFACE,
                    padding=20,
                ),
                # Main Area
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Search-MCP Monitor", size=30, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            
                            # Status card
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Status", size=16, weight=ft.FontWeight.BOLD),
                                        self.status_text,
                                    ]),
                                    padding=20,
                                )
                            ),
                            
                            # Input section
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Current Input", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.input_text,
                                            bgcolor=ft.Colors.BLACK12,
                                            padding=15,
                                            border_radius=10,
                                        ),
                                    ]),
                                    padding=20,
                                )
                            ),
                            
                            # Output section
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Current Output", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.output_text,
                                            bgcolor=ft.Colors.BLACK12,
                                            padding=15,
                                            border_radius=10,
                                            expand=True,
                                        ),
                                    ]),
                                    padding=20,
                                )
                            ),
                            
                            # Currently accessed page URL
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Currently Accessed Page", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=self.url_text,
                                            bgcolor=ft.Colors.BLACK12,
                                            padding=15,
                                            border_radius=10,
                                        ),
                                    ]),
                                    padding=20,
                                )
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
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=5400, host="0.0.0.0")