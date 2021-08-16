"""
denovo: a starter kit for python packages
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'denovo'. This 
        dict is needed for the 'importify' function which is called by this 
        modules '__getattr__' function.

        
In general, python files in denovo are over-documented to allow beginning
programmers to understand basic design choices that were made. If there is any
area of the documentation that could be made clearer, please don't hesitate to 
email me - I want to ensure the package is as accessible as possible.

"""
__version__ = '0.1.0'

__package__ = 'denovo'

__author__ = 'Corey Rayburn Yung'

# from . import core
# from . import typing
# from . import utilities
# from .core import *
# from .typing import *
# from .utilities import *






import abc
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Type, Union)





from .utilities import lazy
from .core import containers
from .typing import types



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
importables: Dict[str, str] = {
    'utilities': 'utilities',
    'converters': 'typing.converters',
    'decorators': 'utilities.decorators',
    'lazy': 'utilities.lazy',
    'memory': 'utilities.memory',
    'summary': 'utilities.summary',
    'testing': 'utilities.testing',
    'tools': 'utilities.tools',
    'containers': 'core.containers',
    'Bunch': 'core.containers.Bunch',
    'Proxy': 'core.containers.Proxy',
    'Manifest': 'core.containers.Manifest',
    'Hybrid': 'core.containers.Hybrid',
    'Lexicon': 'core.containers.Lexicon',
    'Catalog': 'core.containers.Catalog',
    'Library': 'core.containers.Library',
    'quirks': 'core.quirks',
    'Quirk': 'core.quirks.Quirk',
    'configuration': 'core.configuration',
    'settings': 'core.configuration.settings',
    'filing': 'core.filing',
    'Clerk': 'core.filing.Clerk',
    'FileFormat': 'core.filing.FileFormat',
    # 'Keystone': 'core.framework.Keystone',
    # 'create_keystone': 'core.framework.create_keystone',
    # 'Validator': 'core.framework.Validator',
    # 'Converter': 'core.framework.Converter',
    'structures': 'core.structures',
    'Structure': 'core.structures.Structure',
    'Graph': 'core.structures.Graph'}

def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them as package attributes.
    
    Args:
        name (str): name of denovo module or item being sought.

    Returns:
        Any: a module or item stored within a module.
        
    """
    package = __package__ or __name__
    return lazy.importify(name = name, 
                          package = package, 
                          importables = importables)
