"""monotimer v0.0.1"""


from functools import wraps
from time import monotonic, monotonic_ns


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def mono_timer(func):
    """The decorator time function. This is the encapsulating timer
        functionthat takes one argument, the child function, to calculate the
        duration of time.

    - Args:
        - child_function ([function]): the child function to execute

    - Return:
        - wrapper_function: tuple
            - 0: child function name
            - 1: duration the time function ran using time.monotonic
            - 2: the child function return
    """
    # ~~~ #         timer function section
    # using functools.wraps to pass along the child_function details
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        """The decorator time function. This is the timer function
         that takes one argument, the child function, to calculate the
         duration of time.

        - Args:
            - child_function ([function]): the child function to execute

        - Return:
            - wrapper_function: tuple
                - 0: child function name
                - 1: duration the time function ran using time.monotonic
                - 2: the child function return
        """
        t_start = monotonic()
        return_var = func(*args, **kwargs)
        t_stop = monotonic()
        return func.__name__, t_stop - t_start, return_var
    return wrapper_function


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def mono_ns_timer(func):
    """The decorator time function. This is the encapsulating timer
        functionthat takes one argument, the child function, to calculate the
        duration of time.

    - Args:
        - child_function ([function]): the child function to execute

    - Return:
        - wrapper_function: tuple
            - 0: child function name
            - 1: duration the time function ran using time.monotonic_ns
            - 2: the child function return
    """
    # ~~~ #         timer function section
    # using functools.wraps to pass along the child_function details
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        """The decorator time function. This is the encapsulating timer
         functionthat takes one argument, the child function, to calculate the
         duration of time.

        - Args:
            - child_function ([function]): the child function to execute

        - Return:
            - wrapper_function: tuple
                - 0: child function name
                - 1: duration the time function ran using time.monotonic
                - 2: the child function return
        """
        t_start = monotonic_ns()
        return_var = func(*args, **kwargs)
        t_required = monotonic_ns() - t_start
        return func.__name__, t_required, return_var
    return wrapper_function
