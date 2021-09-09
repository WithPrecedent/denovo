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
import inspect
import functools
import types
from typing import Any, Optional, Type, Union, get_type_hints

import denovo
from denovo.typing import Operation, Wrappable


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

class Dispatcher(object):
    """Decorator for a dispatcher.
    
    This decorator is similar to python's singledispatch but it uses isintance
    checks to determint the approriate function to call. The code is adapted
    from the python source code for singledisptach.
    
    Attributes:
        registry (dict[str, denovo.typing.types.Kind]): registry for different
            functions that may be called based on the first parameter's type.
            Defaults to an empty dict.
        
    Returns:
        Operation: with passed arguments.
        
    """

    """ Initialization Methods """
    
    def __init__(self, wrapped: Operation):
        """Allows class to be called as a function decorator."""
        self.wrapped = wrapped
        self.registry: dict[str, Operation] = {}
        # Copies key attributes and functions to wrapped function.
        self.wrapped.register = self.register
        self.wrapped.dispatch = self.dispatch
        self.wrapped.registry = self.registry
        # Updates wrapper information for tracebacks and introspection.
        functools.update_wrapper(self, self.wrapped)
        
    def __call__(self, *args: Any, **kwargs: Any) -> Operation:
        """Returns wrapped object with args and kwargs"""
        return self.wrapped(*args, **kwargs)
    
    """ Public Methods """
    
    def categorize(self, item: Any) -> str:
        """Determines the kind of 'item' and returns its str name."""
        if inspect.isclass(item):
            checker = issubclass
        else:
            checker = isinstance
        for value in denovo.types.catalog.values():
            if checker(item, value):
                return denovo.modify.snakify(item = value.__name__)
                # except AttributeError:
                #     return denovo.modify.snakify(value.__class__.__name__)
        raise KeyError(f'item does not match any recognized type')
           
    def dispatch(self, source: Any, *args: Any, **kwargs: Any) -> Operation:
        """[summary]

        Args:
            source (Any): [description]

        Returns:
            Operation: [description]
            
        """
        key = self.categorize(item = source)
        try:
            dispatched = self.registry[key]
        except KeyError:
            dispatched = self.dispatcher
        return dispatched(source, *args, **kwargs)

    def register(self, dispatched: Operation) -> Operation:
        """[summary]

        Args:
            dispatched (Operation): [description]

        Returns:
            Operation: [description]
            
        """
        _, kind = next(iter(get_type_hints(dispatched).items()))
        key = kind.__name__
        self.registry[key] = dispatched
        return dispatched
    
    def wrapper(self, *args: Any, **kwargs: Any) -> Operation:
        if not args:
            parameter, argument = next(iter(kwargs.items()))
            del kwargs[parameter]
            args = tuple([argument])
        return self.dispatch(*args, **kwargs)  

def dispatcher(dispatcher: Operation) -> Operation:
    """Decorator for a single dispatcher that checks subtypes.
    
    This decorator is similar to python's singledispatch but it uses isintance
    checks to determint the approriate function to call. The code is adapted
    from the python source code for singledisptach.
    
    Args:
        dispatcher (Operation): a callable converter.
        
    Returns:
        Operation: with passed arguments.
        
    """
    # Creates a registry for dispatchers.
    registry: dict[str, types.FunctionType] = {}
    
    def categorize(item: Any) -> str:
        """Determines the kind of 'item' and returns its str name."""
        if inspect.isclass(item):
            checker = issubclass
        else:
            checker = isinstance
        for kind, name in denovo.types.kind.matcher.items():
            if checker(item, value):
                return denovo.modify.snakify(value.__name__)
                # except AttributeError:
                #     return denovo.modify.snakify(value.__class__.__name__)
        raise KeyError(f'item does not match any recognized type')
        
    def dispatch(source: Any, *args: Any, **kwargs: Any) -> Operation:
        key = categorize(item = source)
        try:
            dispatched = registry[key]
        except KeyError:
            dispatched = dispatcher
        return dispatched(source, *args, **kwargs)

    def register(dispatched: Operation) -> None:
        _, kind = next(iter(get_type_hints(dispatched).items()))
        key = kind.__name__
        registry[key] = dispatched
        return
    
    def wrapper(*args: Any, **kwargs: Any) -> Operation:
        if not args:
            parameter, argument = next(iter(kwargs.items()))
            del kwargs[parameter]
            args = tuple([argument])
        return dispatch(*args, **kwargs)

    wrapper.register = register # type: ignore
    wrapper.dispatch = dispatch # type: ignore
    wrapper.registry = registry # type: ignore
    functools.update_wrapper(wrapper, dispatcher)
    return wrapper   
