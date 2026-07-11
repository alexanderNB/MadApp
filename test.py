from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header, Input


class Tag(HorizontalGroup):
    DEFAULT_CSS = """
        Input {
            width: 5;
        }
    """
    def compose(self) -> ComposeResult:
        yield Button("Remove", variant="error")
        yield Input("test")

class TestApp(App):
    """A Textual app to manage stopwatches."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield VerticalScroll(Tag(), Tag(), Tag())


if __name__ == "__main__":
    app = TestApp()
    app.run()
