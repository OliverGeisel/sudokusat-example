import time
from typing import Tuple


def time_needed(func, *args, **kwargs) -> Tuple[float, object]:
    """
    A simple function to get the time, which an other function need

    :param func: The function
    :param args: Arguments for func. Need to be in a list
    :param kwargs: Named-Arguments for func. Need to be in a dictionary
    :return: Time to execute the func
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return end - start, result
