from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.containers import Vertical
from textual import work
from rich.text import Text

from api_client import api

import json
from typing import Any, Dict
from textual.screen import ModalScreen
from textual.containers import Horizontal
from textual.widgets import Label, Button, TextArea
#from textual.app import ComposeResult

class EditFlagModal(ModalScreen[Dict[str, Any]]):
    """A floating modal to edit a flag's targeting rule via JSON."""

    CSS = """
    EditFlagModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #edit-dialog {
        width: 60;
        height: 20;
        padding: 1 2;
        background: $panel;
        border: thick $primary;
    }
    #dialog-buttons {
        height: 3;
        margin-top: 1;
        align: right middle;
    }
    Button { margin-left: 1; }
    """

    def __init__(self, flag_data: dict) -> None:
        super().__init__()
        self.flag_data = flag_data

    def compose(self) -> ComposeResult:
        with Vertical(id="edit-dialog"):
            yield Label(f"Editing Rule: [bold cyan]{self.flag_data.get('id')}[/]", classes="title")
            
            # Extract current rule and format with 2-space indentation
            current_rule = self.flag_data.get("targeting_rule") or {}
            rule_str = json.dumps(current_rule, indent=2)
            
            # TextArea natively supports language modes
            yield TextArea(rule_str, language="json", id="rule-input")
            
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", variant="error", id="cancel-btn")
                yield Button("Save", variant="success", id="save-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
            
        elif event.button.id == "save-btn":
            text_area = self.query_one("#rule-input", TextArea)
            try:
                # Validate JSON strictly before passing it back
                new_rule = json.loads(text_area.text)
                self.dismiss({"targeting_rule": new_rule})
            except json.JSONDecodeError as e:
                self.app.notify(f"Invalid JSON: {e}", title="Syntax Error", severity="error", timeout=5)

# Changed from Screen to Vertical container so it renders inside Tabs!
class FlagsScreen(Vertical):
    BINDINGS = [
        ("space", "toggle_selected", "Toggle Flag"),
        ("e", "edit_flag", "Edit Rule"),
        ("d", "delete_flag", "Delete Flag"),
    ]

    def compose(self) -> ComposeResult:
        yield DataTable(id="flags_table", cursor_type="row")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Status", "Targeting", "Updated At")
        self.load_data()

    @work(exclusive=True)
    async def load_data(self) -> None:
        """Fetches flags from the API and populates the table."""
        try:
            flags = await api.list_flags()
            table = self.query_one(DataTable)
            table.clear()
            
            for flag in flags:
                is_enabled = bool(flag.get("enabled", False))
                status = Text("[ON]", style="bold #00ff00") if is_enabled else Text("[OFF]", style="bold #ff0000")
                
                rule = flag.get("targeting_rule") or {}
                rule_type = str(rule.get("type", "unknown")).capitalize()
                rule_text = Text(f"({rule_type})", style="italic #aaaaaa")
                
                updated_at = str(flag.get("updated_at", "Unknown Date"))
                if "T" in updated_at:
                    updated_at = updated_at.split(".")[0].replace("T", " ")
                
                table.add_row(
                    str(flag.get("id", "missing_id")), 
                    str(flag.get("name", "missing_name")), 
                    status, 
                    rule_text, 
                    updated_at,
                    key=str(flag.get("id"))
                )
        except Exception as e:
            self.app.notify(f"Could not load flags: {e}", title="API Error", severity="error", timeout=10)

    async def action_toggle_selected(self) -> None:
        """Fired when the user presses Space."""
        table = self.query_one(DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            flag_id = row_key.row_key.value
            
            flags = await api.list_flags()
            current_flag = next((f for f in flags if f["id"] == flag_id), None)
            
            if current_flag:
                await api.toggle_flag(flag_id, current_flag["enabled"])
                self.load_data()
        except Exception:
            pass

    async def action_delete_flag(self) -> None:
        """Fired when the user presses 'd'."""
        table = self.query_one(DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            flag_id = row_key.row_key.value
            await api.delete_flag(flag_id)
            self.load_data()
        except Exception:
            pass

    @work
    async def action_edit_flag(self) -> None:
        """Triggered when the user highlights a row and presses 'e'."""
        table = self.query_one(DataTable)
        try:
            # 1. Identify the highlighted flag ID
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            flag_id = str(row_key.row_key.value)
            
            # 2. Fetch current state to populate the editor
            flags = await api.list_flags()
            current_flag = next((f for f in flags if f.get("id") == flag_id), None)
            
            if current_flag:
                # 3. Suspend execution and await the modal's return payload
                flag_update = await self.app.push_screen_wait(EditFlagModal(current_flag))
                
                # 4. If the user hit 'Save' with valid JSON, push to FastAPI
                if flag_update:
                    await api.update_flag(flag_id, flag_update)
                    self.app.notify(f"Updated rule for {flag_id}", title="Success", severity="information")
                    self.load_data() # Force a UI repaint to reflect changes
                    
        except Exception as e:
             self.app.notify(f"Failed to edit: {str(e)}", title="Editor Error", severity="warning")