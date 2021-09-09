"""
module: tools for python modules
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:   
   
ToDo:


"""
from __future__ import annotations
import dataclasses
import inspect
import types
from typing import Any, Optional, Type, Union

import denovo


""" Introspection Tools """
          
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
