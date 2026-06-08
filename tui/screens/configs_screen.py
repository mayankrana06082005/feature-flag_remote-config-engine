from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.containers import Vertical
from textual import work

from api_client import api

# Changed from Screen to Vertical container
class ConfigsScreen(Vertical):

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
