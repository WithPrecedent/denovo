"""
module: tools for python modules
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:   
   
ToDo:
    Add functions for getting and naming module-level variables.

"""
from __future__ import annotations

import importlib
from importlib import util
import inspect
import pathlib
import sys
import types
from typing import Any, Optional, Type, Union

import denovo


""" Introspection Tools """
          
def get_classes(module: types.ModuleType, 
                include_private: bool = False) -> list[Type[Any]]:
    """Returns list of classes in 'module'.
    
    Args:
        module (types.ModuleType): module to inspect.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False).
        
    Returns:
        list[Type[Any]]: list of classes in 'module'.
        
    """
    classes = [m[1] for m in inspect.getmembers(module, inspect.isclass)
               if m[1].__module__ == module.__name__]
    if not include_private:
        classes = denovo.modify.drop_privates(item = classes)
    return classes
        
def get_functions(module: types.ModuleType, 
                  include_private: bool = False) -> list[types.FunctionType]:
    """Returns list of functions in 'module'.
    
    Args:
        module (types.ModuleType): module to inspect.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False).
        
    Returns:
        list[Type[types.FunctionType]]: list of functions in 'module'.
        
    """
    functions = [m[1] for m in inspect.getmembers(module, inspect.isfunction)
                 if m[1].__module__ == module.__name__]
    if not include_private:
        functions = denovo.modify.drop_privates(item = functions)
    return functions 
    
def name_classes(module: types.ModuleType, 
                 include_private: bool = False) -> list[str]:
    """Returns list of string names of classes in 'module'.
    
    Args:
        module (types.ModuleType): module to inspect.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False).
        
    Returns:
        list[Type[types.FunctionType]]: list of functions in 'module'.
        
    """
    classes = [m[0] for m in inspect.getmembers(module, inspect.isclass)
               if m[1].__module__ == module.__name__]
    if not include_private:
        classes = denovo.modify.drop_privates(item = classes)
    return classes
       
def name_functions(module: types.ModuleType, 
                   include_private: bool = False) -> list[str]:
    """Returns list of string names of functions in 'module'.
    
    Args:
        module (types.ModuleType): module to inspect.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False).
        
    Returns:
        list[Type[types.FunctionType]]: list of functions in 'module'.
        
    """
    functions = [m[0] for m in inspect.getmembers(module, inspect.isfunction)
                 if m[1].__module__ == module.__name__]
    if not include_private:
        functions = denovo.modify.drop_privates(item = functions)
    return functions 
 
""" Conversion Tools """

def from_file_path(path: Union[pathlib.Path, str], 
                   name: Optional[str] = None) -> types.ModuleType:
    """Imports and returns module from file path at 'name'.

    Args:
        path (Union[pathlib.Path, str]): file path of module to load.
        name (Optional[str]): name to store module at in 'sys.modules'. If it
            is None, the stem of 'path' is used. Defaults to None.
    Returns:
        types.ModuleType: imported module.
        
    """
    if isinstance(path, str):
        path = pathlib.Path(path)
    if name is None:
        name = path.stem
    spec = util.spec_from_file_location(name, path)
    if spec is None:
        raise ImportError(f'Failed to create spec from {path}')
    else:
        return util.module_from_spec(spec)
        
def from_import_path(path: str, name: Optional[str] = None) -> types.ModuleType:
    """Imports and returns module from import path at 'name'.

    Args:
        path (Union[pathlib.Path, str]): import path of module to load.
        name (Optional[str]): name to store module at in 'sys.modules'. If it
            is None, the stem of 'path' is used. Defaults to None.
            
    Returns:
        types.ModuleType: imported module.
        
    """
    if '.' in path:
        parts = path.split('.')
        module = parts.pop(-1)
        package = '.'.join(parts)
        try:
            imported = importlib.import_module(module, package = package)
        except (AttributeError, ImportError, ModuleNotFoundError):
            try:
                imported = importlib.import_module('.' + module, 
                                                   package = package)
            except (AttributeError, ImportError, ModuleNotFoundError):
                imported = importlib.import_module(path)   
    else:
        imported = importlib.import_module(path)
    if name is not None:
        sys.modules[name] = imported
    return imported
    
def from_path(path: Union[str, pathlib.Path], 
              name: Optional[str] = None) -> types.ModuleType:
    """Imports and returns module from import or file path at 'name'.

    Args:
        path (Union[pathlib.Path, str]): import or file path of module to load.
        name (Optional[str]): name to store module at in 'sys.modules'. If it
            is None, the stem of 'path' is used. Defaults to None.
            
    Returns:
        types.ModuleType: imported module.
        
    """
    if isinstance(path, pathlib.Path) or '\\' in path or '\/' in path:
        operation = from_file_path
    else:
        operation = from_import_path # type: ignore
    return operation(path = path, name = name)

""" Private Methods """ 

# def _safe_import(path: str) -> types.ModuleType:
#     print('test path safe', path)
#     if path in sys.modules:
#         return sys.modules[path]
#     else:
#         try:
#             return importlib.import_module(path)
#         except AttributeError:
#             print('test att error')
#             if '.' in path:
#                 parts = path.split('.')
#                 item = parts[-1]
#                 del parts[-1]
#                 new_path = '.' + '.'.join(parts)
#                 module = importlib.import_module(new_path)
#                 return getattr(module, item)
#             else:
#                 raise ImportError(f'{path} could not be imported')

# def _parse_import_path(path: str) -> tuple[Optional[str], Optional[str], str]:
#     package = = None
#     if '.' in path:
#         parts = path.split('.')
#         if len(parts) == 1:
#             module = parts.pop(-1)
#             package = parts[0]
#         # If there are only two parts, it is impossible at this stage to know
#         # if the two parts are package/module or module/item. So, any call to 
#         # this function should not assume that it is module/item as the returned
#         # data might indicate.
#         elif len(parts) > 1:
#             module = parts.pop(-1)
#             package = '.'.join(parts)
#     else:
#         module = path   
#     return package, module
