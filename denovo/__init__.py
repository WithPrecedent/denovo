"""
denovo: a starter kit for python packages
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'denovo'. This 
        dict is needed for the 'from_dict' function which is called by this 
        modules '__getattr__' function.
    
In general, python files in denovo are over-documented to allow beginning
programmers to understand basic design choices that were made. If there is any
area of the documentation that could be made clearer, please don't hesitate to 
email me - I want to ensure the package is as accessible and useful as possible.

ToDo:
    Create stubs for classes to prevent "cannot subclass ... has type Any" 
        errors.
        
"""
__version__ = '0.1.0'

__package__ = 'denovo'

__author__ = 'Corey Rayburn Yung'


import importlib
from typing import Any

# from .files import lazy
# from .utilities import dynamic
# from .describe import unit
# from .utilities import modify
# from .core import base
# from . import core
# from . import describe
# from . import files
# from . import types
# from . import utilities

""" 
denovo imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Hybrid via denovo.core.containers.Hybrid,
    you can just use: denovo.Hybrid
    
They also operate on a lazy importing system. This means that modules are only
imported when first needed. This allows users to only use part of denovo without 
the memory footprint of the entire package. This also avoids some of the 
circular import problems (and the need for solutions to those problems) when the 
package is first initialized. However, this can come at the cost of less than 
clear error messages if your fork of denovo imports classes and objects out of 
order. However, given that python 3.8+ calls almost every import error a 
"circular import," I don't think the error tracebacks are any less confusing in 
denovo. It's possible that this lazy import system will cause trouble for some 
IDEs (such as pycharm) if you choose to fork denovo. However, I have not 
encountered any such issuse using VSCode and its default python linter.

The keys of 'importables' are the attribute names of how users should access
the modules and other items listed in values. 'importables' is necessary for
the lazy importation system used throughout denovo.

"""
importables: dict[str, str] = {
    'core': 'core',
    'describe': 'describe',
    'files': 'files',
    'types': 'types',
    'utilities': 'utilities',
    
    'base': 'core.base',
    'foundry': 'core.foundry',
    
    'module': 'describe.module',
    'package': 'describe.package',
    'recap': 'describe.recap',
    'unit': 'describe.unit',
    
    'configuration': 'files.configuration',
    'filing': 'files.filing',
    'lazy': 'files.lazy',
    
    'containers': 'types.containers',
    'convert': 'types.convert',
    'quirks': 'types.quirks',
    'structures': 'types.structures',
             
    'clock': 'utilities.clock',
    'dynamic': 'utilities.dynamic',
    'modify': 'utilities.modify',
    'observe': 'utilities.observe',
    'test': 'utilities.test',
    }

           
def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them as package attributes.
    
    Args:
        name (str): name of denovo module or item being sought.

    Returns:
        Any: a module or item stored within a module.
        
    """
    package = __package__ or __name__
    key = '.' + importables[name]
    try:
        return importlib.import_module(key, package = package)
    except ModuleNotFoundError:
        item = key.split('.')[-1]
        module_name = key[:-len(item) - 1]
        module = importlib.import_module(module_name, package = package)
        return getattr(module, item)
