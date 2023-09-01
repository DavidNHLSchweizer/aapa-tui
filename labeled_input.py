from textual.app import ComposeResult
from textual.widgets import Static, Label, Input

class LabeledInput(Static):
    def __init__(self, label_text, horizontal=False, width=None, **kwdargs):
        self._label_text = label_text
        self._horizontal = horizontal
        self._width = width
        self._validators = kwdargs.pop('validators', None)
        super().__init__('', **kwdargs)
    def _label_id(self)->str:
        return f'{self.id}-label'
    def _input_id(self)->str:
        return f'{self.id}-input'
    def on_mount(self):
        self.styles.width = self._width
        self.horizontal = self._horizontal
    @property
    def input(self)->Input:
        return self.query_one(f'#{self._input_id()}', Input)
    @property
    def label(self)->Label:
        return self.query_one(f'#{self._label_id()}', Label)
    @property
    def horizontal(self)->bool:
        return self._horizontal
    @horizontal.setter
    def horizontal(self, value: bool):
        self._horizontal = value
        if value:
            self.styles.layout = 'horizontal'
            self.styles.align_vertical = 'middle'
            self.label.styles.margin=(1,1,0,0)
            self.input.styles.max_width = self._width - len(self._label_text)-1
        else:
            self.styles.layout = 'vertical'
            self.styles.align_horizontal = 'left'
            self.label.styles.margin=(0,0,0,0)
            self.input.styles.width = '100w'
            self.input.styles.max_width = self._width

    def compose(self)->ComposeResult:
        yield Label(self._label_text, id=self._label_id())
        yield Input('', id=self._input_id(), validators=self._validators) 

if __name__ == "__main__":
    import logging
    from textual.app import App
    from textual.widgets import Footer
    from required import Required
    class TestApp(App):
        BINDINGS = [
                    ('t', 'toggle_', 'Toggle horizontal'),
                    ]  
        def compose(self) -> ComposeResult:
            yield LabeledInput('Labeling', True, 60, validators=Required, id='labeling')
            yield LabeledInput('qbux234234 234234 234 234', False, 50, validators=None, id='labeling2')
            yield Footer()
        def action_toggle_(self):           
            labi = self.query_one('#labeling', LabeledInput)
            labi.horizontal = not labi.horizontal
            busi = self.query_one('#labeling2', LabeledInput)
            busi.horizontal = not busi.horizontal
    logging.basicConfig(filename='testing.log', filemode='w', format='%(module)s-%(funcName)s-%(lineno)d: %(message)s', level=logging.DEBUG)
    app = TestApp()
    app.run()