"""
package: tools for packages and file folders
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:   

  
ToDo:


"""
from __future__ import annotations
import dataclasses
import pathlib
import types
from typing import Union

import denovo


""" Package Interface """

@dataclasses.dataclass
class Package(object):
    """Interface for storing package information from 'folder'.
    
    Attributes:
        folder (Union[pathlib.Path, str]): folder for which information should
            be made available.
        include_subfolders (bool): whether to include subfolders in the package.
            Defaults to True. 
            
    """
    folder: Union[pathlib.Path, str]
    include_subfolders: bool = True

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        self.folder = denovo.convert.pathlibify(item = self.folder)
        
    """ Properties """

    @property
    def files(self) -> list[pathlib.Path]:
        """Returns a list of non-python-module file paths in the package.

        Returns:
            list[pathlib.Path]: list of non-python-module file paths.
            
        """
        return get_file_paths(
            folder = self.folder, 
            recursive = self.include_subfolders)

    @property    
    def folders(self) -> list[pathlib.Path]:
        """Returns a list of folder paths in the package.

        Returns:
            list[pathlib.Path]: list of folder paths.
            
        """
        return get_folder_paths(
            folder = self.folder, 
            recursive = self.include_subfolders)

    @property          
    def modules(self) -> list[types.ModuleType]:
        """Returns a list of python modules in the package.

        Returns:
            list[types.ModuleType]: list of python modules.
            
        """
        return get_modules(
            folder = self.folder, 
            recursive = self.include_subfolders)

    @property
    def module_lookup(self) -> dict[str, types.ModuleType]:
        """Returns a dict of python module names and modules.

        Returns:
            dict[str, types.ModuleType]: dict with str key names of python 
                modules and values as the corresponding modules.
            
        """
        return dict(zip(self.module_names, self.modules))     
        
    @property          
    def module_names(self) -> list[str]:
        """Returns a list of python-module names in the package.

        Returns:
            list[str]: list of python-module names.
            
        """
        return name_modules(
            folder = self.folder, 
            recursive = self.include_subfolders)
        
    @property          
    def module_paths(self) -> list[pathlib.Path]:
        """Returns a list of python-module file paths in the package.

        Returns:
            list[pathlib.Path]: list of python-module file paths.
            
        """
        return get_module_paths(
            folder = self.folder, 
            recursive = self.include_subfolders)  
              
    @property    
    def paths(self) -> list[pathlib.Path]:
        """Returns a list of all paths in the package.

        Returns:
            list[pathlib.Path]: list of all paths.
            
        """
        return get_paths(
            folder = self.folder, 
            recursive = self.include_subfolders)

def create_package(
    folder: Union[str, pathlib.Path], 
    include_subfolders: bool = False) -> Package:
    """Convenience function to create a Package instance.
    
    Args:
        folder (Union[pathlib.Path, str]): folder for which information should
            be made available.
        include_subfolders (bool): whether to include subfolders in the package.
            Defaults to True. 
            
    """
    return Package(folder = folder, include_subfolders = include_subfolders)

""" Introspection Tools """

def get_file_paths(
    folder: Union[str, pathlib.Path],
    recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of non-python module file paths in 'folder'.
    
    Args:
        folder (Union[str, pathlib.Path]): path of folder to examine.
        recursive (bool): whether to include subfolders. Defaults to False.
        
    Returns
        list[pathlib.Path]: a list of file paths in 'folder'.
        
    """
    paths = get_paths(folder = folder, recursive = recursive)
    files = [p for p in paths if p.is_file()]
    return [f for f in files if f.is_file]

def get_folder_paths(
    folder: Union[str, pathlib.Path],
    recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of folder paths in 'folder'.
    
    Args:
        folder (Union[str, pathlib.Path]): path of folder to examine.
        recursive (bool): whether to include subfolders. Defaults to False.
        
    Returns
        list[pathlib.Path]: a list of folder paths in 'folder'.
        
    """
    paths = get_paths(folder = folder, recursive = recursive)
    return [p for p in paths if is_folder(item = p)]

def get_module_paths(
    folder: Union[str, pathlib.Path],
    recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of python module paths in 'folder'.
    
    Args:
        folder (Union[str, pathlib.Path]): path of folder to examine.
        recursive (bool): whether to include subfolders. Defaults to False.
        
    Returns
        list[pathlib.Path]: a list of python module paths in 'folder'.
        
    """
    paths = get_paths(folder = folder, recursive = recursive)
    return [p for p in paths if is_module(item = p)]

def get_modules(
    folder: Union[str, pathlib.Path],
    recursive: bool = False) -> list[types.ModuleType]:  
    """Returns list of python modules in 'folder'.
    
    Args:
        folder (Union[str, pathlib.Path]): path of folder to examine.
        recursive (bool): whether to include subfolders. Defaults to False.
        
    Returns
        list[types.ModuleType]: a list of python modules in 'folder'.
        
    """
    return [denovo.load.from_path(path = p)
            for p in get_paths(folder = folder, recursive = recursive)]

def get_paths(
    folder: Union[str, pathlib.Path], 
    suffix: str = '*',
    recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of all paths in 'folder'.
    
    Args:
        folder (Union[str, pathlib.Path]): path of folder to examine.
        suffix (str): file suffix to match. Defaults to '*' (all file suffixes). 
        recursive (bool): whether to include subfolders. Defaults to False.
        
    Returns
        list[pathlib.Path]: a list of all paths in 'folder'.
        
    """
    folder = denovo.convert.pathlibify(item = folder) 
    if recursive:
        return  list(folder.rglob(f'*.{suffix}')) # type: ignore
    else:
        return list(folder.glob(f'*.{suffix}')) # type: ignore
    
def is_file(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' is a non-python-module file.
    
    Args:
        item (Union[str, pathlib.Path]): path to check.
        
    Returns
        bool: whether 'item' is a non-python-module file.
        
    """
    item = denovo.convert.pathlibify(item = item)
    return item.exists() and item.is_file() and not item.suffix in ['.py'] # type: ignore

def is_module(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' is a python-module file.
    
    Args:
        item (Union[str, pathlib.Path]): path to check.
        
    Returns
        bool: whether 'item' is a python-module file.
        
    """
    item = denovo.convert.pathlibify(item = item)
    return item.exists() and item.is_file() and item.suffix in ['.py'] # type: ignore

def is_folder(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' is a path to a folder.
    
    Args:
        item (Union[str, pathlib.Path]): path to check.
        
    Returns
        bool: whether 'item' is a path to a folder.
        
    """
    item = denovo.convert.pathlibify(item = item)
    return item.exists() and item.is_dir() # type: ignore

def is_path(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' is a currently existing path.
    
    Args:
        item (Union[str, pathlib.Path]): path to check.
        
    Returns
        bool: whether 'item' is a currently existing path.
        
    """
    item = denovo.convert.pathlibify(item = item)
    return item.exists() # type: ignore
      
def name_modules(
    folder: Union[str, pathlib.Path],
    recursive: bool = False) -> list[str]:  
    """Returns list of python module names in 'folder'.
    
    Args:
        folder (Union[str, pathlib.Path]): path of folder to examine.
        recursive (bool): whether to include subfolders. Defaults to False.
        
    Returns
        list[str]: a list of python module names in 'folder'.
        
    """
    kwargs = {'folder': folder, 'suffix': '.py', 'recursive': recursive}
    paths = [p.stem for p in get_paths(**kwargs)] # type: ignore
    return [str(p) for p in paths]
