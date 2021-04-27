import tkinter as tk

from src.util import config
# https://realpython.com/python-gui-tkinter/
from src.visualization import Renderer


class Window:
    def __init__(self):
        self.window: tk.Tk = None
        self.toolbar = None # TODO: type
        self.info_area = None
        self.canvas_area = None
        self.canvas: tk.Canvas = None
        self.renderer = None

        self.init_window()

        self.window.bind("<Configure>", self.on_resize)

    def init_window(self):
        self.window = tk.Tk()
        self.window.title(config["visualization"]["window_title"])
        self.window.geometry("1366x768")

        self.window.rowconfigure(0, weight=0, minsize=30)
        self.window.rowconfigure(1, weight=1, minsize=30)
        self.window.rowconfigure(2, weight=0, minsize=30)
        self.window.columnconfigure(0, weight=1, minsize=30)

        self.toolbar = self.init_toolbar()
        self.toolbar.grid(row=0, column=0, pady=15, padx=15, sticky="nw")

        self.canvas_area = self.init_canvas()
        self.canvas_area.grid(row=1, column=0, pady=0, padx=15, sticky="nsew")
        #
        self.info_area = self.init_info_area()
        self.info_area.grid(row=2, column=0, pady=15, padx=15, sticky="sw")

    def init_canvas(self):
        frame = tk.Frame(self.window, bg="yellow")

        self.canvas = tk.Canvas(frame, bg="green", width=50, height=50)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = Renderer(self.canvas)

        return frame

    def init_toolbar(self):
        frame = tk.Frame(self.window)

        cursor_button = tk.Button(frame, text="Cursor")
        cursor_button.grid(column=0, padx=5, sticky="e")

        return frame

    def init_info_area(self):
        frame = tk.Frame(self.window)

        label = tk.Label(frame, text="InfoArea")
        label.grid(column=0, row=0, padx=0)
        status_label = tk.Label(frame, text="someStatus")
        status_label.grid(column=1, row=0, padx=7)

        return frame

    def on_resize(self, event):
        self.renderer.on_resize()



    def main_loop(self):
            self.window.mainloop()
