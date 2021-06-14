"""
testing: functions to make unit testing a little bit easier
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

This module uses labels like 'testify' and 'Testifier' for executing unit tests.
This is consistent with other tools in denovo which use the "-ify" suffix to
create novel, but easily understood, names for various actions. However, in this
instance, those labels might create confusion with the Testify testing framework
which is available here: https://github.com/Yelp/Testify. This project is wholly
unrelated to Testify (which is no longer being updated), but I have chosen to
use similar terminology simply because it fits with the naming structure used
throughout denovo.

Contents:
    get_testables (Callable): generates a list of function names based on the 
        classes and functions in a passed module.
    run_tests (Callable): performs all unit tests on a single module based on 
        the passed 'testables' argument.
    testify (Callable): generates list of testable items in a module and 
        performs all unit tests on that module.
    Testifier (Type, Callable): a callable class which allows for automated 
        testing across an entire package.
    
ToDo:
    Add logger for testing

"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
import sys
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo

def get_testables(module: types.ModuleType, 
                  prefix: str = 'test',
                  include_private: bool = False) -> List[str]:
    """Returns list of testing function names based on 'module' and 'prefix'.

    Args:
        module (types.ModuleType): [description]
        prefix (str, optional): [description]. Defaults to 'test'.
        include_private (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
        
    """
    classes = denovo.tools.get_classes(module = module)
    functions = denovo.tools.get_functions(module = module)
    testables = classes + functions
    testables = [t.lower() for t in testables]
    if not include_private:
        testables = [i for i in testables if not i.startswith('_')]
    testables = denovo.tools.add_prefix(item = testables, prefix = prefix)
    return testables

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
    """[summary]

    Args:
        module_to_test (types.ModuleType): [description]
        testing_module (Union[types.ModuleType, str]): [description]
        
    """
    testables = get_testables(module = module_to_test)
    if isinstance(testing_module, str):
        testing_module = sys.modules[testing_module]
    run_tests(testables = testables, module = testing_module)
    return


@dataclasses.dataclass
class Testifier(object):
    """
    """
    folder: Union[str, pathlib.Path]
    package: str = 'denovo'
    prefix: str = 'test'
    report: Union[str, pathlib.Path] = None
    
    """ Initialization Methods """
    
    def __call__(cls, *args, **kwargs) -> Callable:
        instance  = cls(*args, **kwargs)
        return instance.test()
    
    """ Public Methods """
    
    def test(self) -> None:
        return