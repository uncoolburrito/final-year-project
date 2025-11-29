import flet as ft
from flet import colors

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
            bgcolor=colors.with_opacity(0.05, colors.WHITE),
            border=ft.border.all(1, colors.with_opacity(0.1, colors.WHITE)),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=colors.with_opacity(0.1, colors.BLACK),
                offset=ft.Offset(0, 10),
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            expand=expand,
            on_click=on_click,
        )
