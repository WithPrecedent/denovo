"""
testing: functions to make unit testing a little bit easier
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

This module uses labels like 'testify' and 'Testimony' for executing unit tests.
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
    Testimony (Type, Callable): a callable class which allows for automated 
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


def get_testers(package: object, 
                folder: Union[str, pathlib.Path], 
                prefix: str = 'test_') -> List[pathlib.Path]:
    """[summary]

    Args:
        package (object): [description]
        folder (Union[str, pathlib.Path]): [description]
        prefix (str): [description]

    Returns:
        List[pathlib.Path]: [description]
        
    """
    name = package.__package__
    testers = denovo.tools.get_modules(folder = folder)
    testers = [t for t in testers if t.name.startswith(prefix)]
    testers = [t for t in testers if t.stem != f'{prefix}{name}']
    return testers

def run_testers(testers: MutableSequence[pathlib.Path],
                package: object,
                prefix: str) -> None:
    """[summary]

    Args:
        testers (MutableSequence[pathlib.Path]): [description]
        package (object): [description]
        prefix (str): [description]
        
    """
    for tester in testers:
        target = tester.stem
        module = denovo.tools.drop_prefix(item = target, prefix = prefix)
        target_module = getattr(package, module)
        imported = denovo.lazy.from_path(name = target, file_path = tester)
        testify(target_module = target_module, testing_module = imported) 
    return

def testify(target_module: types.ModuleType,
            testing_module: Union[types.ModuleType, str]) -> None:
    """[summary]

    Args:
        target_module (types.ModuleType): [description]
        testing_module (Union[types.ModuleType, str]): [description]
        
    """
    testables = get_testables(module = target_module)
    if isinstance(testing_module, str):
        testing_module = sys.modules[testing_module]
    run_tests(testables = testables, module = testing_module)
    return

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
        if hasattr(module, testable):
            getattr(module, testable)()
    return


@dataclasses.dataclass
class Testimony(object):
    """Unit tester for a python package.
    
    Args:

        
    """
    folder: Union[str, pathlib.Path]
    package: object = denovo
    prefix: str = 'test_'
    report: Union[str, pathlib.Path] = None
    
    """ Initialization Methods """
    
    def __call__(cls, *args, **kwargs) -> Callable:
        """
        """
        instance  = cls(*args, **kwargs)
        return instance.testify()
    
    """ Public Methods """
    
    def testify(self) -> None:
        """Calls testing methods for an entire package."""
        testers = get_testers(package = self.package,
                              folder = self.folder,
                              prefix = self.prefix)
        run_testers(testers = testers, 
                    package = self.package, 
                    prefix = self.prefix)
        return
    