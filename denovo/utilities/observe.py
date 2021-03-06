"""
decorators: denovo class, function, and method decorators
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    add_name (denovo.base.Operation): adds a 'name' attribute to 'process' if one was not 
        passed as an argument based on the '__name__' attribute of the item
        passed.
    register (denovo.base.Operation): registers the wrapped function to REGISTRY.
    set_registry (denovo.base.Operation): sets REGISTRY to a dict or dict like object.


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


""" Module-Level Attributes """

catalog: MutableMapping[str, denovo.base.Operation] = {}

""" Functions """

def add_name(process: denovo.base.Wrappable) -> denovo.base.Wrappable:
    """Adds 'name' attribute to 'process' if it wasn't passed as an argument.
    
    The decorator uses the 'denovo.unit.get_name' to determine the specific value
    for the 'name' attribute.
    
    Args:
        process (denovo.base.Wrappable): function, method, class, or instance to add a 
            'name' to if 'name' was not passed as an argument.
    
    """
    @functools.wraps(process)
    def wrapped(*args: Any, **kwargs: Any) -> denovo.base.Operation:
        call_signature = inspect.signature(process)
        arguments = dict(call_signature.bind(*args, **kwargs).arguments)
        if not arguments.get('name'):
            arguments['name'] = denovo.unit.get_name(item = process)
        return process(**arguments)
    return wrapped

def register(func: denovo.base.Operation) -> denovo.base.Operation:
    """Decorator for a function registry.
    
    Args:
        func (denovo.base.Operation): any function.
        
    Returns:
        denovo.base.Operation: with passed arguments.
        
    """
    name = func.__name__
    catalog[name] = func
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> denovo.base.Operation:
        return func(*args, **kwargs)
    return wrapper

def set_registry(registry: MutableMapping[str, denovo.base.Operation]) -> None:
    """sets registry for the 'register' decorator.
    
    Args:
        registry (MutableMapping[str, denovo.base.Operation]): dict or dict-like item to use
            for storing functions.
            
    """
    globals()['catalog'] = registry
    return
