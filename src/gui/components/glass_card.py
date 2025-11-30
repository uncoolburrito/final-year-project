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
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 10),
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            expand=expand,
            on_click=on_click,
        )
