"""
lazy: lazy importing utilities
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    fetch (Callable): lazy loader that accepts import and file paths to load
        individual items from them.
    importify (Callable): function which imports items only when such modules 
        and items are first accessed based on a dict.
    Importer (object): descriptor which adds the functionality of 'importify' to
        a class.
    
ToDo:

"""
from __future__ import annotations
import importlib
from importlib import util
import pathlib
import sys
import types
from typing import Any, Optional, Union

""" Importing Tools """

def acquire(path: Union[str, pathlib.Path]) -> Union[type.ModuleType, Any]:
    if isinstance(path, pathlib.Path) or '\\' in path or '\/' in path:
        imported = fetch(file_path = path)
    elif isinstance(path, str):
        if '.' in path:
            parts = path.split('.')
            if len(parts) > 2:
                item = parts.pop(-1)
                module = parts.pop(-1)
                package = parts[0]
            elif len(parts) == 2:
                try:
                    item = parts.pop(-1)
                    module = parts[0]
                    imported =  fetch(item = item, module = module)
                except AttributeError:
                    module = parts.pop(-1)
                    package = parts[0]
                    imported = fetch(module = module, package = package)
        else:
            imported =  fetch(module = path)
    else:
        raise ValueError('path must be a str or pathlib.Path type')
    return imported

def fetch(item: Optional[str] = None, 
          module: Optional[str] = None, 
          package: Optional[str] = None,
          file_path: Optional[Union[str, pathlib.Path]] = None) -> Any:
    """Lazily imports 'item'.
    
    If 'file_path' is passed, the function will import a module at that location
    to 'module' and attempt to import 'item' from it.

    Args:
        item (str): name of object sought.
        module (str): name of module containing the object that is sought.
        package (str): name of packing containing the module that is sought.
        file_path (pathlib.Path, str): file path where the python module is
            located. Defaults to None.
            
    Raises:
        AttributeError: if 'item' is not found in 'module'.
        ImportError: if no module is found at 'file_path'.

    Returns:
        Any: imported python object from 'module'.
        
    """
    if file_path is None:
        if module is None:
            raise ValueError('file_path or module must not be None')
        elif package is None:
            imported = importlib.import_module(module)
        else:
            imported = importlib.import_module(module, package = package)
    else:
        imported = from_path(file_path = file_path, name = module)
    if item is None:
        return imported
    else:
        return getattr(imported, item)
        
def from_path(file_path: Union[str, pathlib.Path],
              name: Optional[str] = None) -> types.ModuleType: 
    """[summary]
    """
    if isinstance(file_path, str):
        file_path = pathlib.Path(file_path)
    if name is None:
        name = file_path.stem
    try:
        spec = util.spec_from_file_location(name, file_path)
        imported = util.module_from_spec(spec) # type: ignore
        sys.modules[name] = imported
        spec.loader.exec_module(imported) # type: ignore
    except (ImportError, AttributeError):
        raise ImportError(f'Failed to import {name} from {file_path}')
    return imported
        
def importify(name: str, package: str, importables: dict[str, str]) -> Any:
    """Lazily imports modules and items within them.
    
    Lazy importing means that modules are only imported when they are first
    accessed. This can save memory and keep namespaces decluttered.
    
    This code is adapted from PEP 562: https://www.python.org/dev/peps/pep-0562/
    which outlines how the decision to incorporate '__getattr__' functions to 
    modules allows lazy loading. Rather than place this function solely within
    '__getattr__', it is included here seprately so that it can easily be called 
    by '__init__.py' files throughout denovo and by users (as 
    'denovo.lazy.importify').
    
    To effectively use 'importify' in an '__init__.py' file, the user needs to 
    pass a 'importables' dict which indicates how users should accesss imported 
    modules and included items. This modules includes an example 'importables' 
    dict and how to easily add this function to a '__getattr__' function.
    
    Instead of limiting its lazy imports to full import paths as the example in 
    PEP 562, this function has 2 major advantages:
        1) It allows importing items within modules and not just modules. The
            function first tries to import 'name' assuming it is a module. But 
            if that fails, it parses the last portion of 'name' and attempts to 
            import the preceding module and then returns the item within it.
        2) It allows import paths that are less than the full import path by
            using the 'importables' dict. 'importables' has keys which are the 
            name of the attribute being sought and values which are the full 
            import path (dropping the leading '.'). 'importables' thus acts as 
            the normal import block in an __init__.py file but insures that all 
            importing is done lazily.
            
    Args:
        name (str): name of module or item within a module.
        package (str): name of package from which the module is sought.
        importables (Dict[str, str]): keys are the access names for items sought
            and values are the import path where the item is actually located.
        
    Raises:
        AttributeError: if there is no module or item matching 'name' im 
            'importables'.
        
    Returns:
        Any: a module or item stored within a module.
        
    """
    if name in importables:
        key = '.' + importables[name]
        try:
            return importlib.import_module(key, package = package)
        except ModuleNotFoundError:
            item = key.split('.')[-1]
            module_name = key[:-len(item) - 1]
            module = importlib.import_module(module_name, package = package)
            return getattr(module, item)
    else:
        raise AttributeError(f'module {package} has no attribute {name}')   


# @dataclasses.dataclass
# class Importer(object):
#     """Descriptor for lazy importing.
    
#     """
#     package: str = None
#     importables: Dict[str, str] = dataclasses.field(default_factory = dict)
    
#     """ Initialization Methods """
    
#     def __set_name__(self, owner: object, name: str) -> None:
#         self.name = name
    
#     """ Dunder Methods """

#     def __get__(self, owner: object, type: Type = None) -> Any:
#         value = owner.__dict__.get(self.name)
#         if (isinstance(value, str) and '.' in value):
#             try:
#                 value = self.fetch(item = value, package = self.package)
#                 owner.__dict__[self.name] = value
#             except ImportError:
#                 pass
#         return value
