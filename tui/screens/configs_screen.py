from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.containers import Vertical
from textual import work ,on

from api_client import api
from screens.modals import EditConfigModal

# Changed from Screen to Vertical container
class ConfigsScreen(Vertical):

    # BINDINGS = [
    #     ("enter", "edit_config", "Edit Value"),
    # ]

    def compose(self) -> ComposeResult:
        yield DataTable(id="configs_table", cursor_type="row")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Value", "Type", "Description")
        self.load_data()

    @work(exclusive=True)
    async def load_data(self) -> None:
        try:
            configs = await api.list_configs()
            table = self.query_one(DataTable)
            table.clear()
            
            for config in configs:
                table.add_row(
                    str(config.get("id", "missing_id")), 
                    str(config.get("value", "missing_value")), 
                    str(config.get("value_type", "missing_type")), 
                    str(config.get("description", "missing_desc")),
                    key=str(config.get("id"))
                )
        except Exception as e:
            self.app.notify(f"Could not load configs: {e}", title="API Error", severity="error", timeout=10)

    # async def action_edit_config(self) -> None:
    #     """Fired when the user presses 'enter'."""
    #     table = self.query_one(DataTable)
        
    #     try:
    #         # 1. Get the current cursor location
    #         coordinate = table.cursor_coordinate
            
    #         # Prevent crashes if the table is completely empty
    #         if coordinate.row < 0:
    #             return

    #         # 2. Extract the ID and the current Value from the highlighted row
    #         row_key = table.coordinate_to_cell_key(coordinate).row_key.value
    #         row_data = table.get_row(row_key)
    #         current_value = row_data[1]
    #         # 3. Define the callback for when the user clicks 'Save' in the popup
    #         async def update_config_callback(config_update: dict | None):
    #             if config_update:
    #                 try:
    #                     # Send the update to the backend
    #                     await api.update_config(row_key, config_update)
                        
    #                     # Refresh the table with the new data
    #                     self.load_data()
                        
    #                     # Show a success toast
    #                     self.app.notify(f"Config '{row_key}' updated!", severity="information")
    #                 except Exception as e:
    #                     self.app.notify(f"Error updating config: {e}", severity="error")

    #         # 4. Display the modal, pre-filled with the current data
    #         self.app.push_screen(
    #             EditConfigModal(config_id=row_key, current_value=str(current_value)), 
    #             update_config_callback
    #         )
            
    #     except Exception as e:
    #         self.app.notify(f"Action failed: {e}", severity="warning")

    @on(DataTable.RowSelected)
    async def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Fired automatically when the user presses Enter on a DataTable row."""
        try:
            # 1. Textual's event hands us the exact ID of the row automatically!
            row_key = event.row_key.value
            
            # 2. Extract the current value
            table = self.query_one(DataTable)
            row_data = table.get_row(row_key)
            current_value = row_data[1] 

            # 3. Define the callback for when the user clicks 'Save'
            async def update_config_callback(config_update: dict | None):
                if config_update:
                    try:
                        # Send the update to the backend
                        await api.update_config(row_key, config_update)
                        
                        # Refresh the table with the new data
                        self.load_data()
                        
                        self.app.notify(f"Config '{row_key}' updated!", severity="information")
                    except Exception as e:
                        self.app.notify(f"Error updating config: {e}", severity="error")

            # 4. Display the modal, pre-filled with the current data
            self.app.push_screen(
                EditConfigModal(config_id=row_key, current_value=str(current_value)), 
                update_config_callback
            )
            
        except Exception as e:
            self.app.notify(f"Action failed: {e}", severity="warning")