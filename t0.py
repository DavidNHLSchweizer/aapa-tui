from rich.syntax import Syntax
from rich.table import Table

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import RichLog, Button

class Terminal(RichLog):
    def compose(self)->ComposeResult:
        yield RichLog(highlight=True, markup=True)
        yield Button('OK')
 
    def on_key(self, event: events.Key) -> None:
        """Write Key events to log."""
        text_log = self.query_one(RichLog)
        text_log.write(event)
    @property
    def terminal(self)->RichLog:
        return self.query_one(RichLog)


class RichLogApp(App):
    CSS_PATH = ['terminal.tcss']
    def compose(self) -> ComposeResult:
        yield Terminal()
    def on_ready(self) -> None:
        """Called  when the DOM is ready."""
        terminal = self.query_one(Terminal).terminal
        terminal.write('HALLO WERELD')

        # rows = iter(csv.reader(io.StringIO(CSV)))
        # table = Table(*next(rows))
        # for row in rows:
        #     table.add_row(*row)

        # text_log.write(table)
        # text_log.write("[bold magenta]Write text or any Rich renderable!")



if __name__ == "__main__":
    app = RichLogApp()
    app.run()