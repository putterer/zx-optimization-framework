from io import BytesIO
from typing import TypeVar, Callable

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


def round_complex(c: complex, digits: int = 8):
    return round(c.real, digits) + round(c.imag, digits) * 1j


T = TypeVar("T")
S = TypeVar("S")

def flat_map(f: Callable[[T], list[S]], l: list[T]) -> list[S]:
    return [e for o in l for e in f(o)]

def flatten(l: list[list[T]]) -> list[T]:
    return flat_map(lambda x: x, l)

