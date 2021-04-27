import tkinter as tk


class Renderer:

    def __init__(self, canvas: tk.Canvas):
        self.canvas: tk.Canvas = canvas
        self.width: int = 0
        self.height: int = 0

        self.on_resize()

    def on_resize(self):
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        print(f"Resized to {self.width}x{self.height}")
