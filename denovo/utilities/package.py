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
from typing import Any, Optional, Type, Union

import denovo


""" Introspection Tools """

@dataclasses.dataclass
class Package(object):
    """Interface for storing package information from 'folder'.
    
    """
    folder: Union[pathlib.Path, str]
    include_subfolders: bool = True

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        self.folder = denovo.convert.pathlibify(item = self.folder)
    """ Properties """

    @property
    def files(self) -> list[pathlib.Path]:
        return get_file_paths(folder = self.folder, 
                              recursive = self.include_subfolders)

    @property    
    def folders(self) -> list[pathlib.Path]:
        return get_folder_paths(folder = self.folder, 
                                recursive = self.include_subfolders)

    @property          
    def modules(self) -> list[types.ModuleType]:
        return get_modules(folder = self.folder, 
                           recursive = self.include_subfolders)

    @property    
    def paths(self) -> list[pathlib.Path]:
        return get_paths(folder = self.folder, 
                             recursive = self.include_subfolders)

def create_package(folder: Union[str, pathlib.Path], 
                   recursive: bool = False) -> Package:
    """Convenience function to create a Package instance."""
    return Package(folder = folder, include_subfolders = recursive)

def get_file_paths(folder: Union[str, pathlib.Path],
                   recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of modules in 'folder'."""
    paths = get_paths(folder = folder, recursive = recursive)
    files = [p for p in paths if p.is_file()]
    return [f for f in files if f.is_file]

def get_folder_paths(folder: Union[str, pathlib.Path],
                     recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of modules in 'folder'."""
    paths = get_paths(folder = folder, recursive = recursive)
    return [p for p in paths if is_folder(item = p)]

def get_modules(folder: Union[str, pathlib.Path],
                recursive: bool = False) -> list[types.ModuleType]:  
    """Returns list of modules in 'folder'."""
    return [denovo.load.from_path(path = p) # type: ignore
            for p in get_paths(folder = folder, recursive = recursive)]

def get_paths(folder: Union[str, pathlib.Path], 
                  suffix: str = '*',
              recursive: bool = False) -> list[pathlib.Path]:  
    """Returns list of pathlib Paths of all items in 'folder'."""
    folder = denovo.convert.pathlibify(item = folder) 
    if recursive:
        return  list(folder.rglob(f'*.{suffix}')) # type: ignore
    else:
        return list(folder.glob(f'*.{suffix}')) # type: ignore
    
def is_file(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' exists, is a file, and isn't a module."""
    item = denovo.convert.pathlibify(item = item)
    return item.exists() and item.is_file() and not item.suffix in ['.py'] # type: ignore

def is_module(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' exists and is a .py file."""
    item = denovo.convert.pathlibify(item = item)
    return item.exists() and item.is_file() and item.suffix in ['.py'] # type: ignore

def is_folder(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' exists and is a folder."""
    item = denovo.convert.pathlibify(item = item)
    return item.exists() and item.is_dir() # type: ignore

def is_path(item: Union[str, pathlib.Path]) -> bool:
    """Returns whether 'item' path exists."""
    item = denovo.convert.pathlibify(item = item)
    return item.exists() # type: ignore
      
def name_modules(folder: Union[str, pathlib.Path],
                 recursive: bool = False) -> list[str]:  
    """Returns list of str names of modules in 'folder'."""
    kwargs = {'folder': folder, 'suffix': '.py', 'recursive': recursive}
    paths = [p.stem for p in get_paths(**kwargs)] # type: ignore
    return [str(p) for p in paths]
