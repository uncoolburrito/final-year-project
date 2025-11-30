import flet as ft

class Sidebar(ft.Container):
    def __init__(self, on_nav_change):
        super().__init__()
        self.on_nav_change = on_nav_change
        self.width = 250
        self.padding = 20
        self.bgcolor = ft.Colors.with_opacity(0.02, ft.Colors.WHITE)
        self.border = ft.border.only(right=ft.border.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)))
        
        self.content = ft.Column(
            controls=[
                ft.Text("EXPANDER", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                ft.Container(height=20),
                self._build_nav_item("Dashboard", ft.icons.DASHBOARD_ROUNDED, 0),
                self._build_nav_item("Library", ft.icons.LIBRARY_BOOKS_ROUNDED, 1),
                self._build_nav_item("Profiles", ft.icons.APPS_ROUNDED, 2),
                ft.Container(expand=True),
                self._build_nav_item("Settings", ft.icons.SETTINGS_ROUNDED, 3),
            ]
        )
        self.selected_index = 0
        self.nav_items = []

    def _build_nav_item(self, label, icon, index):
        
        def on_hover(e):
            e.control.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.WHITE) if e.data == "true" else ft.Colors.TRANSPARENT
            e.control.update()

        def on_click(e):
            self.selected_index = index
            self.on_nav_change(index)
            # Update visuals (simplified)
            
        item = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=20, color=ft.Colors.WHITE70),
                    ft.Text(label, size=14, color=ft.Colors.WHITE),
                ],
                spacing=15,
            ),
            padding=10,
            border_radius=10,
            on_hover=on_hover,
            on_click=on_click,
            cursor=ft.Cursor.CLICK,
        )
        self.nav_items.append(item)
        return item
