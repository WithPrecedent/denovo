"""
clock: date and time related tools
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:   
    how_soon_is_now (Callable): converts a current date and time to a str.
    timer (Callalbe): computes the time it takes for the wrapped 'process' to
        complete.  
ToDo:


"""
from __future__ import annotations
import datetime
import time
from typing import Any, Optional, Type, Union

import denovo


""" General Tools """

def how_soon_is_now(
    prefix: Optional[str] = None,
    time_format: str = '%Y-%m-%d_%H-%M') -> str:
    """Creates a string from current date and time.

    Args:
        prefix: a prefix to add to the returned str.
        
    Returns:
        str: with current date and time in 'format' format.

    """
    time_string = datetime.datetime.now().strftime(time_format)
    if prefix is None:
        return f'{prefix}{time_string}'
    else:
        return time_string

""" Decorators """

def timer(process: denovo.base.Operation) -> denovo.base.Operation:
    """Decorator for computing the length of time a process takes.

    Args:
        process (denovo.base.Operation): wrapped callable to compute the time 
            it takes to complete its execution.

    """
    try:
        name = process.__name__
    except AttributeError:
        name = process.__class__.__name__
    def shell_timer(
        operation: denovo.base.Operation) -> denovo.base.Operation:
        def decorated(*args: Any, **kwargs: Any) -> denovo.base.Operation:
            def convert_time(
                seconds: Union[int, float]) -> tuple[int, int, int]:
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                return int(hours), int(minutes), int(seconds)
            implement_time = time.time()
            result = operation(*args, **kwargs)
            total_time = time.time() - implement_time
            h, m, s = convert_time(total_time)
            print(f'{name} completed in %d:%02d:%02d' % (h, m, s))
            return result
        return decorated
    return shell_timer
