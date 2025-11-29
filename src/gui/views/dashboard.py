import flet as ft
from flet import colors
from src.gui.components.glass_card import GlassCard

class DashboardView(ft.Column):
    def __init__(self):
        super().__init__(expand=True, spacing=20)
        
        self.status_text = ft.Text("Engine Active", size=24, weight=ft.FontWeight.BOLD)
        self.toggle_switch = ft.Switch(value=True, on_change=self.toggle_engine)
        
        self.controls = [
            ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            GlassCard(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                self.status_text,
                                ft.Text("Listening for abbreviations...", color=colors.WHITE54),
                            ],
                            expand=True,
                        ),
                        self.toggle_switch,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=30,
            ),
            ft.Row(
                controls=[
                    GlassCard(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.icons.FLASH_ON_ROUNDED, size=30, color=colors.AMBER),
                                ft.Text("124", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Expansions Today", size=12, color=colors.WHITE54),
                            ]
                        ),
                        expand=True,
                    ),
                    GlassCard(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.icons.TIMER_ROUNDED, size=30, color=colors.BLUE),
                                ft.Text("15m", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Time Saved", size=12, color=colors.WHITE54),
                            ]
                        ),
                        expand=True,
                    ),
                ],
                spacing=20,
            )
        ]

    def toggle_engine(self, e):
        is_on = self.toggle_switch.value
        self.status_text.value = "Engine Active" if is_on else "Engine Paused"
        self.status_text.update()
        # TODO: Send IPC to backend/hook
