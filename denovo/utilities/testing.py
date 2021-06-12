"""
testing: functions to make unit testing a little bit easier
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

    
ToDo:

"""
from __future__ import annotations
import inspect
import sys
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo

def get_testables(module: types.ModuleType, 
                  prefix: str = 'test',
                  include_private: bool = False):
    """[summary]

    Args:
        module (types.ModuleType): [description]
        prefix (str, optional): [description]. Defaults to 'test'.
        include_private (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
        
    """
    classes = [m[0] for m in inspect.getmembers(module, inspect.isclass)
               if m[1].__module__ == module.__name__]
    functions = [m[0] for m in inspect.getmembers(module, inspect.isfunction)
                 if m[1].__module__ == module.__name__]
    testables = classes + functions
    testables = [t.lower() for t in testables]
    if not include_private:
        testables = [i for i in testables if not i.startswith('_')]
    testables = denovo.tools.add_prefix(item = testables, prefix = prefix)
    return testables

def is_testable(item: Any) -> bool:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        bool: [description]
        
    """
    return isinstance(item, types.FunctionType) or inspect.isclass(item) 

def run_tests(module: types.ModuleType, 
              testables: MutableSequence[str]) -> None:
    """[summary]

    Args:
        module (types.ModuleType): [description]
        testables (MutableSequence[str]): [description]
        
    """
    for testable in testables:
        try:
            getattr(module, testable)()
        except AttributeError:
            pass
    return

def testify(module_to_test: types.ModuleType,
            testing_module: Union[types.ModuleType, str]) -> None:
    testables = get_testables(module = module_to_test)
    if isinstance(testing_module, str):
        testing_module = sys.modules[testing_module]
    run_tests(testables = testables, module = testing_module)
    return