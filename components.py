from textual.app import ComposeResult
from textual.containers import Horizontal, HorizontalGroup
from textual.widget import Widget
from textual.widgets import Button, Input, Select


class Tag(HorizontalGroup):
    def __init__(self, tag=""):
        self.remove_button = Button("\uf00d", id="tag-remove", variant="error")
        self.input = Input(tag, id="tag-input")
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.input
        yield self.remove_button

    def on_button_pressed(self) -> None:
        self.remove()

class Ingrediant(HorizontalGroup):
    def __init__(self, ingrediant="", unit="g", amount=0):
        self.remove_button = Button("\uf00d", id="ingrediant-remove", variant="error")
        self.unit_select = Select([
                ("g", "g"),
                ("dl", "dl"),
                ("stk", "stk"),
                ("Omgange", "Omgange"),
                ("Dåser", "Dåser"),
                ("Glas", "Glas")],
                allow_blank=False,
                value=unit,
                id="ingrediant-unit"
            )
        self.amount_input = Input(str(amount), id="ingrediant-amount")
        self.input = Input(ingrediant, id="ingrediant-input")
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.input
        yield self.amount_input
        yield self.unit_select
        yield self.remove_button

    def on_button_pressed(self) -> None:
        self.remove()
