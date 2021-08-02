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
import abc
import dataclasses
import datetime
import inspect
import functools
import time
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Type, Union, get_type_hints)

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
    name = func.__name__
    REGISTRY[name] = func
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def set_registry(registry: MutableMapping[str, Callable]) -> None:
    """sets registry for the 'register' decorator.
    
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


class Dispatcher(object):
    """Decorator for a dispatcher.
    
    This decorator is similar to python's singledispatch but it uses isintance
    checks to determint the approriate function to call. The code is adapted
    from the python source code for singledisptach.
    
    This class doesn't follow the normal python naming convention for a class
    because it is only designed to be used as a decorator. But rather than 
    creating a nested function dispatcher (which cannot be inherited and
    extended), 'dispatcher' is a class.
    
    Args:
        wrapped (Callable): a callable dispatcher.
        registry (dict[str, denovo.typing.types.Kind]): registry for different
            functions that may be called based on the first parameter's type.
            Defaults to an empty dict.
        
    Returns:
        Callable: with passed arguments.
        
    """
    # wrapped: Callable
    # registry: dict[str, Callable] = dataclasses.field(default_factory = dict)
    
    """ Initialization Methods """
    
    def __init__(self, wrapped: Callable):
        """Allows class to be called as a function decorator."""
        self.wrapped = wrapped
        self.registry = {}
        # Copies key attributes and functions to wrapped function.
        self.wrapped.register = self.register
        self.wrapped.dispatch = self.dispatch
        self.wrapped.registry = self.registry
        # Updates wrapper information for tracebacks and introspection.
        functools.update_wrapper(self, self.wrapped)
        
    def __call__(self, *args: Any, **kwargs: Any) -> Callable:

        return self.wrapped(*args, **kwargs)
    
    """ Public Methods """
    
    def categorize(self, item: Any) -> str:
        """Determines the kind of 'item' and returns its str name."""
        if inspect.isclass(item):
            checker = issubclass
        else:
            checker = isinstance
        for value in denovo.typing.types.catalog.values():
            if checker(item, value):
                return denovo.tools.snakify(value.__name__)
                # except AttributeError:
                #     return denovo.tools.snakify(value.__class__.__name__)
        raise KeyError(f'item does not match any recognized type')
           
    def dispatch(self, source: Any, *args, **kwargs) -> Callable:
        """[summary]

        Args:
            source (Any): [description]

        Returns:
            Callable: [description]
            
        """
        key = self.categorize(item = source)
        try:
            dispatched = self.registry[key]
        except KeyError:
            dispatched = self.dispatcher
        return dispatched(source, *args, **kwargs)

    def register(self, dispatched: Callable) -> Callable:
        """[summary]

        Args:
            dispatched (Callable): [description]

        Returns:
            Callable: [description]
            
        """
        _, kind = next(iter(get_type_hints(dispatched).items()))
        key = kind.__name__
        self.registry[key] = dispatched
        return dispatched
    
    def wrapper(self, *args, **kwargs):
        if not args:
            parameter, argument = next(iter(kwargs.items()))
            del kwargs[parameter]
            args = tuple([argument])
        return self.dispatch(*args, **kwargs)  

def dispatcher(dispatcher: Callable) -> Callable:
    """Decorator for a converter registry and dispatcher.
    
    This decorator is similar to python's singledispatch but it uses isintance
    checks to determint the approriate function to call. The code is adapted
    from the python source code for singledisptach.
    
    Args:
        dispatcher (Callable): a callable converter.
        
    Returns:
        Callable: with passed arguments.
        
    """
    # Creates a registry for dispatchers.
    registry = {}
    
    def categorize(item: Any) -> str:
        """Determines the kind of 'item' and returns its str name."""
        if inspect.isclass(item):
            checker = issubclass
        else:
            checker = isinstance
        print('test kind catalog', denovo.typing.types.catalog)
        for value in denovo.typing.types.catalog.values():
            print('test kind name', value.__name__)
            if checker(item, value):
                return denovo.tools.snakify(value.__name__)
                # except AttributeError:
                #     return denovo.tools.snakify(value.__class__.__name__)
        raise KeyError(f'item does not match any recognized type')
        
    def dispatch(source: Any, *args, **kwargs) -> Callable:
        key = categorize(item = source)
        try:
            dispatched = registry[key]
        except KeyError:
            dispatched = dispatcher
        return dispatched(source, *args, **kwargs)

    def register(dispatched: Callable) -> None:
        _, kind = next(iter(get_type_hints(dispatched).items()))
        key = kind.__name__
        registry[key] = dispatched
        return dispatched
    
    def wrapper(*args, **kwargs):
        if not args:
            parameter, argument = next(iter(kwargs.items()))
            del kwargs[parameter]
            args = tuple([argument])
        return dispatch(*args, **kwargs)  

    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = registry
    functools.update_wrapper(wrapper, dispatcher)
    return wrapper   
