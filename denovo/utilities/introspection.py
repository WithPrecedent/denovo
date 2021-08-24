"""
introspection: functions to inspect packages, modules, classes, and objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:    
        
ToDo:

"""
from __future__ import annotations
import inspect
import pathlib
import types
from typing import Any, Type, Union

import denovo


""" Package Introspection Tools """

def get_modules(folder: Union[str, pathlib.Path]) -> list[types.ModuleType]:  
    """Returns list of modules in 'folder'."""
    return [denovo.tools.acquire(file_path = p) 
            for p in get_module_paths(folder = folder)]

def get_module_paths(folder: Union[str, pathlib.Path]) -> list[pathlib.Path]:  
    """Returns list of pathlib Paths of modules in 'folder'."""
    folder = denovo.typing.pathlibify(item = folder)  
    return list(folder.glob('*/*.py'))

def name_modules(folder: Union[str, pathlib.Path]) -> list[str]:  
    """Returns list of str names of modules in 'folder'."""
    return [p.stem for p in get_module_paths(folder = folder)]

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
    
""" Class and Object Introspection Tools """

def get_methods(item: Union[object, Type[Any]], 
                exclude_private: bool = True) -> bool:
    """Returns methods of 'item'."""
    methods = [is_method(item = item, attribute = a) for a in item.__dir__]
    if exclude_private:
        methods = [m for m in methods if not m.__name__.startswith('_')]
    return methods

def name_methods(item: Union[object, Type[Any]], 
                     exclude_private: bool = True) -> bool:
    """Returns method names of 'item'."""
    return [m.__name__ for m in get_methods(item = item, 
                                            exclude_private = exclude_private)]

def get_properties(item: Union[object, Type[Any]], 
                   exclude_private: bool = True) -> bool:
    """Returns properties of 'item'."""
    properties = [is_property(item = item, attribute = a) for a in item.__dir__]
    if exclude_private:
        properties = [p for p in properties if not m.__name__.startswith('_')]
    return properties

def name_properties(item: Union[object, Type[Any]], 
                       exclude_private: bool = True) -> bool:
    """Returns method names of 'item'."""
    return [m.__name__ for m in get_properties(item = item, 
                                               exclude_private = exclude_private)]
    
""" Attribute Introspection Tools """
    
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
    return (isinstance(item, str) and isinstance(attribute, property))
