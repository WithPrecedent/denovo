"""
test: functions to make unit testing a little bit easier
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
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, Mapping, 
                    MutableMapping, MutableSequence, Optional, Sequence, Type, 
                    Union)

import denovo


def get_testers(package: types.ModuleType, 
                folder: Union[str, pathlib.Path], 
                prefix: str = 'test_') -> list[pathlib.Path]:
    """[summary]

    Args:
        package (object): [description]
        folder (Union[str, pathlib.Path]): [description]
        prefix (str): [description]

    Returns:
        list[pathlib.Path]: [description]
        
    """
    name = package.__package__
    testers = denovo.check.name_modules(folder = folder)
    testers = [denovo.convert.pathlibify(t) for t in testers]
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
        imported = denovo.load.from_path(name = target, file_path = tester)
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
                  include_private: bool = False) -> list[str]:
    """Returns list of testing function names based on 'module' and 'prefix'.

    Args:
        module (types.ModuleType): [description]
        prefix (str, optional): [description]. Defaults to 'test'.
        include_private (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
        
    """
    classes = denovo.module.name_classes(module = module)
    functions = denovo.module.name_functions(module = module)
    testables = classes + functions
    testables = [t.lower() for t in testables]
    if not include_private:
        testables = [i for i in testables if not i.startswith('_')]
    testables = denovo.modify.add_prefix(item = testables, prefix = prefix)
    testables.append('test_all')
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
    """Automated unit tester for an entire python package.
    
    Args:
        package (object): the package to create and run unit tests for. Defaults
            to 'denovo' package.
        folder (Union[str, pathlib.Path]): folder where the unit test files are
            located. Defaults to None.
        prefix (str): prefix for the file names of the unit test files. Defaults
            to 'test_' string.
        
    Attributes:
        report (Union[str, pathlib.Path]): log report of testing listing which
            tests were performed, which were skipped, any errors in testing,
            and other information.
            
    To Do:
        report: add method and support for it in the 'testify' method. 
        
    """
    package: types.ModuleType = denovo
    folder: Optional[Union[str, pathlib.Path]] = None
    prefix: str = 'test_'
    
    """ Initialization Methods """
    
    def __call__(cls, *args: Any, **kwargs: Any) -> None:
        """Instances the class and calls testify method.
        
        Returns:
            Callable: 'testify' method based on args and kwargs.
            
        """
        instance  = cls(*args, **kwargs)
        return instance.testify()
    
    """ Public Methods """
    
    def testify(self, 
                package: types.ModuleType = None, 
                folder: Optional[Union[str, pathlib.Path]] = None,
                prefix: Optional[str] = None) -> None:
        """Calls testing methods for an entire package.
        
        Args:
            package (object): the package to create and run unit tests for. 
                Defaults to None, which will use the class instance attribute.
            folder (Union[str, pathlib.Path]): folder where the unit test files 
                are located.  Defaults to None, which will use the class 
                instance attribute.
            prefix (str): prefix for the file names of the unit test files. 
                 Defaults to None, which will use the class instance attribute.
            
        """
        package = package or self.package
        folder = folder or self.folder
        prefix = prefix or self.prefix
        testers = get_testers(package = package, 
                              folder = folder, 
                              prefix = prefix)
        run_testers(testers = testers, 
                    package = package, 
                    prefix = prefix)
        return
    