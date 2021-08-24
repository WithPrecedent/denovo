"""
checks: typing check functions
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:    
    is_iterable (Callable): returns whether an item is iterable but not a str.
    is_nested (Callable): returns whether a dict or dict-like item is nested.
    is_property (Callable): returns whether an attribute is actually a property.

        
ToDo:

"""
from __future__ import annotations
import collections.abc
import datetime
import inspect
import pathlib
import re
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, Mapping, 
                    MutableMapping, MutableSequence, Optional, Sequence, Type, 
                    Union)

import more_itertools

import denovo


""" Class and Object Check Tools """
         
def has_methods(item: Union[object, Type[Any]], 
                methods: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'methods' which are methods."""
    methods = denovo.typing.listify(item = methods)
    return all(denovo.tools.is_method(item = item, attribute = m) 
               for m in methods)

def has_properties(item: Union[object, Type[Any]], 
                   properties: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'properties' which are properties."""
    properties = denovo.typing.listify(item = properties)
    return all(denovo.tools.is_property(item = item, attribute = p) 
               for p in properties)
 
def is_iterable(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is iterable and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__    
    return (issubclass(item, collections.abc.Iterable) 
            and not issubclass(item, str))

def is_nested(dictionary: collections.abc.Mapping[Any, Any]) -> bool:
    """Returns if passed 'contents' is nested at least one-level."""
    return any(isinstance(v, collections.abc.Mapping) 
               for v in dictionary.values())

def is_subclass(item: Type[Any],
                attributes: Optional[list[str]] = None,
                methods: Optional[list[str]] = None,
                properties: Optional[list[str]] = None) -> bool:
    """Returns if 'item' has 'attributes', 'methods' and 'properties'."""
    attributes = attributes or []
    methods = methods or []
    properties = properties or []
    return (all(hasattr(item, a) for a in attributes)
            and has_methods(item = item, methods = methods)
            and has_properties(item = item, properties = properties))
    