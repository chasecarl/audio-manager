import numpy as np


def join(iterable, on):
    # assuming all the inputs have the same number of channels (shape[1])
    it = iter(iterable)
    # asssuming there is at least one object in the iterable
    joined_iterable = [next(it)]
    for el in it:
        joined_iterable.append(on)
        joined_iterable.append(el)
    return np.concatenate(joined_iterable, axis=0)

