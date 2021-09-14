"""
decorators: denovo class, function, and method decorators
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    add_name (Operation): adds a 'name' attribute to 'process' if one was not 
        passed as an argument based on the '__name__' attribute of the item
        passed.
    register (Operation): registers the wrapped function to REGISTRY.
    set_registry (Operation): sets REGISTRY to a dict or dict like object.


ToDo:

"""
from __future__ import annotations
from collections.abc import MutableMapping
import dataclasses
import inspect
import functools
import types
from typing import Any, ClassVar, Optional, Type, Union, get_type_hints

import denovo
from denovo.typing.types import Operation, Wrappable


""" Module-Level Attributes """

catalog: MutableMapping[str, Operation] = {}

""" Functions """

def add_name(process: Wrappable) -> Wrappable:
    """Adds 'name' attribute to 'process' if it wasn't passed as an argument.
    
    The decorator uses the 'denovo.check.get_name' to determine the specific value
    for the 'name' attribute.
    
    Args:
        process (Wrappable): function, method, class, or instance to add a 
            'name' to if 'name' was not passed as an argument.
    
    """
    @functools.wraps(process)
    def wrapped(*args: Any, **kwargs: Any) -> Operation:
        call_signature = inspect.signature(process)
        arguments = dict(call_signature.bind(*args, **kwargs).arguments)
        if not arguments.get('name'):
            arguments['name'] = denovo.check.get_name(item = process)
        return process(**arguments)
    return wrapped

def register(func: Operation) -> Operation:
    """Decorator for a function registry.
    
    Args:
        func (Operation): any function.
        
    Returns:
        Operation: with passed arguments.
        
    """
    name = func.__name__
    catalog[name] = func
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Operation:
        return func(*args, **kwargs)
    return wrapper

def set_registry(registry: MutableMapping[str, Operation]) -> None:
    """sets registry for the 'register' decorator.
    
    Args:
        registry (MutableMapping[str, Operation]): dict or dict-like item to use
            for storing functions.
            
    """
    globals()['catalog'] = registry
    return
