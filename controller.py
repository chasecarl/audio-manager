import numpy as np
import tkinter as tk
import logging


from view import MainView
from model import ListModel


def join(iterable, on):
    # assuming all the inputs have the same number of channels (shape[1])
    it = iter(iterable)
    # asssuming there is at least one object in the iterable
    joined_iterable = [next(it)]
    for el in it:
        joined_iterable.append(on)
        joined_iterable.append(el)
    return np.concatenate(joined_iterable, axis=0)


class Controller:

    def __init__(self, root):
        self.model = ListModel()
        self.view = MainView(root)
        self.model.add_callback(self.model_changed)
        self.view.add_callback(self.selection_changed)
        self.view.display_samples(self.model)
        self.view.remove_button.config(command=self.remove_entry)


    def selection_changed(self, selection):
        logging.debug(f'C: Passing the following selection to the model: {str(selection)}')
        self.model.set_selected(selection)


    def model_changed(self):
        self.view.display_samples(self.model)


    def remove_entry(self):
        self.model.remove_entry()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
