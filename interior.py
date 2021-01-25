from prompt_toolkit import Application, HTML
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from itertools import groupby
import collections
import argparse

def strip(text):
    return "".join([x for x in text.lower() if x.isalpha()])

parser = argparse.ArgumentParser()
parser.add_argument('domain', type=str)
args = parser.parse_args()
members = set(strip(args.domain))

def show(text, color=None):
    # TODO: color support

    text = "".join(
        sorted(
            list(
                filter(lambda x: not x.isspace(),
                       text))))
    if len(text) < 15:
        return " ".join(text)
    else:
        return text

message = args.domain

def complement(text):
    return show(members - set(text))

all_remaining = FormattedTextControl(text=show(args.domain))
all_overused = FormattedTextControl(text=show(""))
all_excess = FormattedTextControl(text=show(""))

def assess(event):
    global all_remaining
    global all_excess
    global all_overused

    excess = []
    overused = []
    remaining = []

    lines = event.text.splitlines()
    for i, line in enumerate(lines):
        remaining.append(show(members - set(line)))
        excess.append(show(
            filter(lambda x: x not in members, line)))
        overused.append(show(
            map(lambda x: x[0],
                filter(lambda x: x[1] > 1,
                       collections.Counter(line).items()))))

    if event.text:
        if event.text[-1] == '\n':

            remaining.append(show(args.domain))

        all_remaining.text = "\n".join(remaining)
        all_excess.text = "\n".join(excess)
        all_overused.text = "\n".join(overused)


used = Buffer(on_text_changed=assess)
kb = KeyBindings()

@kb.add('c-q')
def exit_(event):
    event.app.exit()

root_container = HSplit([
    Window(height=1, content=FormattedTextControl(text=message)),
    Window(height=1, char='-'),
    VSplit([
        Window(content=BufferControl(buffer=used)),
        Window(width=1, char='|'),
        Window(content=all_remaining),
        Window(width=1, char='|'),
        Window(content=all_overused),
        Window(width=1, char='|'),
        Window(content=all_excess),
    ]),
    Window(height=1, char='-'),
    Window(height=1, content=FormattedTextControl(text="Ctrl + Q to Quit"))
])

layout = Layout(root_container)



app = Application(key_bindings=kb, layout=layout)
app.run()
print('\n\n' + used.text)
