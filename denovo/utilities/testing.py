"""
testing: functions to make unit testing a little bit easier
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    how_soon_is_now (Callable): converts a current date and time to a str in the
        format described in the 'TIME_FORMAT' module-level attribute.
    fetch (Callable): lazy loader that accepts import and file paths to load
        individual items from them.
    beautify (Callable): provides a pretty str representation for an object. The
        function uses the 'NEW_LINE' and 'INDENT' module-level attributes for
        the values for new lines and length of an indentation.
    delistify (Callable): converts a list to a str, if it is passed a list.
    instancify (Callable): converts a class to an instance or adds kwargs to a
        passed instance as attributes.
    listify (Callable): converts passed item to a list.
    namify (Callable): returns hashable name for passed item.
    numify (Callable): attempts to convert passed item to a numerical type.
    pathlibify (Callable): converts a str to a pathlib object or leaves it as
        a pathlib object.
    snakify (Callable): converts string to snakecase.
    tuplify (Callable): converts a passed item to a tuple.
    typify (Callable): converts a str type to other common types, if possible.
    add_prefix (Callable): adds a str prefix to each item in a list (or list-
        like item) or each key in a dict (or dict-like item).
    add_suffix (Callable): adds a str suffix to each item in a list (or list-
        like item) or each key in a dict (or dict-like item).
    deduplicate (Callable): removes duplicate items from a list or list-like 
        item.
    divide_string (Callable): divides a str and returns a tuple of str based on
        the first or last appearance of the divider (but drops the divider from 
        the returned str).
    drop_prefix (Callable): removes a str prefix to each item in a list (or 
        list-like item) or each key in a dict (or dict-like item).
    drop_suffix (Callable): removes a str suffix to each item in a list (or 
        list-like item) or each key in a dict (or dict-like item).  
    is_iterable (Callable): returns whether an item is iterable but not a str.
    is_nested (Callable): returns whether a dict or dict-like item is nested.
    is_property (Callable): returns whether an attribute is actually a property.
    
ToDo:

"""
from __future__ import annotations
import collections.abc
import datetime
import importlib
import inspect
import pathlib
import re
import sys
import textwrap
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo

def get_testables(module: types.ModuleType, 
                  prefix: str = 'test',
                  include_private: bool = False):
    classes = [m[0] for m in inspect.getmembers(module, inspect.isclass)
               if m[1].__module__ == module.__name__]
    functions = [m[0] for m in inspect.getmembers(module, inspect.isfunction)
                 if m[1].__module__ == module.__name__]
    testables = classes + functions
    if not include_private:
        testables = [i for i in testables if not i.startswith('_')]
    testables = denovo.tools.add_prefix(item = testables, prefix = prefix)
    return testables

def is_testable(item: Any) -> bool:
    return isinstance(item, types.FunctionType) or inspect.isclass(item) 

def run_tests(module: types.ModuleType, 
              testables: MutableSequence[str]) -> None:
    for testable in testables:
        try:
            getattr(module, testable)()
        except AttributeError:
            pass
    return