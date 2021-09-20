"""
polymotph: utilities for polymorphic objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    dispatcher (Callable, object): decorator for denovo's dispatch system 
        which has greater functionality to the python singledispatch method 
        using the Kind protocol system. It is also fully compatible with 
        python builtin types.
    Settings (Factory, Lexicon): stores configuration settings after either 
        loading them from disk or by the passed arguments. Settings accepts
        more file types than configparser, offers a more familiar dict 
        interface, and allows for automatic type inference. 

ToDo:
       
"""
from __future__ import annotations
import dataclasses
import functools
from typing import Any, Callable, Type, Union, get_type_hints


""" Dispatch System """

@dataclasses.dataclass
class dispatcher(object):
    """Decorator for a dispatcher.
    
    dispatcher violates the normal python convention of naming classes in
    capital case because it is only designed to be used as a callable decorator,
    where lowercase names are the norm.
    
    decorator attempts to solve two shortcomings of the current python 
    singledispatch framework: 
        1) It checks for subtypes of passed items that serve as the basis for
            the dispatcher. As of python 3.10, singledispatch tests the type of
            a passed argument was equivalent to a stored type which precludes
            testing of subtypes.
        2) It supports the denovo typing system which allows for an alternative 
            approach to parameterized generics that can be used at runtime. So,
            for example, singledispatch cannot match MutableSequence[str] to a
            function even though type annotations often prefer the flexibility
            of generics. However, dispatcher compares the passed argument with
            the types (and Kinds) stored in 'get_registry'.
    
    Attributes:
        wrapped (Wrappable): wrapped class or function.
        registry (dict[str, Callable[..., Any]]): registry for different 
            functions that may be called based on the first parameter's type. 
            Defaults to an empty dict.
        
    """
    wrapped: Union[object, Type[Any], Callable[..., Any]]
    registry: dict[str, Callable[..., Any]] = dataclasses.field(
        default_factory = dict)
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Allows class to be called as a function decorator."""
        # Updates 'wrapped' for proper introspection and traceback.
        functools.update_wrapper(self, self.wrapped)
        # Copies key attributes and functions to wrapped item.
        self.wrapped.register = self.register
        self.wrapped.dispatch = self.dispatch
        self.wrapped.registry = self.registry
        
    def __call__(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """Calls appropriate function with 'args' and 'kwargs'.
        
        Returns:
            Callable[..., Any]: function appropriate to the type of the 
                first argumetn passed.
        
        """ 
        return self.dispatch(*args, **kwargs)

    """ Public Methods """
      
    def dispatch(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """Calls appropriate function with 'args' and 'kwargs'.
        
        Returns:
            Callable[..., Any]: function appropriate to the type of the 
                first argumetn passed.
            
        """
        if args:
            item = args[0]
        else:
            item = list(kwargs.values())[0]
        key = _identify(item = item)
        return self.registry[key](*args, **kwargs)
    
    def register(self, wrapped: Callable[..., Any]) -> None:
        """Adds 'wrapped' to 'registry' based on type of its first parameter.

        Args:
            wrapped (Callable[..., Any]): wrapped callable.
            
        """
        _, annotation = next(iter(get_type_hints(wrapped).items()))
        key = _identify(item = annotation)
        self.registry[key] = wrapped
        return

def _identify(item: Any) -> str:
    """Determines the kind/type of 'item' and returns its str name."""
    # Local import as workaround for circular import.
    import denovo
    return denovo.base.identify(item = item)
    # return 'list'