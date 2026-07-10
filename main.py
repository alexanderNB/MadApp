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
from textual.reactive import var
from textual.widgets import Button, Digits, Header, Placeholder, SelectionList, Static, Input, Select


class MadApp(App):
    """A working 'desktop' calculator."""
    CSS_PATH = "css.tcss"

    def compose(self) -> ComposeResult:
        with Container(id="maincontainer"):
            with Container(id="frontpage"):
                yield Button("Tilføj opskrift", id="add")
                yield Button("Find", id="find")
                yield Button("Indkøbsliste", id="list")
                yield Button("Tilfældige", id="random")
                yield Static()
                yield Static()
                yield Static()
                yield Static()
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

        search = "Kylling"
        chosen_meats = ["Oksekød", "Kylling", "Svinekød"]
        chosen_side = ["Kartofler", "Ris", "Pasta"]
        chosen_difficulty = ["Nem", "Medium", "Svær"]
        chosen_profile = ["Mor"]

        with open("dishes.json", mode="r", encoding="utf-8") as dishes_file:
             dishes = json.load(dishes_file)
        results = [dish["Name"] for dish in dishes 
                    if dish["Meat"] in chosen_meats 
                    and dish["Side"] in chosen_side 
                    and dish["Difficulty"] in chosen_difficulty 
                    and dish["Profile"] in chosen_profile
                    and search.lower() in dish["Name"].lower()
                    ]
        results_list = SelectionList[int]()
        
        results_list.add_options([(results, i) for i, results in enumerate(results)])


        findpage.mount_all([
            Input("", id="search"), 
            SelectionList[int](
                ("Oksekød", 0),
                ("Kylling", 1),
                ("Svinekød", 2),
                ("Fisk", 3),
                ("Vegetar", 4),
                ("Andet", 5),
                ("Dessert", 6)
            ),
            SelectionList[int](
                ("Pasta", 0),
                ("Ris", 1),
                ("Kartofler", 2),
                ("Brød", 3),
                ("Andet", 4),
            ),
            SelectionList[int](
                ("Nem", 0),
                ("Medium", 1),
                ("Svær", 2),
            ),
            SelectionList[int](
                ("Mor", 0),
                ("Alexander", 1),
            ),
            SelectionList[int](
                ("Tags...", 0),
            ),
            SelectionList[int](
                ("Ingredienser...", 0),
            ),
            VerticalScroll(
                results_list,
                id="results"
            ),
            Button("Tilbage", id="back"),
        ])



if __name__ == "__main__":
    mad_app = MadApp()
    mad_app.run()

