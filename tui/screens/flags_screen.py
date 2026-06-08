from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.screen import Screen
from textual import work
from rich.text import Text

from api_client import api

class FlagsScreen(Screen):
    BINDINGS = [
        ("space", "toggle_selected", "Toggle Flag"),
        ("d", "delete_flag", "Delete Flag"),
        # Modals to be implemented in Part B:
        # ("enter", "edit_rule", "Edit Rule"), 
    ]

    def compose(self) -> ComposeResult:
        yield DataTable(id="flags_table", cursor_type="row")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Status", "Targeting", "Updated At")
        self.load_data()

    # @work(exclusive=True)
    # async def load_data(self) -> None:
    #     """Fetches flags from the API and populates the table."""
    #     try:
    #         flags = await api.list_flags()
    #         table = self.query_one(DataTable)
    #         table.clear()
            
    #         for flag in flags:
    #             status = Text("[ON]", style="bold #00ff00") if flag["enabled"] else Text("[OFF]", style="bold #ff0000")
    #             rule_type = flag.get("targeting_rule", {}).get("type", "unknown").capitalize()
    #             rule_text = Text(f"({rule_type})", style="italic #aaaaaa")
                
    #             table.add_row(
    #                 flag["id"], 
    #                 flag["name"], 
    #                 status, 
    #                 rule_text, 
    #                 flag["updated_at"][:16].replace("T", " "), # Format date nicely
    #                 key=flag["id"]
    #             )
    #     except Exception as e:
    #         # This will pop up a red error message in the bottom right of the terminal!
    #         self.app.notify(f"Could not load flags: {e}", title="API Error", severity="error")

    @work(exclusive=True)
    async def load_data(self) -> None:
        """Fetches flags from the API and populates the table."""
        try:
            flags = await api.list_flags()
            table = self.query_one(DataTable)
            table.clear()
            
            for flag in flags:
                # 1. Safely handle enabled boolean
                is_enabled = bool(flag.get("enabled", False))
                status = Text("[ON]", style="bold #00ff00") if is_enabled else Text("[OFF]", style="bold #ff0000")
                
                # 2. Safely handle nested targeting rules
                rule = flag.get("targeting_rule") or {} # In case it is None
                rule_type = str(rule.get("type", "unknown")).capitalize()
                rule_text = Text(f"({rule_type})", style="italic #aaaaaa")
                
                # 3. Safely handle dates (The likely culprit)
                updated_at = str(flag.get("updated_at", "Unknown Date"))
                if "T" in updated_at:
                    updated_at = updated_at.split(".")[0].replace("T", " ") # Gets '2026-06-08 11:35:34' safely
                
                # Ensure all primitive values are strings before giving to Textual
                table.add_row(
                    str(flag.get("id", "missing_id")), 
                    str(flag.get("name", "missing_name")), 
                    status, 
                    rule_text, 
                    updated_at,
                    key=str(flag.get("id"))
                )
        except Exception as e:
            # THIS IS CRITICAL: If the above fails, you will see it as a red error popup now!
            self.app.notify(f"Table rendering failed: {str(e)}", title="Crash", severity="error", timeout=10)

    async def action_toggle_selected(self) -> None:
        """Fired when the user presses Space."""
        table = self.query_one(DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            flag_id = row_key.row_key.value
            
            # Find the current status by hitting the API (could also read from table)
            flags = await api.list_flags()
            current_flag = next((f for f in flags if f["id"] == flag_id), None)
            
            if current_flag:
                await api.toggle_flag(flag_id, current_flag["enabled"])
                self.load_data() # Refresh table
        except Exception:
            pass # Handle gracefully if table is empty

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