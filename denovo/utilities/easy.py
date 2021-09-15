"""
types: denovo type protocols, aliases, and variables
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

The base class types in denovo serve two purposes (unless otherwise noted):
    1) They can be base classes that can be inherited from with attributes,
        methods, and properties.
    2) They act as de facto protocols that allow non-inherited and 
        non-registered classes/instances to be recognized as subclasses/
        instances if they meet certain criteria.
It is this second purpose that attempts to bridge the demands of static type 
checkers and runtime type checking that currently is impossible with the typing
module in python. It also affords users greater flexibility in designing 
compatible classes without hassling with inheritance or abstract base class
registration.

Contents:
    Type Aliases:
        denovo.alias.Operation: generic, flexible Callable type alias.
        denovo.alias.Signatures: dict of denovo.alias.Signatures type.
        denovo.alias.Wrappable: type for an item that can be wrapped by a decorator.
    Module Level Variables:
        BUILTINS (dict): mapping with str names of builtin in a types and values
            as the (generic) type to compare against.
        registry (dict): using the module '__getattr__' function, 'registry' 
            acts as a constantly updated registry of Kind subclasses and 
            BUILTINS. Until a tree structure is built for the Kind registry, the 
            order of 'registry' determines the order of matching. So, BUILTINS 
            are always placed at the bottom of the dict to prioritize user 
            created classes.
    Simplified Protocol System:
        Kind (ABC): denovo protocol class which allows classes to be defined in
             manner that facilitates static and runtime type checking including
             attributes, properties, methods, and method signatures.
        dispatcher (Callable, object): decorator for denovo's dispatch system 
            which has greater functionality to the python singledispatch method 
            using the Kind protocol system. It is also fully compatible with 
            python builtin types.
        identify (Callable): determines the matching Kind or builtin python 
            type.
        kindify (Callable): convenience function for creating Kind subclasses.

ToDo:
    Convert Kind registry into a tree for a more complex typing match search.
       
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Iterator, MutableMapping, MutableSequence, Sequence, 
    Set)
import copy
import dataclasses
import datetime
import functools
import inspect
from typing import (
    Any, Callable, ClassVar, Optional, Type, TypeVar, Union, get_type_hints)

import denovo

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
            the types (and Kinds) stored in 'denovo.framework.Kind.registry'.
    
    Attributes:
        wrapped (denovo.alias.Wrappable): wrapped class or function.
        registry (dict[str, denovo.alias.Operation]): registry for different 
            functions that may be called based on the first parameter's type. 
            Defaults to an empty dict.
        
    """
    wrapped: denovo.alias.Wrappable
    registry: dict[str, denovo.alias.Operation] = dataclasses.field(
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
        
    def __call__(self, *args: Any, **kwargs: Any) -> denovo.alias.Operation:
        """Returns wrapped object with args and kwargs"""
        return self.dispatch(*args, **kwargs)

    """ Public Methods """
      
    def dispatch(self, *args: Any, **kwargs: Any) -> denovo.alias.Operation:
        """[summary]

        Args:
            source (Any): [description]

        Returns:
            denovo.alias.Operation: [description]
            
        """
        if args:
            item = args[0]
        else:
            item = list(kwargs.values())[0]
        key = denovo.framework.identify(item = item)
        return self.registry[key](*args, **kwargs)
    
    def register(self, wrapped: denovo.alias.Operation) -> None:
        """[summary]

        Args:
            wrapped (denovo.alias.Operation): [description]

        Returns:
            denovo.alias.Operation: [description]
            
        """
        _, annotation = next(iter(get_type_hints(wrapped).items()))
        print('test annot', annotation)
        key = denovo.framework.identify(item = annotation)
        print('test key', key)
        self.registry[key] = wrapped
        return
