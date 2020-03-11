from queue import Queue, Empty
from threading import Thread
from tkinter.ttk import Style

import worldview
from toolbox.toolbox_ui import ToolWindow
from tkinter import Tk, TOP, BOTH


class CommandDispatcherThread(Thread):
    # todo: move this to its own class

    _quitting = False

    def __init__(self, command_queue: Queue, quit_function):
        self._command_queue = command_queue
        self._quit_function = quit_function
        super().__init__()

    def run(self):
        while not self._quitting:
            while not self._command_queue.empty():
                try:
                    command = self._command_queue.get()
                    print("Command processed!")
                    print(command)
                    if command == "UI_QUIT":
                        self.stop()
                except Empty as e:
                    break
                except Exception as e:
                    print(e)
        # quitting
        self._quit_function()

    def stop(self):
        self._quitting = True


class Application:
    # application should hold the tk window and the pyglet window
    pyglet_window = None
    tk_window = None
    ui_command_queue = Queue()

    def __init__(self):
        self.tk_thread = Thread(target=self.create_tk_ui)
        self.tk_thread.daemon = True
        self.pyglet_thread = Thread(target=self.create_pyglet_ui)
        self.pyglet_thread.daemon = True
        self.ui_command_dispatcher_thread = CommandDispatcherThread(self.ui_command_queue, self.stop)
        self.ui_command_dispatcher_thread.daemon = True

    def create_tk_ui(self):
        self.tk_window = Tk()
        self.tk_window.style = Style()
        self.tk_window.style.theme_use("classic")
        self.tk_window.geometry("300x600+300+300")
        self.tk_window.toolbox = ToolWindow(self.tk_window, self.ui_command_queue)
        self.tk_window.toolbox.pack(side=TOP, fill=BOTH, expand=1)
        self.tk_window.protocol("WM_DELETE_WINDOW", self.tk_window.toolbox.quit_external)

        self.tk_window.mainloop()

    def create_pyglet_ui(self):
        worldview.main()

    def run(self):
        self.ui_command_dispatcher_thread.start()
        self.tk_thread.start()
        # self.pyglet_thread.start()

        # self.pyglet_thread.join()
        self.create_pyglet_ui()
        self.tk_thread.join()
        self.ui_command_dispatcher_thread.join()

    def stop(self):
        worldview.exit_app()


def main():
    Application().run()


if __name__ == '__main__':
    main()
