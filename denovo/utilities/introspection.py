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
    
""" Class and Object Introspection Tools """

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
