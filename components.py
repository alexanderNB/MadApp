from typing import ClassVar, override
from rich.segment import Segment
from rich.style import Style
from textual import events, on
from textual.app import ComposeResult
from textual.containers import Horizontal, HorizontalGroup
from textual.message import Message
from textual.selection import Selection
from textual.strip import Strip
from textual.types import SelectType
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Input, OptionList, RadioButton, Select, SelectionList
from textual.widgets.option_list import OptionDoesNotExist


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

    @override
    def compose(self) -> ComposeResult:
        yield self.input
        yield self.amount_input
        yield self.unit_select
        yield self.remove_button

    def on_button_pressed(self) -> None:
        self.remove()

    def test(self):
        return ["Test"]

    



class RadioSelectionList(SelectionList[str]):
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "selection-list--button",
        "selection-list--button-selected",
        "selection-list--button-hover",
        "selection-list--button-selected-hover",
    }
    """
    | Class | Description |
    | :- | :- |
    | `selection-list--button` | Target the default button style. |
    | `selection-list--button-selected` | Target a selected button style. |
    | `selection-list--button-hover` | Target a highlighted button style. |
    | `selection-list--button-selected-hover` | Target a highlighted selected button style. |
    """


    @override
    def _get_left_gutter_width(self) -> int:
        return len(
            RadioButton.BUTTON_LEFT
            + RadioButton.BUTTON_INNER
            + RadioButton.BUTTON_RIGHT
            + " "
        )

    @override
    def render_line(self, y: int) -> Strip:
        """Render a line in the display.

        Args:
            y: The line to render.

        Returns:
            A [`Strip`][textual.strip.Strip] that is the line to render.
        """

        # TODO: This is rather crufty and hard to fathom. Candidate for a rewrite.

        # First off, get the underlying prompt from OptionList.
        line_number = self.scroll_offset.y + y
        try:
            option_index, line_offset = self._lines[line_number]
            option = self.options[option_index]
        except IndexError:
            return Strip.blank(
                self.scrollable_content_region.width,
                self.get_visual_style("option-list--option").rich_style,
            )

        mouse_over = self._mouse_hovering_over == option_index
        component_class = ""
        if option.disabled:
            component_class = "option-list--option-disabled"
        elif mouse_over:
            component_class = "option-list--option-hover"

        if component_class:
            style = self.get_visual_style("option-list--option", component_class)
        else:
            style = self.get_visual_style("option-list--option")

        strips = self._get_option_render(option, style)
        try:
            strip = strips[line_offset]
        except IndexError:
            return Strip.blank(
                self.scrollable_content_region.width,
                self.get_visual_style("option-list--option").rich_style,
            )
        line = strip

        # We know the prompt we're going to display, what we're going to do
        # is place a CheckBox-a-like button next to it. So to start with
        # let's pull out the actual Selection we're looking at right now.
        _, scroll_y = self.scroll_offset
        selection_index = scroll_y + y
        try:
            selection = self.get_option_at_index(selection_index)
        except OptionDoesNotExist:
            return line

        # Figure out which component style is relevant for a checkbox on
        # this particular line.
        component_style = "selection-list--button"
        if selection.value in self._selected:
            component_style += "-selected"
        # if self.highlighted == selection_index:
        #     component_style += "-highlighted"
        if self._mouse_hovering_over == selection_index:
            component_style += "-hover"

        # # # Get the underlying style used for the prompt.
        # TODO: This is not a reliable way of getting the base style
        underlying_style = next(iter(line)).style or self.rich_style
        assert underlying_style is not None

        # Get the style for the button.
        button_style = self.get_component_rich_style(component_style)

        # Build the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style.from_color(button_style.bgcolor, underlying_style.bgcolor)

        # Add the option index to the style. This is used to determine which
        # option to select when the button is clicked or hovered.
        side_style += Style(meta={"option": selection_index})
        button_style += Style(meta={"option": selection_index})

        # At this point we should have everything we need to place a
        # "button" before the option.
        return Strip(
            [
                Segment(RadioButton.BUTTON_LEFT, style=side_style),
                Segment(RadioButton.BUTTON_INNER, style=button_style),
                Segment(RadioButton.BUTTON_RIGHT, style=side_style),
                Segment(" ", style=underlying_style),
                *line,
            ]
        )

class MultiSelect(Widget):
    ALLOW_SELECT = False

    def __init__(self, selection: RadioSelectionList, title=None):
        self.selection_list: RadioSelectionList = selection
        # self.collapsible: BetterCollapsible = BetterCollapsible()
        self.collapsible: Collapsible = Collapsible()
        self.collapsible.ALLOW_SELECT = False
        self.update()
        super().__init__()
        if title:
            self.border_title = title

    @override
    def compose(self) -> ComposeResult:
        with self.collapsible:
            yield self.selection_list

    @on(RadioSelectionList.SelectedChanged)
    def update(self):
        if len(self.selection_list.selected) == 0:
            self.collapsible.title = "None"
            return
        self.collapsible.title = ""
        for selected in self.selection_list.selected.copy():
            self.collapsible.title += selected + ", "
        self.collapsible.title = self.collapsible.title.removesuffix(", ")

    async def _on_click(self, event: events.Click) -> None:
        """Inform ancestor we want to toggle."""
        event.stop()
        if event.widget != self.selection_list:
            self.collapsible.collapsed = not self.collapsible.collapsed

