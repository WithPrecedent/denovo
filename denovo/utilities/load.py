"""
load: lazy importing utilities
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importify (Callable): lazy loader that accepts import and file paths to load
        individual items from them.
    from_path (Callable): lazy loader from a file path.
    load (Callable): lazy loader that intelligently imports from either a
        file path or import path.
    from_dict (Callable): function which imports items only when such modules 
        and items are first accessed based on a dict.
    # Importer (object): descriptor which adds the functionality of 'from_dict' to
    #     a class.
    
ToDo:

"""
from __future__ import annotations
import dataclasses
import importlib
from importlib import util
import pathlib
import sys
import types
from typing import Any, ClassVar, MutableMapping, Optional, Union


""" Conversion Tools """

def file_to_module(path: Union[pathlib.Path, str], 
                   name: Optional[str] = None) -> types.ModuleType:
    """[summary]

    Args:
        path (Union[pathlib.Path, str]): [description]
        name (Optional[str], optional): [description]. Defaults to None.

    Raises:
        ImportError: [description]

    Returns:
        types.ModuleType: [description]
        
    """
    if isinstance(path, str):
        path = pathlib.Path(path)
    if name is None:
        name = path.stem
    try:
        spec = util.spec_from_file_location(name, path)
        imported = util.module_from_spec(spec) # type: ignore
        sys.modules[name] = imported
        spec.loader.exec_module(imported) # type: ignore
    except (ImportError, AttributeError):
        raise ImportError(f'Failed to import {name} from {path}')  
    return imported  
        
def import_to_module(module: str, 
                     package: Optional[str] = None) -> types.ModuleType:
    """[summary]

    Args:
        module (str): [description]
        package (Optional[str], optional): [description]. Defaults to None.

    Returns:
        types.ModuleType: [description]
        
    """
    if package is None:
        imported = importlib.import_module(module)
    else:
        try:
            imported = importlib.import_module('.' + module, package = package)
        except (AttributeError, ImportError):
            imported = importlib.import_module(module, package = package)
    return imported        

""" Importing Tools """
 
def from_dict(name: str, 
              importables: MutableMapping[str, str]) -> Any:
    """Lazily imports modules and items within them.
    
    Lazy importing means that modules are only imported when they are first
    accessed. This can save memory and keep namespaces decluttered.
    
    This code is adapted from PEP 562: https://www.python.org/dev/peps/pep-0562/
    which outlines how the decision to incorporate '__getattr__' functions to 
    modules allows lazy loading. Rather than place this function solely within
    '__getattr__', it is included here seprately so that it can easily be called 
    by '__init__.py' files throughout denovo and by users (as 
    'denovo.load.from_dict').
    
    To effectively use 'from_dict' in an '__init__.py' file, the user needs to 
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
        package, module, item = _parse_import_path(path = importables[name])
        return from_import(package = package, module = module, item = item) 
    else:
        raise AttributeError(f'{name} is not in importables')   

def from_file(path: Union[str, pathlib.Path],
              name: Optional[str] = None, 
              item: Optional[str] = None) -> Any: 
    """[summary]

    Args:
        path (Union[str, pathlib.Path]): [description]
        name (Optional[str], optional): [description]. Defaults to None.
        item (Optional[str], optional): [description]. Defaults to None.

    Raises:
        ImportError: [description]

    Returns:
        Any: [description]
        
    """
    imported = file_to_module(path = path, name = name)
    if item:
        return getattr(imported, item)
    else:
        return imported
 
def from_import(package: Optional[str], 
                module: str, 
                item: Optional[str] = None) -> Any: 
    """[summary]

    Args:
        path (str): [description]

    Returns:
        Any: [description]
        
    """
    print('test p, m, i', package, module, item)
    if (module in sys.modules
            and isinstance(module, str) 
            and isinstance(item, str)):
        imported = sys.modules[module]
        imported = getattr(imported, item)
    elif (isinstance(package, str) 
            and isinstance(module, str) 
            and isinstance(item, str)):
        try:
            name = '.' + module + '.' + item
            imported = importlib.import_module(name, package = package)
        except (AttributeError, ImportError, ModuleNotFoundError):
            name = '.' + module
            imported = importlib.import_module(name, package = package)
            imported = getattr(imported, item)
    elif package is None and item is None and isinstance(module, str):
        imported = importlib.import_module(module)
    elif (package is None 
          and isinstance(module, str) 
          and isinstance(item, str)):
        try:
            name = '.' + item
            imported =  importlib.import_module(name, package = module)
        except (AttributeError, ImportError, ModuleNotFoundError):  
            name = '.' + module
            imported = importlib.import_module(name)
            imported = getattr(imported, item)
    else:
        raise ValueError(f'Unable to import with passed arguments')
    return imported

def from_path(path: Union[str, pathlib.Path], **kwargs: Any) -> Any:
    """Convenience function that takes either a file or import path.

    Args:
        path (Union[str, pathlib.Path]): [description]

    Raises:
        ValueError: [description]

    Returns:
        types.ModuleType: [description]
        
    """
    if isinstance(path, pathlib.Path) or '\\' in path or '\/' in path:
        imported = from_file(path = path, **kwargs)
    else:
        package, module, item = _parse_import_path(path = path)
        imported = from_import(package = package, module = module, item = item)
    return imported

def importify(item: Optional[str] = None, 
              module: Optional[str] = None, 
              package: Optional[str] = None,
              path: Optional[Union[str, pathlib.Path]] = None) -> Any:
    """Lazily imports 'item'.
    
    If 'path' is passed, the function will import a module at that location
    to 'module' and attempt to import 'item' from it.

    Args:
        item (str): name of object sought.
        module (str): name of module containing the object that is sought.
        package (str): name of packing containing the module that is sought.
        path (pathlib.Path, str): file path where the python module is
            located. Defaults to None.
            
    Raises:
        AttributeError: if 'item' is not found in 'module'.
        ImportError: if no module is found at 'path'.

    Returns:
        Any: imported python object from 'module'.
        
    """
    if path is None:  
        if module is None:
            raise ValueError('path or module must not be None')
        elif package is None:
            imported = importlib.import_module(module)
        else:
            imported = importlib.import_module(module, package = package)
    elif isinstance(path, pathlib.Path) or '\\' in path or '\/' in path:
        imported = from_path(path = path, name = module)
    else:
        package, module, item = _parse_import_path(path = path)
        imported = from_import(package = package, module = module, item = item)
    if item is None:
        return imported
    else:
        return getattr(imported, item)

def _parse_import_path(path: str) -> tuple[Optional[str], 
                                           str, 
                                           Optional[str]]:
    """[summary]

    Args:
        path (str): [description]

    Returns:
        tuple[Optional[str], str, Optional[str]]: [description]
        
    """
    package = item = None
    if '.' in path:
        parts = path.split('.')
        if len(parts) > 2:
            item = parts.pop(-1)
            module = parts.pop(-1)
            package = parts[0]
        # If there are only two parts, it is impossible at this stage to know
        # if the two parts are package/module or module/item. So, any call to 
        # this function should not assume that it is module/item as the returned
        # data might indicate.
        elif len(parts) == 2:
            item = parts.pop(-1)
            module = parts[0]
    else:
        module = path   
    return package, module, item


@dataclasses.dataclass
class Importer(object):
    """Descriptor for lazy importing.
    
    """
    package: str
    importables: MutableMapping[str, str] = dataclasses.field(
        default_factory = dict)
    registry: ClassVar[MutableMapping[str, Importer]] = {}
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        # Stores instance in the class registry.
        self.__class__.registry[self.package] = self
        
    """ Public Methods """
    
    def load(self, 
             path: Optional[str] = None,
             module: Optional[str] = None, 
             item: Optional[str] = None) -> Any:
        """Returns module or item in module based on 'module' and 'item'."""
        if path:
            new_package, new_module, new_item = _parse_import_path(path = path)
            package = new_package or self.package
            module = module or new_module
            item = item or new_item
            return from_import(package = package, module = module, item = item)
        else:
            return from_import(package = self.package, 
                               module = module, # type: ignore
                               item = item)