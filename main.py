from ast import main
from decimal import Decimal
import json
import time
from typing import Any, Literal, ReadOnly

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.css.query import NoMatches
from textual.notifications import Notification
from textual.reactive import var
from textual.widgets import Button, Collapsible, Digits, Header, Label, ListItem, ListView, Placeholder, SelectionList, Static, Input, Select
from components import RadioSelectionList, Tag, Ingrediant, MultiSelect, DishElement, ShoppingListSection


class MadApp(App[Any]):
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

    @property
    def dishes(self) -> list[
                            dict[
                                Literal["Difficulty"] | Literal["Ingrediants"] | Literal["Meat"] | Literal["Name"] | Literal["Profile"] | Literal["Side"] | Literal["Tags"],
                                str | list[dict[Literal["Amount"] | Literal["Name"] | Literal["Unit"], str | int]] | list[str]
                            ]
                        ]:
        with open("dishes.json", mode="r", encoding="utf-8") as file:
            return json.load(file)

    def write_to_dishes(self, updated_dishes):
        with open("dishes.json", mode="w", encoding="utf-8") as file:
            json.dump(updated_dishes, file, indent=4, sort_keys=False, ensure_ascii=False)


    @property
    def sections(self) ->   list[
                                dict[
                                    Literal["Name"] | Literal["ingrediantList"] | Literal["ingrediantsWithUnits"],
                                    str | list[str] | dict[str, list[str]]
                                ]
                            ]:
        with open("sections.json", mode="r", encoding="utf-8") as file:
            return json.load(file)

    def write_to_sections(self, updated_sections):
        with open("sections.json", mode="w", encoding="utf-8") as file:
            json.dump(updated_sections, file, indent=4, sort_keys=False, ensure_ascii=False)


    @property
    def selections(self):
        with open("active_selections.json", mode="r", encoding="utf-8") as file:
            return json.load(file)[self.profile]

    def write_to_selections(self, updated_selections):
        with open("active_selections.json", mode="r", encoding="utf-8") as file:
            full_json = json.load(file)
        full_json[self.profile] = updated_selections
        with open("active_selections.json", mode="w", encoding="utf-8") as file:
            json.dump(full_json, file, indent=4, sort_keys=False, ensure_ascii=False)


    profile = "Alexander"
    active_dish_index = None

    def compose(self) -> ComposeResult:

        with Container(id="maincontainer"):
            with Container(id="frontpage"):
                yield Button("Tilføj opskrift", id="add")
                yield Button("Find", id="find")
                yield Button("Indkøbsliste", id="shopping-list")
                yield Button("Tilfældige", id="random")
                with VerticalScroll(id="frontpage-selected-dishes"):
                    for dish_index in self.selections["dishes"]:
                        yield DishElement(self.dishes[dish_index]["Name"], value=True, edit_function=lambda x=dish_index: (self.dish_view(dish_index=x)), selected_function=lambda value, x=dish_index: self.selected_dish(x, value))
                yield Button("Load", id="load")


    @on(Button.Pressed, "#back")
    def frontpage(self) -> None:
        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        frontpage = Container(id="frontpage")
        maincontainer.mount(frontpage)
        selected_dishes = VerticalScroll(id="frontpage-selected-dishes")
        selected_dishes.border_title = "Valgte opskrifter"

        frontpage.mount_all([
            Button("Tilføj opskrift", id="add"),
            Button("Find", id="find"),
            Button("Indkøbsliste", id="shopping-list"),
            Button("Tilfældige", id="random"),
            selected_dishes,
            Button("Load", id="load"),
            ])

        selected_dishes.mount_all([
            DishElement(self.dishes[dish_index]["Name"], value=True, edit_function=lambda x=dish_index: (self.dish_view(dish_index=x)), selected_function=lambda value, x=dish_index: self.selected_dish(x, value)) for dish_index in self.selections["dishes"]
            ])

    @on(Button.Pressed, "#find")
    def findpage(self) -> None:
        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        findpage = Container(id="findpage")
        maincontainer.mount(findpage)
        results_list = VerticalScroll(id="findpage-results")
        results_list.border_title = "Opskrifter"


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
                ),
                title="Kød"
            ),
            MultiSelect(RadioSelectionList(
                    ("Pasta", "Pasta"),
                    ("Ris", "Ris"),
                    ("Kartofler", "Kartofler"),
                    ("Brød", "Brød"),
                    ("Andet", "Andet"),
                    id="findpage-side"
                ),
                title="Tilbehør"
            ),
            MultiSelect(RadioSelectionList(
                    ("Nem", "Nem"),
                    ("Medium", "Medium"),
                    ("Svær", "Svær"),
                    id="findpage-difficulty"
                ),
                title="Sværhedsgrad"
            ),
            MultiSelect(RadioSelectionList(
                    ("Mor", "Mor"),
                    ("Alexander", "Alexander"),
                    id="findpage-profile"
                ),
                title="Profil"
            ),
            MultiSelect(RadioSelectionList(
                ("Tags...", "Tags..."),
            ), title="Tags"),
            MultiSelect(RadioSelectionList(
                ("Ingredienser...", "Ingredienser..."),
            ), title="Ingredienser"),
            results_list,
            Button("Tilbage", id="back"),
        ])
        self.search()


    
    @on(Input.Changed, "#findpage-search")
    @on(RadioSelectionList.SelectedChanged, "#findpage-meat,#findpage-side,#findpage-difficulty,#findpage-profile")
    def search(self):
        search: Input = self.query_one("#findpage-search", Input)
        results_list: VerticalScroll = self.query_one("#findpage-results", VerticalScroll)
        chosen_meats: RadioSelectionList = self.query_one("#findpage-meat", RadioSelectionList)
        chosen_side: RadioSelectionList = self.query_one("#findpage-side", RadioSelectionList)
        chosen_difficulty: RadioSelectionList = self.query_one("#findpage-difficulty", RadioSelectionList)
        chosen_profile: RadioSelectionList = self.query_one("#findpage-profile", RadioSelectionList)

        results = [dish for dish in self.dishes
                    if len(chosen_meats.selected) == 0 or dish["Meat"] in [selection for selection in chosen_meats.selected]
                    if len(chosen_side.selected) == 0 or dish["Side"] in [selection for selection in chosen_side.selected]
                    if len(chosen_difficulty.selected) == 0 or dish["Difficulty"] in [selection for selection in chosen_difficulty.selected]
                    if len(chosen_profile.selected) == 0 or dish["Profile"] in [selection for selection in chosen_profile.selected]
                    if search.value.lower() in dish["Name"].lower()
                    ]

        results_list.remove_children()
        results_list.mount_all([
            DishElement(result["Name"], value=i in self.selections["dishes"], edit_function=lambda x=i: (self.dish_view(dish_index=x)), selected_function=lambda value, x=i: self.selected_dish(x, value) ) for i, result in enumerate(results)
            ])
        
    def _Select_with_label(self, select: Select[str], label: str):
        select.border_title = label
        return select

    def selected_dish(self, dish_index, value):
        selections = self.selections
        if dish_index in selections["dishes"]:
            selections["dishes"].remove(dish_index)
        if value:
            selections["dishes"].append(dish_index)
        self.write_to_selections(selections)

    def dish_view(self, dish_index):
        self.active_dish_index = dish_index
        dish = self.dishes[dish_index]
        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        dish_container = Container(id="dishcontainer")
        maincontainer.mount(dish_container)

        tag_container = VerticalScroll(
                *[Tag(tag) for tag in dish["Tags"]],
                Button("Add tag", id="dish-view-add-tag"),
                id="dish-view-tags",
            )
        tag_container.border_title = "Tags"
        ingrediant_container = VerticalScroll(
                *[Ingrediant(ingrediant["Name"], ingrediant["Unit"], ingrediant["Amount"]) for ingrediant in dish["Ingrediants"]],
                Button("Add Ingrediant", id="dish-view-add-ingrediant"),
                id="dish-view-ingrediants",
            )
        ingrediant_container.border_title = "Ingredienser"
        

        dish_container.mount_all([
            Input(dish["Name"], id="dish-view-title"),
            self._Select_with_label(
                Select[str]([
                    ("Oksekød", "Oksekød"),
                    ("Kylling", "Kylling"),
                    ("Svinekød", "Svinekød"),
                    ("Fisk", "Fisk"),
                    ("Vegetar", "Vegetar"),
                    ("Andet", "Andet"),
                    ("Dessert", "Dessert")], 
                    value=dish["Meat"],
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
                    value=dish["Side"],
                    allow_blank=False,
                    id="dish-view-side"
                ), "Tilbehør"),
            self._Select_with_label(
                Select[str]([
                    ("Nem", "Nem"),
                    ("Medium", "Medium"),
                    ("Svær", "Svær")],
                    value=dish["Difficulty"],
                    allow_blank=False,
                    id="dish-view-difficulty"
                ), "Sværhedsgrad"),
            self._Select_with_label(
                Select[str]([
                    ("Mor", "Mor"),
                    ("Alexander", "Alexander")],
                    value=dish["Profile"],
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
        
        dish = self.dishes[self.active_dish_index].copy()
        dish["Name"] = title.value
        dish["Meat"] = chosen_meat.value
        dish["Side"] = chosen_side.value
        dish["Difficulty"] = chosen_difficulty.value
        dish["Profile"] = chosen_profile.value
        dish["Tags"] = [tag.input.value for tag in tag_list.children if isinstance(tag, Tag)]
        dish["Ingrediants"] = [
                {
                    "Amount": int(ingrediant.amount_input.value),
                    "Name": ingrediant.input.value,
                    "Unit": ingrediant.unit_select.value
                } for ingrediant in ingrediant_list.children if isinstance(ingrediant, Ingrediant)]

        updated_dishes = self.dishes.copy()
        updated_dishes[self.active_dish_index] = dish.copy()
        self.write_to_dishes(updated_dishes)

    @on(Button.Pressed, "#shopping-list")
    def shopping_list(self):
        maincontainer = self.query_one("#maincontainer")
        maincontainer.remove_children()

        shopping_container = Container(id="shoppingcontainer")
        maincontainer.mount(shopping_container)
        
        ingrediants = {}
        for dish_index in self.selections["dishes"]:
            dish = self.dishes[dish_index]
            for ingrediant in dish["Ingrediants"]:
                if ingrediant["Name"] not in ingrediants:
                    ingrediants[ingrediant["Name"].lower()] = {}
                if ingrediant["Unit"] not in ingrediants[ingrediant["Name"].lower()]:
                    ingrediants[ingrediant["Name"].lower()][ingrediant["Unit"]] = 0
                ingrediants[ingrediant["Name"].lower()][ingrediant["Unit"]] += ingrediant["Amount"]

        sorted_ingrediants = {section["Name"]: {} for section in self.sections}
        sorted_ingrediants["Andet"] = {}
        for ingrediant in ingrediants:
            ingrediant: str # Just the name of the ingrediant
            in_section = False
            for section in self.sections:
                if ingrediant not in section["ingrediantList"]:
                    continue

                ingrediant_already_sorted: bool = ingrediant in sorted_ingrediants[section["Name"]]
                if ingrediant_already_sorted:
                    in_section = True
                    break

                if ingrediant in section["ingrediantsWithUnits"].keys():
                    sorted_ingrediants[section["Name"]][ingrediant] = {}

                    for unit in ingrediants[ingrediant]: # Loops through each unit, only adding the units specified in section["ingrediantsWithUnits"]
                        unit: str # Just the name of the unit
                        unit_in_section: bool = unit in section["ingrediantsWithUnits"][ingrediant]
                        if unit_in_section:
                            amount: int = ingrediants[ingrediant][unit]
                            sorted_ingrediants[section["Name"]][ingrediant][unit] = amount

                    # If none of the units for the section was present the ingrediant is removed from the section
                    if len(sorted_ingrediants[section["Name"]][ingrediant]) == 0: 
                        sorted_ingrediants[section["Name"]].pop(ingrediant)

                    in_section = True # NOTE: this assumes that all units for the given ingrediant have been defined in a section
                    continue

                # If the unit is not specified in 'section["ingrediantsWithUnits"]' the ingrediant for the section gets the entire {<unit: amount>} dict
                sorted_ingrediants[section["Name"]][ingrediant] = ingrediants[ingrediant]

                in_section = True
                break

            if not in_section:
                sorted_ingrediants["Andet"][ingrediant] = ingrediants[ingrediant]


        list_container = VerticalScroll(
            *[ShoppingListSection(
                ingrediants=RadioSelectionList(
                    *[(f"{ingrediant.title()}: {self._unpack_str_list([f"{ingrediants[ingrediant][unit]} {unit}" for unit in sorted_ingrediants[ingrediant_section][ingrediant]], " + ")}", f"{ingrediant}: {self._unpack_str_list([f"{ingrediants[ingrediant][unit]} {unit}" for unit in sorted_ingrediants[ingrediant_section][ingrediant]], " + ")}") for ingrediant in sorted_ingrediants[ingrediant_section]] 
                ),
                label=ingrediant_section
            ) for ingrediant_section in sorted_ingrediants]
        )

        shopping_container.mount(list_container)

        shopping_container.mount(Button("Tilbage", id="back"))

    def _unpack_str_list(self, list, separator=""):
        result = ""
        for element in list:
            result += element + separator
        return result.removesuffix(separator)


if __name__ == "__main__":
    MadApp().run()
