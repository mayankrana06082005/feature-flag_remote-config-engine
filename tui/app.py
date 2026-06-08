from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane

from screens.flags_screen import FlagsScreen
from screens.configs_screen import ConfigsScreen

class FeatureFlagApp(App):
    """The master control dashboard for the Feature Flag Engine."""
    
    CSS_PATH = "app.tcss"
    TITLE = "Feature Flag & Config Manager"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Data"),
        # Modal to be added in Part B
        # ("n", "new_flag", "New Flag"),
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

if __name__ == "__main__":
    app = FeatureFlagApp()
    app.run()