from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane

from screens.flags_screen import FlagsScreen
from screens.configs_screen import ConfigsScreen

from screens.modals import NewFlagModal 
from api_client import api

from screens.modals import NewFlagModal, NewConfigModal

class FeatureFlagApp(App):
    """The master control dashboard for the Feature Flag Engine."""
    
    CSS_PATH = "app.tcss"
    TITLE = "Feature Flag & Config Manager"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Data"),
        # Modal to be added in Part B
        ("n", "new_flag", "New Flag"),
        ("c", "new_config", "New Config"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="flags"):
            with TabPane("Flags", id="flags"):
                yield FlagsScreen()
            with TabPane("Configs", id="configs"):
                yield ConfigsScreen()
        yield Footer()

    def action_refresh(self) -> None:
        """Fired when the user presses 'r'."""
        self.query_one(FlagsScreen).load_data()
        self.query_one(ConfigsScreen).load_data()

    async def action_new_flag(self) -> None:
        """Fired when the user presses 'n'."""
        
        # 1. Define what happens AFTER the modal closes
        async def create_flag_callback(flag_data: dict | None):
            # If flag_data is None, the user pressed "Cancel"
            if flag_data:
                try:
                    # Send the data to your FastAPI backend
                    await api.create_flag(flag_data)
                    
                    # Refresh the tables so the new flag shows up immediately
                    self.action_refresh()
                    
                    # Show a success toast in the corner
                    self.notify("Flag created successfully!", severity="information")
                except Exception as e:
                    # Show an error toast if the API call fails
                    self.notify(f"Error creating flag: {e}", severity="error")

        # 2. Tell Textual to display the modal and attach the callback
        self.push_screen(NewFlagModal(), create_flag_callback)

    async def action_new_config(self) -> None:
        """Fired when the user presses 'c'."""
        
        async def create_config_callback(config_data: dict | None):
            if config_data:
                try:
                    # Send the data to your configs API endpoint
                    await api.create_config(config_data)
                    
                    # Refresh the tables so the new config shows up immediately
                    self.action_refresh()
                    
                    # Show a success toast in the corner
                    self.notify("Config created successfully!", severity="information")
                except Exception as e:
                    self.notify(f"Error creating config: {e}", severity="error")

        # Tell Textual to display the modal and attach the callback
        self.push_screen(NewConfigModal(), create_config_callback)

if __name__ == "__main__":
    app = FeatureFlagApp()
    app.run()