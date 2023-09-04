from textual.app import ComposeResult
from textual.css.scalar import Scalar, Unit
from textual.containers import Horizontal
from textual.widgets import Static, Label, Input, Button
from textual.events import Resize
from textual.binding import Binding     
import logging

class LabeledInput(Static):
    HORIZONTAL = 'labeled_input--horizontal'
    VERTICAL   = 'labeled_input--vertical'
    COMPONENT_CLASSES = [HORIZONTAL, VERTICAL]

    DEFAULT_CSS = """
    LabeledInput.labeled_input--horizontal {
        layout: horizontal;
    }
    LabeledInput.labeled_input--horizontal Label {
        align-vertical: middle;
        margin: 1 1 0 0;
    }
    LabeledInput.labeled_input--horizontal Input {
        max-width: 100%;
    }
    LabeledInput.labeled_input--vertical {
        layout: vertical;
        align-horizontal: left;
        margin: 0 0 0 0;
        width: 100%;
        max-width: 100%;
    }
    .small {
        max-width: 5;
    }
    """
    def __init__(self, label_text, horizontal=False, width=None, button=False, **kwdargs):
        self._label_text = label_text
        self._width = width
        self._validators = kwdargs.pop('validators', None)
        self._button = button
        super().__init__('', **kwdargs, classes = LabeledInput.HORIZONTAL if horizontal else LabeledInput.VERTICAL)
    def compose(self)->ComposeResult:
        yield Label(self._label_text, id=self._label_id())
        if self._button:
            with Horizontal():
                yield Input('', id=self._input_id(), validators=self._validators) 
                yield Button('...', id='edit_root', classes='small')
        else:
            yield Input('', id=self._input_id(), validators=self._validators) 
    def on_mount(self):
        if self._width:
            self.styles.width = Scalar(self._width, Unit.CELLS, Unit.WIDTH)
        else:
            self.styles.width = Scalar(100, Unit.WIDTH, Unit.PERCENT)
    def _label_id(self)->str:
        return f'{self.id}-label'
    def _input_id(self)->str:
        return f'{self.id}-input'
    @property
    def _button_size(self)->int:
        return 5 if self._button else 0
    def on_resize(self, message: Resize):        
        if self.horizontal:
            self.input.styles.width = message.size.width - len(self._label_text)-1 - self._button_size
        else:
            self.input.styles.width = message.size.width - self._button_size
    @property
    def input(self)->Input:
        return self.query_one(f'#{self._input_id()}', Input)
    @property
    def label(self)->Label:
        return self.query_one(f'#{self._label_id()}', Label)
    @property
    def horizontal(self)->bool:
        return LabeledInput.HORIZONTAL in self.classes 
    @horizontal.setter
    def horizontal(self, value: bool):
        self.classes = LabeledInput.HORIZONTAL if value else LabeledInput.VERTICAL

if __name__ == "__main__":
    import logging
    from textual.app import App
    from textual.widgets import Footer
    from required import Required
    class TestApp(App):
        BINDINGS = [
                    ('t', 'toggle_', 'Toggle horizontal'),
                    # Binding('alt+w', 'width_', 'width truuk', priority=True)
                    ]  
        def compose(self) -> ComposeResult:
            yield LabeledInput('Labeling', True, width=60, validators=Required(), id='labeling')
            yield LabeledInput('qbux234234 234234 234 234', False, width=50, validators=None, id='labeling2')
            yield LabeledInput('Raveling', True, validators=Required(), id='labeling3')
            yield LabeledInput('qbux234234 dsriugt6i3u4ui 234', False, validators=None, id='labeling4')
            yield LabeledInput('Sexy mf', False, validators=Required(), button=True, id='labeling5')
            yield LabeledInput('TRaveling Light', True, validators=Required(), button=True, id='labeling7')
            yield Button('De Button')
            yield Footer()
        def action_toggle_(self):           
            for labi in self.query(LabeledInput):
                labi.horizontal = not labi.horizontal

    logging.basicConfig(filename='testing.log', filemode='w', format='%(module)s-%(funcName)s-%(lineno)d: %(message)s', level=logging.DEBUG)
    app = TestApp()
    app.run()