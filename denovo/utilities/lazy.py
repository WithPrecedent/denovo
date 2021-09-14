"""
lazy: lazy importing utilities
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
from importlib.machinery import PathFinder
import pathlib
import sys
import types
from typing import Any, ClassVar, MutableMapping, MutableSequence, Optional, Union


""" Importing Tools """
 
def from_importables(name: str, 
                     importables: MutableMapping[str, str],
                     subpackages: MutableSequence[str],
                     package: Optional[str] = None) -> Any:
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
        if importables[name] in sys.modules:
            return sys.modules[importables[name]]
        path = importables[name]
        for sub in subpackages:
            if sub.startswith(path):
                package = sub
                path = '.' + path[len(sub):]
                break   
        return safe_import(path = path, package = package)
    else:
        raise AttributeError(f'{name} is not in importables') 

def safe_import(path: str, package: Optional[str] = None) -> Any:
    """[summary]

    Args:
        path (str): [description]
        package (Optional[str], optional): [description]. Defaults to None.

    Raises:
        ValueError: [description]

    Returns:
        Any: [description]
    """
    if path.startswith('.') and package is None:
        raise ValueError('package cannot be None for relative imports')
    elif not path.startswith('.') and package is not None:
        path = '.' + path
    if package is None:
        kwargs = {}
    else:
        kwargs = {'package': package}
        print('test path package', path, package)
    try: 
        return importlib.import_module(path, **kwargs)
    except (AttributeError, ImportError, ModuleNotFoundError):
        item = path.split('.')[-1]
        new_path = path[:-len(item) - 1]
        print('test new path item', new_path, item)
        if '.' in new_path:
            _ = safe_import(path = new_path, package = package)
        module = importlib.import_module(new_path, **kwargs)
        return getattr(module, item)

    
    
       
    # if name in importables:
    #     if package is None and importables[name].startswith('.'):
    #         raise ValueError('package cannot be None for relative imports')
    #     else:
    #         if package is None:
    #             path = importables[name]
    #         else:
    #             path = '.' + importables[name]
    #         try:
    #             return importlib.import_module()
    #         except ImportError:
    #             if '.' in path:
    #                 print('test path', path)
    #                 parts = path.split('.')
    #                 print('test parts', parts)
    #                 item = parts.pop(-1)
    #                 path = path.removesuffix(item)
    #                 item = item.removeprefix('.')
    #                 path = '.'.join(parts)
    #                 imported = denovo.module.from_import_path(path = path,
    #                                                           name = name)
    #                 return getattr(imported, item)
    #             else:
    #                 raise ImportError(f'{importables[name]} cannot be imported')
    # else:
    #     raise AttributeError(f'{name} is not in importables')   
    
# def importify(item: Optional[str] = None, 
#               module: Optional[str] = None, 
#               package: Optional[str] = None,
#               path: Optional[Union[str, pathlib.Path]] = None) -> Any:
#     """Lazily imports 'item'.
    
#     If 'path' is passed, the function will import a module at that location
#     to 'module' and attempt to import 'item' from it.

#     Args:
#         item (str): name of object sought.
#         module (str): name of module containing the object that is sought.
#         package (str): name of packing containing the module that is sought.
#         path (pathlib.Path, str): file path where the python module is
#             located. Defaults to None.
            
#     Raises:
#         AttributeError: if 'item' is not found in 'module'.
#         ImportError: if no module is found at 'path'.

#     Returns:
#         Any: imported python object from 'module'.
        
#     """
#     if path is None:  
#         if module is None:
#             raise ValueError('path or module must not be None')
#         elif package is None:
#             imported = importlib.import_module(module)
#         else:
#             imported = importlib.import_module(module, package = package)
#     elif isinstance(path, pathlib.Path) or '\\' in path or '\/' in path:
#         imported = from_path(path = path, name = module)
#     else:
#         package, module, item = _parse_import_path(path = path)
#         imported = from_import(package = package, module = module, item = item)
#     if item is None:
#         return imported
#     else:
#         return getattr(imported, item)
    
# def from_file(path: Union[str, pathlib.Path],
#               name: Optional[str] = None, 
#               item: Optional[str] = None) -> Any: 
#     """[summary]

#     Args:
#         path (Union[str, pathlib.Path]): [description]
#         name (Optional[str], optional): [description]. Defaults to None.
#         item (Optional[str], optional): [description]. Defaults to None.

#     Raises:
#         ImportError: [description]

#     Returns:
#         Any: [description]
        
#     """
#     imported = file_to_module(path = path, name = name)
#     if item:
#         return getattr(imported, item)
#     else:
#         return imported
 
# def from_import(package: Optional[str], 
#                 module: str, 
#                 item: Optional[str] = None) -> Any: 
#     """[summary]

#     Args:
#         path (str): [description]

#     Returns:
#         Any: [description]
        
#     """
#     print('test p, m, i', package, module, item)
#     if (module in sys.modules
#             and isinstance(module, str) 
#             and isinstance(item, str)):
#         imported = sys.modules[module]
#         imported = getattr(imported, item)
#     elif (isinstance(package, str) 
#             and isinstance(module, str) 
#             and isinstance(item, str)):
#         try:
#             name = '.' + module + '.' + item
#             imported = importlib.import_module(name, package = package)
#         except (AttributeError, ImportError, ModuleNotFoundError):
#             name = '.' + module
#             imported = importlib.import_module(name, package = package)
#             imported = getattr(imported, item)
#     elif package is None and item is None and isinstance(module, str):
#         imported = importlib.import_module(module)
#     elif (package is None 
#           and isinstance(module, str) 
#           and isinstance(item, str)):
#         try:
#             name = '.' + item
#             imported =  importlib.import_module(name, package = module)
#         except (AttributeError, ImportError, ModuleNotFoundError):  
#             name = '.' + module
#             imported = importlib.import_module(name)
#             imported = getattr(imported, item)
#     else:
#         raise ValueError(f'Unable to import with passed arguments')
#     return imported


""" Class Implementation """

@dataclasses.dataclass
class Importer(object):
    """Descriptor for lazy importing.
    
    """
    package: str
    importables: MutableMapping[str, str] = dataclasses.field(
        default_factory = dict)
    subpackages: MutableSequence[str] = dataclasses.field(
        default_factory = list)
    registry: ClassVar[MutableMapping[str, Importer]] = {}
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        # Stores instance in the class registry.
        self.__class__.registry[self.package] = self
        # Imports subpackages
        self._initialize_subpackages()
        
    """ Public Methods """
    
    def load(self, name: str) -> Any:
        return from_importables(name = name, 
                                importables = self.importables,
                                subpackages = self.subpackages,
                                package = self.package)

    """ Private Methods """

    def _initialize_subpackages(self) -> None:
        """Imports all subpackages."""
        for subpackage in self.subpackages:
            importlib.import_module('.' + subpackage, package = self.package)
        return
        
                    
""" Private Functions """


# def _import_module(module: str, 
#                    package: Optional[str] = None) -> types.ModuleType:
#     if package is None and '.' in module:
#         parts = module.split('.')
#         package = parts.pop[0]
#         new_module = '.'.join(parts)
#         return importlib.import_module(new_module, package = package)
#     elif package is None:
#         return importlib.import_module(module)
#     else:
#         return importlib.import_module(module, package = package)
        
# def _import_parents(module: str, package: str) -> None:
#     if package not in sys.modules:
#         importlib.import_module(package)
#     if '.' in module:
#         parts = module.split('.')
#         to_import = parts.pop[-1]
#         if to_import not in sys.modules:
#             importlib.import_module(to_import, package = package)
#     else:
#         importlib.import_module(module, package)
#     return

         
