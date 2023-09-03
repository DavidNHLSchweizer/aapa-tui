from dataclasses import dataclass
from datetime import datetime
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, Button, RadioSet, RadioButton
from textual.containers import Horizontal, Vertical
from labeled_input import LabeledInput
from required import Required
from terminal import TerminalScreen, TerminalWrite
import logging
import tkinter.filedialog as tkifd

global_terminal: TerminalScreen = None
def testscript(**kwdargs)->bool:
    global_terminal.post_message(TerminalWrite(f'params {kwdargs}'))   
    for i in range(1,kwdargs.pop('N')):
        if i % 300 == 0:
            global_terminal.post_message(TerminalWrite(f'dit is {i}'))            
            logging.debug(f'dit is {i}')
    return False

ToolTips = {'root': 'De directory waarbinnen gezocht wordt naar (nieuwe) aanvragen',
            'forms': 'De directory waar beoordelingsformulieren worden aangemaakt',
            'database':'De database voor het programma',
            'edit_root': 'Kies de directory',
            'edit_forms': 'Kies de directory',
            'edit_database': 'Kies de database',
            'scan': 'Zoek nieuwe aanvragen in root-directory/subdirectories, maak aanvraagformulieren',
            'mail': 'Zet mails klaar voor beoordeelde aanvragen',
            'preview_preview': 'Laat verloop van de acties zien; Geen wijzigingen in bestanden of database',
            'preview_uitvoeren': 'Voer acties uit. Wijzigingen in bestanden en database, kan niet worden teruggedraaid'
            }

@dataclass
class AapaTuiParams:
    root_directory: str = ''
    forms_directory: str = ''
    database: str = ''
    preview: bool = True

class AapaConfiguration(Static):
    def compose(self)->ComposeResult:
        with Vertical():
            with Horizontal():
                yield LabeledInput('Root directory', width = '100', id='root', validators=Required(), tooltip=ToolTips['root'])
                yield Button('...', id='edit_root', classes='small')
            with Horizontal():
                yield LabeledInput('Forms directory', width = '100', id='forms', validators=Required(), tooltip=ToolTips['forms'])
                yield Button('...', id='edit_forms', classes='small')
            with Horizontal():
                yield LabeledInput('Database', width = '100', id='database', validators=Required(), tooltip=ToolTips['database'])
                yield Button('...', id='edit_database', classes='small')                
    def on_mount(self):
        self.border_title = 'AAPA Configuratie'
        for id in ['edit_root', 'edit_forms', 'edit_database']:
            self.query_one(f'#{id}', Button).tooltip = ToolTips[id]
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
            case 'edit_root': self.edit_root()
            case 'edit_forms': self.edit_forms()
            case 'edit_database': self.edit_database()
        message.stop()
    def edit_root(self):
        self._select_directory('root', 'Select root directory')
    def edit_forms(self):
        self._select_directory('forms', 'Select forms directory')
    def edit_database(self):
        self._select_file('database','Select databasefile', 'database files', '.db')
    @property
    def params(self)-> AapaTuiParams:
        return AapaTuiParams(root_directory= self.query_one('#root', LabeledInput).input.value, 
                             forms_directory= self.query_one('#forms', LabeledInput).input.value,
                             database=self.query_one('#database', LabeledInput).input.value)
    @params.setter
    def params(self, value: AapaTuiParams):
        self.query_one('#root', LabeledInput).input.value = value.root_directory
        self.query_one('#forms', LabeledInput).input.value = value.forms_directory
        self.query_one('#database', LabeledInput).input.value = value.database
        
class AapaButtons(Static):
    def compose(self)->ComposeResult:
        with Horizontal():
            yield Button('Scan', variant= 'primary', id='scan')
            yield Button('Mail', variant ='primary', id='mail') 
            yield RadioSet('preview', 'uitvoeren', id='preview')
    def on_mount(self):
        radio = self.query_one(RadioSet)
        radio.styles.layout = 'horizontal'
        self.query_one('#scan', Button).tooltip = ToolTips['scan']
        self.query_one('#mail', Button).tooltip = ToolTips['mail']
        radio.query(RadioButton)[0].value = True
        self.query(RadioButton)[0].tooltip = ToolTips['preview_preview']
        self.query(RadioButton)[1].tooltip = ToolTips['preview_uitvoeren']
    def toggle(self):
        self.preview = not self.preview
    @property
    def preview(self)->bool:
        return self.query(RadioButton)[0].value
    @preview.setter
    def preview(self, value: bool):
        buttons = self.query(RadioButton)
        if value:
            buttons[0].value = True
        else:
            buttons[1].value = True
  
class AapaApp(App):
    BINDINGS = [ 
                Binding('ctrl+s', 'scan', 'Scan nieuwe aanvragen', priority = True),
                Binding('ctrl+m', 'mail', 'Zet mails klaar', priority = True),         
                Binding('ctrl+p', 'toggle_preview', 'Toggle preview mode', priority=True),
                Binding('ctrl+r', 'edit_root', 'Bewerk root directory', priority = True, show=False),
                Binding('ctrl+f', 'edit_forms', 'Bewerk forms directory', priority = True, show=False),
                Binding('ctrl+d', 'edit_database', 'Kies database file', priority = True, show=False),
               ]
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
    
    async def activate_terminal(self)->bool:
        logging.debug(f'activate run terminal {self.terminal_active}')
        if self.terminal_active:
            return False
        await self.app.push_screen('terminal', self.callback_run_terminal)
        self.terminal_active = True
        self.terminal.clear()
        return True
    async def on_button_pressed(self, message: Button.Pressed):
        logging.debug(f'button {message.button.id}')
        match message.button.id:
            case 'scan': await self.action_scan()
            case 'mail': await self.action_mail()
        message.stop()
    # def on_key(self, event: events.Key) -> None:
    #     """Write Key events to log."""
    #     if self.terminal_active:
    #         self.terminal.write('\n'+ str(event))
    async def action_scan(self):    
        params = self.params
        logging.debug(f'{params=}')
        if await self.activate_terminal():
            self.terminal.write(f'INITIALIZE SCAN {datetime.strftime(datetime.now(), "%d-%m-%Y, %H:%M:%S")}')
            self.terminal.run(testscript, N=5000, params=params)                
    async def action_mail(self):
        params = self.params
        if await self.activate_terminal():
            self.terminal.write(f'INITIALIZE MAIL {datetime.strftime(datetime.now(), "%d-%m-%Y, %H:%M:%S")}')
            self.terminal.run(testscript, N=5000, params=params)                
    @property 
    def params(self)->AapaTuiParams:
        result = self.query_one(AapaConfiguration).params
        result.preview = self.query_one(AapaButtons).preview
        return result
    @params.setter
    def params(self, value: AapaTuiParams):
        self.query_one(AapaConfiguration).params = value
        self.query_one(AapaButtons).preview = value.preview
    def action_toggle_preview(self):
        self.query_one(AapaButtons).toggle()
    def action_edit_root(self):
        self.query_one(AapaConfiguration).edit_root()
    def action_edit_forms(self):
        self.query_one(AapaConfiguration).edit_forms()
    def action_edit_database(self):
        self.query_one(AapaConfiguration).edit_database()

if __name__ == "__main__":
    logging.basicConfig(filename='terminal.log', filemode='w', format='%(module)s-%(funcName)s-%(lineno)d: %(message)s', level=logging.DEBUG)
    app = AapaApp()
    app.run()