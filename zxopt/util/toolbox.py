from io import BytesIO

from IPython.display import display, SVG

cached_is_interactive: bool = None
def is_interactive():
    global cached_is_interactive
    if cached_is_interactive is not None:
        return cached_is_interactive

    try:
        cached_is_interactive = get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        cached_is_interactive = False

    if not cached_is_interactive:
        print("Running non interactively, logging enabled")

    return cached_is_interactive

def display_in_notebook(io: BytesIO):
    display(SVG(data=io.getvalue()))