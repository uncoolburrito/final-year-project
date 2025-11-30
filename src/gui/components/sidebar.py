import flet as ft


class Sidebar(ft.Container):
    def __init__(self, on_nav_change):
        super().__init__()
        self.on_nav_change = on_nav_change
        self.width = 250
        self.padding = 20

        # Simple background and border using color strings
        self.bgcolor = "rgba(255, 255, 255, 0.02)"
        self.border = ft.border.only(
            right=ft.border.BorderSide(1, "rgba(255, 255, 255, 0.10)")
        )

        self.selected_index = 0
        self.nav_items = []

        self.content = ft.Column(
            controls=[
                ft.Text(
                    "EXPANDER",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="#AAAAAA",
                ),
                ft.Container(height=20),
                self._build_nav_item("Dashboard", 0),
                self._build_nav_item("Library", 1),
                self._build_nav_item("Profiles", 2),
                ft.Container(expand=True),
                self._build_nav_item("Settings", 3),
            ]
        )

    def _build_nav_item(self, label, index):
        def on_hover(e):
            e.control.bgcolor = (
                "rgba(255, 255, 255, 0.10)" if e.data == "true" else "transparent"
            )
            e.control.update()

        def on_click(e):
            self.selected_index = index
            self.on_nav_change(index)

        item = ft.Container(
            content=ft.Row(
                controls=[
                    # No icon here to avoid ft.icons issues; just text.
                    ft.Text(label, size=14, color="#FFFFFF"),
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
