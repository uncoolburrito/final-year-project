import flet as ft
from flet import colors
from src.gui.components.sidebar import Sidebar
from src.gui.views.dashboard import DashboardView
from src.gui.views.library import LibraryView
from src.gui.views.settings import SettingsView
from src.engine.store import Store

def main(page: ft.Page):
    page.title = "Text Expander"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 1000
    page.window_height = 700
    page.bgcolor = "#1E1E1E" # Deep gray background
    
    # Initialize Store
    store = Store()
    
    # Views
    dashboard = DashboardView()
    library = LibraryView(store)
    settings = SettingsView()
    
    views = [dashboard, library, ft.Container(), settings] # Placeholder for Profiles
    
    content_area = ft.Container(
        content=dashboard,
        expand=True,
        padding=30,
    )
    
    def on_nav_change(index):
        content_area.content = views[index]
        content_area.update()
    
    sidebar = Sidebar(on_nav_change)
    
    page.add(
        ft.Row(
            controls=[
                sidebar,
                content_area,
            ],
            expand=True,
            spacing=0,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
