import flet as ft
from src.gui.components.glass_card import GlassCard
from src.common.models import Snippet, TriggerType
from src.engine.store import Store


class LibraryView(ft.Row):
    def __init__(self, store: Store):
        super().__init__(expand=True, spacing=20)
        self.store = store

        # Left Pane: List
        self.snippet_list = ft.ListView(expand=True, spacing=10)

        # Simple search field, no icon to avoid ft.icons
        self.search_field = ft.TextField(
            hint_text="Search snippets...",
            border_radius=10,
            bgcolor="rgba(255, 255, 255, 0.10)",
            border_width=0,
            on_change=self.filter_snippets,
        )

        self.left_pane = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Library", size=32, weight=ft.FontWeight.BOLD),
                    self.search_field,
                    self.snippet_list,
                    # Use text instead of icon for the FAB
                    ft.FloatingActionButton(text="+", on_click=self.add_snippet),
                ],
                expand=True,
            ),
            width=300,
        )

        # Right Pane: Editor
        self.abbr_field = ft.TextField(label="Abbreviation", border_radius=10)
        self.content_field = ft.TextField(
            label="Expansion",
            multiline=True,
            min_lines=10,
            border_radius=10,
            text_style=ft.TextStyle(font_family="Consolas"),
        )
        self.trigger_dropdown = ft.Dropdown(
            label="Trigger",
            options=[
                ft.dropdown.Option(TriggerType.SPACE.value),
                ft.dropdown.Option(TriggerType.ENTER.value),
                ft.dropdown.Option(TriggerType.NONE.value),
            ],
            value=TriggerType.NONE.value,
        )

        self.editor_pane = GlassCard(
            content=ft.Column(
                controls=[
                    ft.Text("Edit Snippet", size=20, weight=ft.FontWeight.BOLD),
                    self.abbr_field,
                    self.trigger_dropdown,
                    self.content_field,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Save", on_click=self.save_snippet),
                            ft.TextButton(
                                "Delete",
                                on_click=self.delete_snippet,
                                style=ft.ButtonStyle(color={"": "#FF5252"}),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=20,
            ),
            expand=True,
        )

        self.controls = [self.left_pane, self.editor_pane]
        self.current_snippet = None

        # Build initial UI from store
        self.refresh_list()

    def refresh_list(self):
        self.snippet_list.controls.clear()

        for snippet in self.store.snippets:
            self.snippet_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                snippet.abbreviation,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                snippet.expansion,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                size=12,
                                color="#AAAAAA",
                            ),
                        ]
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor="rgba(255, 255, 255, 0.05)",
                    on_click=lambda e, s=snippet: self.select_snippet(s),
                    # IMPORTANT: no cursor=ft.Cursor.CLICK here
                )
            )

        # Only update if already attached to page
        if self.page is not None:
            self.update()

    def filter_snippets(self, e):
        # TODO: Optional filtering
        pass

    def select_snippet(self, snippet: Snippet):
        self.current_snippet = snippet
        self.abbr_field.value = snippet.abbreviation
        self.content_field.value = snippet.expansion
        self.trigger_dropdown.value = snippet.trigger.value

        if self.page is not None:
            self.update()

    def add_snippet(self, e):
        self.current_snippet = None
        self.abbr_field.value = ""
        self.content_field.value = ""
        self.trigger_dropdown.value = TriggerType.NONE.value

        if self.page is not None:
            self.update()

    def save_snippet(self, e):
        if not self.abbr_field.value:
            return

        if self.current_snippet:
            self.current_snippet.abbreviation = self.abbr_field.value
            self.current_snippet.expansion = self.content_field.value
            self.current_snippet.trigger = TriggerType(
                self.trigger_dropdown.value
            )
            self.store.update_snippet(self.current_snippet)
        else:
            new_snippet = Snippet(
                abbreviation=self.abbr_field.value,
                expansion=self.content_field.value,
                trigger=TriggerType(self.trigger_dropdown.value),
            )
            self.store.add_snippet(new_snippet)

        self.refresh_list()

    def delete_snippet(self, e):
        if self.current_snippet:
            self.store.delete_snippet(self.current_snippet.id)
            self.add_snippet(None)
            self.refresh_list()
