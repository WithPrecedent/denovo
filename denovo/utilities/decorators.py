"""
decorators: denovo class, function, and method decorators
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    add_name (Callable): adds a 'name' attribute to 'process' if one was not 
        passed as an argument based on the '__name__' attribute of the item
        passed.
    register (Callable): registers the wrapped function to REGISTRY.
    set_registry (Callable): sets REGISTRY to a dict or dict like object.
    timer (Callalbe): computes the time it takes for the wrapped 'process' to
        complete.

ToDo:

"""
from __future__ import annotations
import datetime
import inspect
import functools
import time
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo

""" Type Annotations """

Processes: Type = Union[object, Type, Callable]

""" Module-Level Attributes """

REGISTRY: MutableMapping[str, Callable] = {}

""" Functions """

def add_name(process: Processes) -> Processes:
    """Adds 'name' attribute to 'process' if it wasn't passed as an argument.
    
    The decorator uses the 'denovo.tools.namify' to determine the specific value
    for the 'name' attribute.
    
    Args:
        process (Processes): function, method, class, or instance to add a 
            'name' to if 'name' was not passed as an argument.
    
    """
    @functools.wraps(process)
    def wrapped(*args, **kwargs):
        call_signature = inspect.signature(process)
        arguments = dict(call_signature.bind(*args, **kwargs).arguments)
        if not arguments.get('name'):
            arguments['name'] = denovo.tools.namify(item = process)
        return process(**arguments)
    return wrapped

def register(func: Callable) -> Callable:
    """Decorator for a function registry.
    
    Args:
        func (Callable): any function.
        
    Returns:
        Callable: with passed arguments.
        
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        REGISTRY[name] = func
        return func(*args, **kwargs)
    return wrapper

def set_registry(registry: MutableMapping[str, Callable]) -> None:
    """Sets registry for the 'register' decorator.
    
    Args:
        registry (MutableMapping[str, Callable]): dict or dict-like item to use
            for storing functions.
            
    """
    globals().REGISTRY = registry
    return
    
def timer(process: Callable) -> Callable:
    """Decorator for computing the length of time a process takes.

    Args:
        process (Callable): wrapped callable to compute the time it takes to 
            complete its execution.

    """
    try:
        name = process.__name__
    except AttributeError:
        name = process.__class__.__name__
    def shell_timer(_function):
        def decorated(*args, **kwargs):
            def convert_time(seconds: int) -> tuple(int, int, int):
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                return hours, minutes, seconds
            implement_time = time.time()
            result = _function(*args, **kwargs)
            total_time = time.time() - implement_time
            h, m, s = convert_time(total_time)
            print(f'{name} completed in %d:%02d:%02d' % (h, m, s))
            return result
        return decorated
    return shell_timer
