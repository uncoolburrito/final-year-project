import flet as ft


class GlassCard(ft.Container):
    def __init__(
        self,
        content: ft.Control,
        width: int = None,
        height: int = None,
        padding: int = 20,
        expand: bool = False,
        on_click=None,
    ):
        super().__init__(
            content=content,
            width=width,
            height=height,
            padding=padding,
            border_radius=16,

            # Very safe visual defaults, no ft.colors / ft.animation / with_opacity
            bgcolor="rgba(255, 255, 255, 0.05)",  # soft translucent white
            border=ft.border.all(1, "#FFFFFF22"),  # subtle border

            # Drop blur/animation/shadow complexity for now to avoid version issues
            # You can add nicer visuals later once everything runs reliably.

            expand=expand,
            on_click=on_click,
        )
