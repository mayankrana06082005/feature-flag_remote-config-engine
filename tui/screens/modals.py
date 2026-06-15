# tui/screens/modals.py
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, Select
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult

class NewFlagModal(ModalScreen[dict | None]):
    """Modal to create a new Feature Flag."""
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-dialog"):
            yield Label("Create New Feature Flag", classes="modal-title")
            yield Input(placeholder="Flag ID (e.g., my_new_flag)", id="flag_id")
            yield Input(placeholder="Name (e.g., My New Flag)", id="flag_name")
            yield Input(placeholder="Description", id="flag_desc")
            yield Select(
                [("Everyone", "everyone"), ("Group", "group"), ("Percentage", "percentage")],
                prompt="Targeting Type",
                value="everyone",
                id="flag_type"
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Create", variant="success", id="create")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "create":
            raw_type = self.query_one("#flag_type", Select).value
            
            safe_type = raw_type if isinstance(raw_type, str) else "everyone"
            
            data = {
                "id": self.query_one("#flag_id", Input).value,
                "name": self.query_one("#flag_name", Input).value,
                "description": self.query_one("#flag_desc", Input).value,
                "enabled": False,
                "targeting_rule": {"type": self.query_one("#flag_type", Select).value or "everyone"}
            }
            self.dismiss(data)


class EditConfigModal(ModalScreen[dict | None]):
    """Modal to edit a config value."""
    def __init__(self, config_id: str, current_value: str, name: str | None = None, id: str | None = None, classes: str | None = None):
        super().__init__(name, id, classes)
        self.config_id = config_id
        self.current_value = current_value

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-dialog"):
            yield Label(f"Edit Config: {self.config_id}", classes="modal-title")
            yield Input(value=self.current_value, id="config_value")
            with Horizontal(classes="modal-buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Save", variant="success", id="save")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            new_value = self.query_one("#config_value", Input).value
            self.dismiss({"value": new_value})

class NewConfigModal(ModalScreen[dict | None]):
    """Modal to create a new Configuration."""
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-dialog"):
            yield Label("Create New Configuration", classes="modal-title")
            yield Input(placeholder="Config ID (e.g., max_retries)", id="config_id")
            yield Input(placeholder="Description", id="config_desc")
            yield Input(placeholder="Value (e.g., 5, true, some_string)", id="config_value")
            
            # Select dropdown for the valid config types in your database
            yield Select(
                [("String", "string"), ("Integer", "integer"), ("Float", "float"), ("Boolean", "boolean")],
                prompt="Value Type", 
                value="string",
                id="config_type"
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Create", variant="success", id="create")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "create":
            # Extract the raw value safely to avoid JSON errors
            raw_type = self.query_one("#config_type", Select).value
            safe_type = raw_type if isinstance(raw_type, str) else "string"
            
            data = {
                "id": self.query_one("#config_id", Input).value,
                "description": self.query_one("#config_desc", Input).value,
                "value": self.query_one("#config_value", Input).value,
                "value_type": safe_type
            }
            self.dismiss(data)