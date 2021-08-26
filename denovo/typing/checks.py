"""
checks: typing check functions that return booleans
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
import abc
import collections.abc
import dataclasses
import datetime
import inspect
import pathlib
import re
import types
from typing import Any, ClassVar, Optional, Type, Union

import more_itertools

import denovo


""" Simplified Protocol """

@dataclasses.dataclass
class Kind(abc.ABC):
    
    attributes: ClassVar[list[str]] = []
    methods: ClassVar[list[str]] = []
    properties: ClassVar[list[str]] = []
    signatures: ClassVar[dict[str, inspect.Signature]] = {}
    
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Tests whether 'subclass' has the relevant characteristics."""
        return is_kind(item = subclass,
                       attributes = cls.attributes,
                       methods = cls.methods,
                       properties = cls.properties,
                       signatures = cls.signatures)


""" Package Introspection Tools """

def get_modules(folder: Union[str, pathlib.Path],
                recursive: bool = False) -> list[types.ModuleType]:  
    """Returns list of modules in 'folder'."""
    return [denovo.lazy.acquire(path = p) 
            for p in get_paths(folder = folder, recursive = recursive)]

def get_paths(folder: Union[str, pathlib.Path], 
              suffix: str = 'py',
              recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of pathlib Paths of modules in 'folder'."""
    folder = denovo.converters.pathlibify(item = folder) 
    if recursive:
        return  list(folder.rglob(f'*.{suffix}')) # type: ignore
    else:
        return list(folder.glob(f'*.{suffix}')) # type: ignore

def is_file(file_path: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'file_path' currently exists and is a file."""
    folder = denovo.converters.pathlibify(item = file_path)
    return folder.exists() and folder.is_file() # type: ignore

def is_folder(folder: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'folder' currently exists and is a folder."""
    folder = denovo.converters.pathlibify(item = folder)
    return folder.exists() and folder.is_dir() # type: ignore
    
def name_modules(folder: Union[str, pathlib.Path],
                 recursive: bool = False) -> list[str]:  
    """Returns list of str names of modules in 'folder'."""
    return [p.stem for p in get_paths(folder = folder, recursive = recursive)]

""" Module Introspection Tools """
          
def get_classes(module: types.ModuleType) -> list[Type[Any]]:
    """Returns list of string names of classes in a module."""
    return [m[1] for m in inspect.getmembers(module, inspect.isclass)
            if m[1].__module__ == module.__name__]

def get_functions(module: types.ModuleType) -> list[types.FunctionType]:
    """Returns list of string names of functions in a module."""
    return [m[1] for m in inspect.getmembers(module, inspect.isfunction)
            if m[1].__module__ == module.__name__]

def name_classes(module: types.ModuleType) -> list[str]:
    """Returns list of string names of classes in a module."""
    return [m[0] for m in inspect.getmembers(module, inspect.isclass)
            if m[1].__module__ == module.__name__]
       
def name_functions(module: types.ModuleType) -> list[str]:
    """Returns list of string names of functions in a module."""
    return [m[0] for m in inspect.getmembers(module, inspect.isfunction)
            if m[1].__module__ == module.__name__]
    
""" Class and Object Attributes Checks """

def get_methods(item: Union[object, Type[Any]], 
                exclude_private: bool = True) -> list[types.FunctionType]:
    """Returns methods of 'item'."""
    methods = name_methods(item = item, exclude_private = exclude_private)
    return [getattr(item, m) for m in methods]

def get_properties(item: Union[object, Type[Any]], 
                   exclude_private: bool = True) -> list[Any]:
    """Returns properties of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    properties = name_properties(item = item, exclude_private = exclude_private)
    return [getattr(item, p) for p in properties]
 
def has_methods(item: Union[object, Type[Any]], 
                methods: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'methods' which are methods."""
    methods = denovo.converters.listify(item = methods)
    return all(denovo.tools.is_method(item = item, attribute = m) 
               for m in methods)

def has_properties(item: Union[object, Type[Any]], 
                   properties: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'properties' which are properties."""
    properties = denovo.converters.listify(item = properties)
    return all(denovo.tools.is_property(item = item, attribute = p) 
               for p in properties)

def has_signatures(item: Union[object, Type[Any]], 
                   signatures: dict[str, inspect.Signature]) -> bool:
    """Returns whether 'item' has 'signatures' of its methods."""
    names = name_methods(item = item)
    methods = get_methods(item = item)
    item_signatures = [m.__signature__ for m in methods]
    pass_test = True
    for name, parameters in dict(zip(names, item_signatures)).items():
        if (not hasattr(item, name) 
                or getattr(item, name).__signature__ != parameters):
            pass_test = False
    return pass_test
    
def is_kind(item: Union[object, Type[Any]],
            attributes: Optional[list[str]] = None,
            methods: Optional[list[str]] = None,
            properties: Optional[list[str]] = None,
            signatures: Optional[dict[str, inspect.Signature]] = None) -> bool:
    """Returns if 'item' has 'attributes', 'methods' and 'properties'."""
    if not inspect.isclass(item):
        item = item.__class__ 
    attributes = attributes or []
    methods = methods or []
    properties = properties or []
    signatures = signatures or {}
    if not methods and signatures:
        methods = list(signatures.keys())
    return (all(hasattr(item, a) for a in attributes)
            and has_methods(item = item, methods = methods)
            and has_properties(item = item, properties = properties)
            and has_signatures(item = item, signatures = signatures))

def name_methods(item: Union[object, Type[Any]], 
                 exclude_private: bool = True) -> list[str]:
    """Returns method names of 'item'."""
    methods = [a for a in dir(item)
               if is_method(item = item, attribute = a)]
    if exclude_private:
        methods = [m for m in methods if not m.startswith('_')]
    return methods

def name_properties(item: Union[object, Type[Any]], 
                    exclude_private: bool = True) -> list[str]:
    """Returns method names of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    properties = [a for a in dir(item)
                  if is_property(item = item, attribute = a)]
    if exclude_private:
        properties = [p for p in properties if not p.startswith('_')]
    return properties
    
""" Class and Object Typing Checks """
 
def is_iterable(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is iterable and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__ 
    return (issubclass(item, collections.abc.Iterable)  # type: ignore  
            and not issubclass(item, str)) # type: ignore  

def is_nested(dictionary: collections.abc.Mapping[Any, Any]) -> bool:
    """Returns if passed 'contents' is nested at least one-level."""
    return any(isinstance(v, collections.abc.Mapping) 
               for v in dictionary.values())
 
def is_sequence(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is a sequence and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__ 
    return (issubclass(item, collections.abc.Sequence)  # type: ignore  
            and not issubclass(item, str)) # type: ignore  

""" Attribute Introspection Tools """

def is_classvar(item: Union[object, Type[Any]], 
                attribute: str) -> bool:
    """Returns if 'attribute' is a class attribute of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    return (hasattr(item, attribute)
            and not is_method(item = item, attribute = attribute)
            and not is_property(item = item, attribute = attribute))

def is_method(item: Union[object, Type[Any]], 
              attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a method of 'item'."""
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return inspect.ismethod(attribute)

def is_property(item: Union[object, Type[Any]], 
                attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a property of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return isinstance(attribute, property)
