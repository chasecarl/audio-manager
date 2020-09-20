import numpy as np
import tkinter as tk
from view import MainView


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
        self.view = MainView(root)
        samples = self.load_samples()
        self.view.display_samples(samples)
    

    def load_samples(self):
        return ['Ani', 'Ata', 'Shalom']


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
