from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.screen import Screen
from textual import work

from api_client import api

class ConfigsScreen(Screen):
    # Edit modal to be added in Part B
    # BINDINGS = [("enter", "edit_config", "Edit Value")]

    def compose(self) -> ComposeResult:
        yield DataTable(id="configs_table", cursor_type="row")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Value", "Type", "Description")
        self.load_data()

    @work(exclusive=True)
    async def load_data(self) -> None:
        configs = await api.list_configs()
        table = self.query_one(DataTable)
        table.clear()
        
        for config in configs:
            table.add_row(
                config["id"], 
                str(config["value"]), 
                config["value_type"], 
                config["description"],
                key=config["id"]
            )