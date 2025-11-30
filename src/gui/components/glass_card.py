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

            # was: bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
            bgcolor="rgba(255, 255, 255, 0.05)",  # soft translucent white

            # was: border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
            border=ft.border.all(1, "rgba(255, 255, 255, 0.10)"),

            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),

            # was: color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color="rgba(0, 0, 0, 0.10)",
                offset=ft.Offset(0, 10),
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            expand=expand,
            on_click=on_click,
        )
