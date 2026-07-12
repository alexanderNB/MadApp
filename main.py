"""
An implementation of a classic calculator, with a layout inspired by macOS calculator.

Works like a real calculator. Click the buttons or press the equivalent keys.
"""

from ast import main
from decimal import Decimal
import json
import time

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.css.query import NoMatches
from textual.notifications import Notification
from textual.reactive import var
from textual.widgets import Button, Collapsible, Digits, Header, Label, ListItem, ListView, Placeholder, SelectionList, Static, Input, Select
from components import RadioSelectionList, Tag, Ingrediant, MultiSelect


class MadApp(App):
    """A working 'desktop' calculator."""
    CSS_PATH = "css.tcss"

    HORIZONTAL_BREAKPOINTS = [
        (0, "-narrow"),
        (40, "-normal"),
        (80, "-wide"),
        (120, "-very-wide"),
    ]

    BINDINGS = [
            ("d", "dish_view", "Dish View")
            ]

    @staticmethod
    def _dishes():
        with open("dishes.json", mode="r", encoding="utf-8") as dishes_file:
             return json.load(dishes_file)

    dishes = _dishes()
    active_dish = None
    

    def compose(self) -> ComposeResult:


        with Container(id="maincontainer"):
            with Container(id="frontpage"):
                yield Button("Tilføj opskrift", id="add")
                yield Button("Find", id="find")
                yield Button("Indkøbsliste", id="list")
                # yield Static()
                yield Button("Tilfældige", id="random")

                yield Button("Load", id="load")


    @on(Button.Pressed, "#back")
    def frontpage(self) -> None:
        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        frontpage = Container(id="frontpage")
        maincontainer.mount(frontpage)

        frontpage.mount_all([
            Button("Tilføj opskrift", id="add"),
            Button("Find", id="find"),
            Button("Indkøbsliste", id="list"),
            Button("Tilfældige", id="random"),
            Static(),
            Static(),
            Static(),
            Static(),
            Button("Load", id="load"),
            ])

    @on(Button.Pressed, "#find")
    def findpage(self) -> None:
        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        findpage = Container(id="findpage")
        maincontainer.mount(findpage)
        results_list = RadioSelectionList(id="findpage-results")


        findpage.mount_all([
            Input("", id="findpage-search"), 
            MultiSelect(RadioSelectionList(
                    ("Oksekød", "Oksekød"),
                    ("Kylling", "Kylling"),
                    ("Svinekød", "Svinekød"),
                    ("Fisk", "Fisk"),
                    ("Vegetar", "Vegetar"),
                    ("Andet", "Andet"),
                    ("Dessert", "Dessert"),
                    id="findpage-meat",
                ).toggle_all(),
                title="Kød"
            ),
            MultiSelect(RadioSelectionList(
                    ("Pasta", "Pasta"),
                    ("Ris", "Ris"),
                    ("Kartofler", "Kartofler"),
                    ("Brød", "Brød"),
                    ("Andet", "Andet"),
                    id="findpage-side"
                ).toggle_all(),
                title="Tilbehør"
            ),
            MultiSelect(RadioSelectionList(
                    ("Nem", "Nem"),
                    ("Medium", "Medium"),
                    ("Svær", "Svær"),
                    id="findpage-difficulty"
                ).toggle_all(),
                title="Sværhedsgrad"
            ),
            MultiSelect(RadioSelectionList(
                    ("Mor", "Mor"),
                    ("Alexander", "Alexander"),
                    id="findpage-profile"
                ).toggle_all(),
                title="Profil"
            ),
            MultiSelect(RadioSelectionList(
                ("Tags...", "Tags..."),
            ), title="Tags"),
            MultiSelect(RadioSelectionList(
                ("Ingredienser...", "Ingredienser..."),
            ), title="Ingredienser"),
            VerticalScroll(
                results_list,
                id="findpage-result-scroll"
            ),
            Button("Tilbage", id="back"),
        ])
        self.search()


    
    @on(Input.Changed, "#findpage-search")
    @on(RadioSelectionList.SelectedChanged, "#findpage-meat,#findpage-side,#findpage-difficulty,#findpage-profile")
    def search(self):
        search = self.query_one("#findpage-search")
        results_list = self.query_one("#findpage-results")
        chosen_meats = self.query_one("#findpage-meat")
        chosen_side = self.query_one("#findpage-side")
        chosen_difficulty = self.query_one("#findpage-difficulty")
        chosen_profile = self.query_one("#findpage-profile")

        results = [dish["Name"] for dish in self.dishes
                    if dish["Meat"] in [selection for selection in chosen_meats.selected]
                    if dish["Side"] in [selection for selection in chosen_side.selected]
                    if dish["Difficulty"] in [selection for selection in chosen_difficulty.selected]
                    if dish["Profile"] in [selection for selection in chosen_profile.selected]
                    and search.value.lower() in dish["Name"].lower()
                    ]

        results_list.clear_options()
        results_list.add_options([(results, i) for i, results in enumerate(results)])
        
    def _Select_with_label(self, select: Select, label: str):
        select.border_title = label
        return select

    @on(SelectionList.SelectedChanged, "#findpage-results")
    def action_dish_view(self, dish=None):
        results_list = self.query_one("#findpage-results")


        self.active_dish = [x for x in self.dishes if x["Name"] == results_list.get_option_at_index(results_list.selected[0]).prompt][0]


        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        dish_container = Container(id="dishcontainer")
        maincontainer.mount(dish_container)

        tag_container = VerticalScroll(
                *[Tag(tag) for tag in self.active_dish["Tags"]],
                Button("Add tag", id="dish-view-add-tag"),
                id="dish-view-tags",
            )
        tag_container.border_title = "Tags"
        ingrediant_container = VerticalScroll(
                *[Ingrediant(ingrediant["Name"], ingrediant["Unit"], ingrediant["Amount"]) for ingrediant in self.active_dish["Ingrediants"]],
                Button("Add Ingrediant", id="dish-view-add-ingrediant"),
                id="dish-view-ingrediants",
            )
        ingrediant_container.border_title = "Ingredienser"
        

        dish_container.mount_all([
            Input(self.active_dish["Name"], id="dish-view-title"),
            self._Select_with_label(
                Select[str]([
                    ("Oksekød", "Oksekød"),
                    ("Kylling", "Kylling"),
                    ("Svinekød", "Svinekød"),
                    ("Fisk", "Fisk"),
                    ("Vegetar", "Vegetar"),
                    ("Andet", "Andet"),
                    ("Dessert", "Dessert")], 
                    value=self.active_dish["Meat"],
                    allow_blank=False,
                    id="dish-view-meat"
                ), "Kød"),
            self._Select_with_label(
                Select[str]([
                    ("Pasta", "Pasta"),
                    ("Ris", "Ris"),
                    ("Kartofler", "Kartofler"),
                    ("Brød", "Brød"),
                    ("Andet", "Andet")],
                    value=self.active_dish["Side"],
                    allow_blank=False,
                    id="dish-view-side"
                ), "Tilbehør"),
            self._Select_with_label(
                Select[str]([
                    ("Nem", "Nem"),
                    ("Medium", "Medium"),
                    ("Svær", "Svær")],
                    value=self.active_dish["Difficulty"],
                    allow_blank=False,
                    id="dish-view-difficulty"
                ), "Sværhedsgrad"),
            self._Select_with_label(
                Select[str]([
                    ("Mor", "Mor"),
                    ("Alexander", "Alexander")],
                    value=self.active_dish["Profile"],
                    allow_blank=False,
                    id="dish-view-profile"
                ), "Profile"),
            tag_container,
            ingrediant_container,
            Button("Tilbage", id="back"),
        ])

    @on(Button.Pressed, "#dish-view-add-tag")
    def add_tag(self):
        tags_list: VerticalScroll = self.query_one("#dish-view-tags", VerticalScroll)
        tags_list.mount(Tag(), before=-1)

    @on(Button.Pressed, "#dish-view-add-ingrediant")
    def add_ingrediant(self):
        ingrediant_list: VerticalScroll = self.query_one("#dish-view-ingrediants", VerticalScroll)
        ingrediant_list.mount(Ingrediant(), before=-1)

    # TODO: Potentially make it a save button to trigger
    @on(Input.Changed, "#dish-view-title")
    @on(Select.Changed, "#dish-view-meat,#dish-view-side,#dish-view-difficulty,#dish-view-profile")
    def update_recipe(self):
        title: Input = self.query_one("#dish-view-title", Input)
        chosen_meat: Select[str] = self.query_one("#dish-view-meat", Select)
        chosen_side: Select[str] = self.query_one("#dish-view-side", Select)
        chosen_difficulty: Select[str] = self.query_one("#dish-view-difficulty", Select)
        chosen_profile: Select[str] = self.query_one("#dish-view-profile", Select)
        tag_list: VerticalScroll = self.query_one("#dish-view-tags", VerticalScroll)
        ingrediant_list: VerticalScroll = self.query_one("#dish-view-ingrediants", VerticalScroll)
        

        self.active_dish["Name"] = title.value
        self.active_dish["Meat"] = chosen_meat.value
        self.active_dish["Side"] = chosen_side.value
        self.active_dish["Difficulty"] = chosen_difficulty.value
        self.active_dish["Profile"] = chosen_profile.value
        self.active_dish["Tags"] = [tag.input.value for tag in tag_list.children if isinstance(tag, Tag)]
        self.active_dish["Ingrediants"] = [
                {
                    "Amount": ingrediant.amount_input.value,
                    "Name": ingrediant.input.value,
                    "Unit": ingrediant.unit_select.value
                } for ingrediant in ingrediant_list.children if isinstance(ingrediant, Ingrediant)]




if __name__ == "__main__":
    MadApp().run()



