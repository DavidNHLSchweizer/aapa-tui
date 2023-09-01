from datetime import datetime
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Checkbox
from textual.containers import Horizontal, Vertical
from labeled_input import LabeledInput
from required import Required
from terminal import TerminalScreen, TerminalWrite
import logging
import tkinter.filedialog as tkifd

global_terminal: TerminalScreen = None
def testscript(**kwdargs)->bool:
    for i in range(1,648000):
        if i % 300 == 0:
            global_terminal.post_message(TerminalWrite(f'dit is {i}'))            
            logging.debug(f'dit is {i}')
    return False

class AapaConfiguration(Static):
    def compose(self)->ComposeResult:
        with Vertical():
            # yield AapaConfBigLabel('AAPA Configuratie')
            with Horizontal():
                yield LabeledInput('Root directory', width = '100', id='root', validators=Required())
                yield Button('...', id='edit_root', classes='small')
            with Horizontal():
                yield LabeledInput('Forms directory', width = '100', id='forms', validators=Required())
                yield Button('...', id='edit_forms', classes='small')
            with Horizontal():
                yield LabeledInput('Database', width = '100', id='database', validators=Required())
                yield Button('...', id='edit_database', classes='small')
    def on_mount(self):
        self.border_title = 'AAPA Configuratie'
    def _select_directory(self, input_id: str, title: str):
        input = self.query_one(f'#{input_id}', LabeledInput).input
        if (result := tkifd.askdirectory(mustexist=True, title=title, initialdir=input.value)):
            input.value=result
            input.cursor_position = len(result)
            input.focus()
    def _select_file(self, input_id: str, title: str, default_file: str, default_extension: str):
        input = self.query_one(f'#{input_id}', LabeledInput).input
        if (result := tkifd.askopenfilename(initialfile=input.value, title=title, 
                                            filetypes=[(default_file, f'*{default_extension}'),('all files', '*')], defaultextension=default_extension)):
            input.value=result
            input.cursor_position = len(result)
            input.focus()
    def on_button_pressed(self, message: Button.Pressed):
        match message.button.id:
            case 'edit_root': self._select_directory('root', 'Select root directory')
            case 'edit_forms': self._select_directory('forms', 'Select forms directory')
            case 'edit_database': self._select_file('database','Select databasefile', 'database files', '.db')
        message.stop()

class AapaButtons(Static):
    def compose(self)->ComposeResult:
        with Horizontal():
            yield Button('Scan', variant= 'primary', id='scan')
            yield Button('Mail', variant ='primary', id='mail') 
            yield Checkbox('Preview', value=True, id='preview')
            # yield Button('Cancel', variant = 'error', id='cancel') #niet werkend gekregen

class AapaApp(App):
    BINDINGS = [('r', 'run_terminal', 'Run de terminal')]
    CSS_PATH = ['terminal.tcss', 'aapa.tcss']
    def __init__(self, **kwdargs):
        self.terminal_active = False
        super().__init__(**kwdargs)
    def compose(self) -> ComposeResult:
        yield Header()
        yield AapaConfiguration()
        yield AapaButtons()
        yield Footer()
    @property
    def terminal(self)->TerminalScreen:
        if not hasattr(self, '_terminal'):
            self._terminal = self.get_screen('terminal')
            global global_terminal 
            global_terminal = self._terminal
        return self._terminal
    def on_mount(self):
        self.install_screen(TerminalScreen(), name='terminal')
    def callback_run_terminal(self, result: bool):
        logging.debug(f'callbacky {result}')
        self.terminal_active = False
    async def action_run_terminal(self):
        logging.debug(f'run terminal {self.terminal_active}')
        if self.terminal_active:
            return
        await self.app.push_screen('terminal', self.callback_run_terminal)
        self.terminal_active = True
        self.terminal.clear()
        self.terminal.write(f'HALLO WERELD {datetime.strftime(datetime.now(), "%d-%m-%Y, %H:%M:%S")}')
        self.terminal.run(testscript, aap=3, noot=42)        
    def on_key(self, event: events.Key) -> None:
        """Write Key events to log."""
        if self.terminal_active:
            self.terminal.write('\n'+ str(event))



if __name__ == "__main__":
    logging.basicConfig(filename='terminal.log', filemode='w', format='%(module)s-%(funcName)s-%(lineno)d: %(message)s', level=logging.DEBUG)
    app = AapaApp()
    app.run()