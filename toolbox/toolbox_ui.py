from queue import Queue
from tkinter import Frame, Tk, Menu, BOTTOM, X, SUNKEN, W, Label, Button, TOP, BOTH


class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, fmt, *args):
        self.label.config(text=fmt % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


class ToolWindow(Frame):
    def __init__(self, parent: Tk, command_queue: Queue):
        Frame.__init__(self, parent)
        self.parent = parent
        self.command_queue = command_queue

        self._menu_bar = Menu(self.parent)
        self.parent.config(menu=self._menu_bar)
        self._command_menu = Menu(self._menu_bar, tearoff=0)
        self._command_menu.add_command(label="Quit", command=self.menu_quit)
        self._menu_bar.add_cascade(label="File", menu=self._command_menu)
        self.status = StatusBar(self)
        self.status.pack(side=BOTTOM, fill=X)

        self.content_frame = Frame(self)
        self.content_frame.pack(side=BOTTOM, fill=BOTH, expand=1)

        self.click_to_start_button = Button(self.content_frame, text="Start game!")
        self.click_to_start_button.pack(side=TOP)
        self.click_to_start_button.bind("<Button-1>", self.click_to_start)

    def quit_external(self):
        return self.quit_event(None)

    def menu_quit(self):
        self.quit_event(None)

    def quit_event(self, event):
        self.command_queue.put("UI_QUIT")
        self.parent.destroy()

    def click_to_start(self, event):
        self.command_queue.put("UI_BUTTON")
        print("Started!")
        print(event)
