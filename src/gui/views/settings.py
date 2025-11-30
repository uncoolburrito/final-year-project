import flet as ft
from src.gui.components.glass_card import GlassCard

class SettingsView(ft.Column):
    def __init__(self):
        super().__init__(expand=True, spacing=20)
        
        self.controls = [
            ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
            GlassCard(
                content=ft.Column(
                    controls=[
                        ft.Switch(label="Start on Boot", value=False),
                        ft.Switch(label="Dark Mode", value=True),
                        ft.Divider(color=ft.Colors.WHITE10),
                        ft.Text("About", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Text Expander v0.1.0", color=ft.Colors.WHITE54),
                    ]
                )
            )
        ]
