
from textual.containers import Horizontal
from textual import events
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import RichLog, Button, Log, Static, Header, Footer, Placeholder

# class Terminal(Static):
#     def compose(self)->ComposeResult:
#         yield Log()
 
#     def on_key(self, event: events.Key) -> None:
#         """Write Key events to log."""
#         self.terminal.write('\n'+ str(event))

class TerminalButtons(Static):
    def compose(self)->ComposeResult:
        with Horizontal():
            yield Button('Save Log', variant= 'primary', id='save_log')
            yield Button('Close', variant ='error', id='close') 

class TerminalForm(Static):
    def compose(self)->ComposeResult:
        yield Log()
        yield TerminalButtons()
    @property
    def terminal(self)->Log:
        return self.query_one(Log)



class TerminalScreen(Screen):
    def compose(self) -> ComposeResult:
        yield TerminalForm()
    @property
    def terminal(self)->Log:
        return self.query_one(TerminalForm).terminal
    
class RichLogApp(App):
    CSS_PATH = ['terminal.tcss']
    def compose(self) -> ComposeResult:
        yield Header()
        yield Placeholder('giel debiel')
        yield Footer()

    async def on_mount(self):
        self.install_screen(TerminalScreen(), name='terminal')
        await self.app.push_screen('terminal')
        """Called  when the DOM is ready."""
        terminal = self.query_one(TerminalScreen).terminal
        terminal.write('HALLO WERELD')

    def on_key(self, event: events.Key) -> None:
        """Write Key events to log."""
        terminal = self.query_one(TerminalScreen).terminal
        terminal.write('\n'+ str(event))
        # terminal.refresh()
        # rows = iter(csv.reader(io.StringIO(CSV)))
        # table = Table(*next(rows))
        # for row in rows:
        #     table.add_row(*row)

        # text_log.write(table)
        # text_log.write("[bold magenta]Write text or any Rich renderable!")



if __name__ == "__main__":
    app = RichLogApp()
    app.run()