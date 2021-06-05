"""
tools: denovo utility functions
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


ToDo:


"""
from __future__ import annotations
import collections.abc
import datetime
import importlib
import inspect
import pathlib
import re
import sys
import textwrap
import typing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import more_itertools


NEW_LINE = '\n'
INDENT = '    '


""" Importing Tools """

def fetch(module: str, 
          item: str, 
          file_path: Union[str, pathlib.Path] = None) -> Any:
    """Lazily loads 'item' from 'module'.
    
    If 'file_path' is passed, the function will import a module at that location
    to 'module' and attempt to load 'item' from it.

    Args:
        module (str): name of module holding object that is sought.
        item (str): name of object sought.
        file_path (pathlib.Path, str): file path where the python module is
            located. Defaults to None.
            
    Raises:
        AttributeError: if 'item' is not found in 'module'.
        ImportError: if no module is found at 'file_path'.

    Returns:
        Any: imported python object from 'module'.
        
    """
    if file_path:
        try:
            spec = importlib.util.spec_from_file_location(module, file_path)
            imported = importlib.util.module_from_spec(spec)
            sys.modules[module] = imported
            spec.loader.exec_module(imported)
        except (ImportError, AttributeError):
            raise ImportError(f'failed to load {module} from {file_path}')
        try:
            return getattr(imported, item)
        except AttributeError:
            raise AttributeError(f'failed to load {item} from {imported}')
    try:
        return getattr(importlib.import_module(module), item)
    except (ImportError, AttributeError):
        raise AttributeError(f'failed to load {item} from {module}')

""" Conversion Tools """

# def deannotate(annotation: Any) -> tuple[Any]:
#     """Returns type annotations as a tuple.
    
#     This allows even complicated annotations with Union to be converted to a
#     form that fits with an isinstance call.

#     Args:
#         annotation (Any): type annotation.

#     Returns:
#         tuple[Any]: base level of stored type in an annotation
    
#     """
#     origin = typing.get_origin(annotation)
#     args = typing.get_args(annotation)
#     if origin is Union:
#         return tuple(deannotate(a)[0] for a in args)
#     elif origin is None:
#         return annotation
#     else:
#         return typing.get_args(annotation)
            
def delistify(item: Any, default_value: Any = None) -> Any:
    """Converts a list to a str.

    """
    if item is None:
        if default_value is None or default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(item, MutableSequence):
        return ', '.join(item)
    else:
        return item
    
def instancify(item: Union[Type, object], **kwargs) -> object:
    """Converts 'item' to a class instance with 'kwargs' as parameters.
    
    If 'item' is already an instance, kwargs are added as attributes to the
    existing 'item'.

    Args:
        item (Any): item to create an instance out of.

    Raises:
        TypeError: if 'item' is neither a class nor instance.
        
    Returns:
        object: a class instance with 'kwargs' as attributes.
        
    """         
    if inspect.isclass(item):
        return item(**kwargs)
    elif isinstance(item, object):
        for key, value in kwargs.items():
            setattr(item, key, value)
        return item
    else:
        raise TypeError('item must be a class or class instance')
            
def listify(item: Any, default_value: Any = None) -> List[Any]:
    """Returns passed item as a list (if not already a list).

    Args:
        item (any): item to be transformed into a list to allow proper
            iteration.
        default_value (Any): the default value to return if 'item' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default_value'
            is set to [].

    Returns:
        Sequence[Any]: a passed list, 'item' converted to a list, or 
            'default_value'.

    """
    if item is None:
        if default_value is None:
            return []
        elif default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(item, list) and not isinstance(item, str):
        return item
    else:
        return [item]

def namify(self, item: Any) -> str:
    """Returns hashable representation of 'item'.

    This function returns a hashable name for an item in the following priority
    order:
        1) If 'item' is a str, it is returned.
        2) If 'item' has a 'name' attribute with a hashable value, that is 
            returned.
        3) str() for 'item.
        4) Snakecase '__name__' attribute of 'item'.
        5) Snakecase '__name__' attribute of the '__class__' attribute of 
            'item'.
        
    Args:
        item (Any): item to convert to a str type.

    Returns:
        str: the str used to represent a item.
        
    """        
    if isinstance(item, str):
        return item
    else:
        if hasattr(item, 'name') and isinstance(item.name, Hashable):
            return item.name
        else:
            try:
                return hash(item)
            except (TypeError, AttributeError):
                try:
                    return str(item)
                except TypeError:
                    try:
                        return snakify(item.__name__)
                    except AttributeError:
                        return snakify(item.__class__.__name__)
                    
def numify(item: str, raise_error: bool = False) -> Union[int, float, str]:
    """Converts 'item' to a numeric type.
    
    If 'item' cannot be converted to a numeric type and 'raise_error' is False, 
        'item' is returned as is.

    Args:
        item (str): item to be converted.
        raise_error (bool): whether to raise a TypeError when conversion to a
            numeric type fails (True) or to simply return 'item' (False). 
            Defaults to False.

    Raises:
        TypeError: if 'item' cannot be converted to a numeric type and 
            'raise_error' is True.
            
    Returns
        item (int, float, str) converted to numeric type, if possible.

    """
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            if raise_error:
                raise TypeError('item must be a str that can be converted to a '
                                'numeric type')
            else:
                return item

def pathlibify(path: Union[str, pathlib.Path]) -> pathlib.Path:
    """Converts string 'path' to pathlib.Path object.

    Args:
        path (Union[str, pathlib.Path]): either a string representation of a
            path or a pathlib.Path object.

    Returns:
        pathlib.Path object.

    Raises:
        TypeError if 'path' is neither a str or pathlib.Path type.

    """
    if isinstance(path, str):
        return pathlib.Path(path)
    elif isinstance(path, pathlib.Path):
        return path
    else:
        raise TypeError('path must be str or pathlib.Path type')

def representify(item: Any, package: str = 'denovo') -> str:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        str: [description]
    """
    representation = [f'{NEW_LINE}{package} {item.__class__.__name__}']
    representation.append(f'name: {item.name}')
    attributes = [a for a in item.__dict__ if not a.startswith('_')]
    attributes.remove('name')
    if hasattr(item, 'identification'):
        representation.append(f'identification: {item.identification}')
        attributes.remove('identification')
    for attribute in attributes:
        stored = getattr(item, attribute)
        if isinstance(stored, dict):
            for key, value in stored.items():
                representation.append(
                    textwrap.indent(f'{key}: {value}', INDENT))
        elif isinstance(stored, (list, tuple, set)):
            line = [f'{attribute}:']
            for key in stored:
                line.append(f'{str(key)}')
            representation.append(' '.join(line))
        # elif isinstance(stored, str):
        #     representation.append(item)
        else:
            representation.append(str(stored))
    return NEW_LINE.join(representation)     

def snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): string to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()

def stringify(item: Union[str, Sequence],
              default_null: bool = False,
              default_empty: bool = False) -> str:
    """Converts one item list to a string (if not already a string).

    Args:
        item (str, list): item to be transformed into a string.
        default_null (boolean): whether to return None (True) or ['none']
            (False).

    Returns:
        item (str): either the original str, a string pulled from a
            one-item list, or the original list.

    """
    if item is None:
        if default_null:
            return None
        elif default_empty:
            return []
        else:
            return ['none']
    elif isinstance(item, str):
        return item
    else:
        try:
            return item[0]
        except TypeError:
            return item

def tuplify(item: Any, default_value: Any = None) -> Tuple[Any]:
    """Returns passed item as a tuple (if not already a tuple).

    Args:
        item (Any): item to be transformed into a tuple.
        default_value (Any): the default value to return if 'item' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default_value'
            is set to ().

    Returns:
        tuple[Any]: a passed tuple, 'item' converted to a tuple, or 
            'default_value'.

    """
    if item is None:
        if default_value is None:
            return ()
        elif default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(item, tuple) and not isinstance(item, str):
        return item
    else:
        return tuple(item)
        
def typify(item: str) -> Union[Sequence, int, float, bool, str]:
    """Converts stingsr to appropriate, supported datatypes.

    The method converts strings to list (if ', ' is present), int, float,
    or bool datatypes based upon the content of the string. If no
    alternative datatype is found, the item is returned in its original
    form.

    Args:
        item (str): string to be converted to appropriate datatype.

    Returns:
        item (str, list, int, float, or bool): converted item.

    """
    if not isinstance(item, str):
        return item
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            if item.lower() in ['true', 'yes']:
                return True
            elif item.lower() in ['false', 'no']:
                return False
            elif ', ' in item:
                item = item.split(', ')
                return [numify(item) for item in item]
            else:
                return item

""" Modification Tools """

def add_prefix(item: Union[Mapping[str, Any], Sequence[str]],
               prefix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Adds prefix to each item in a list or keys in a dict.

    An underscore is automatically added after the string prefix.

    Args:
        item (list(str) or dict(str: any)): iterable to be modified.
        prefix (str): prefix to be added.

    Returns:
        list or dict with prefixes added.

    """
    try:
        return {prefix + '_' + k: v for k, v in item.items()}
    except AttributeError:
        return [prefix + '_' + item for item in item]

def add_suffix(item: Union[Mapping[str, Any], Sequence[str]],
               suffix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Adds suffix to each item in a list or keys in a dict.

    An underscore is automatically added after the string suffix.

    Args:
        item (list(str) or dict(str: any)): iterable to be modified.
        suffix (str): suffix to be added.

    Returns:
        list or dict with suffixes added.

    """
    try:
        return {k + '_' + suffix: v for k, v in item.items()}
    except AttributeError:
        return [item + '_' + suffix for item in item]

def datetime_string(prefix: str = None) -> str:
    """Creates a string from current date and time.

    Returns:
        str with current date and time in Y/M/D/H/M format.

    """
    if prefix is None:
        prefix = ''
    time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    return f'{prefix}_{time_string}'

def deduplicate(item: MutableSequence) -> MutableSequence:
    """Deduplicates list or other mutable sequence."""
    if isinstance(item, list):
        return list(dict.fromkeys(item))
    else:
        contents = list(dict.fromkeys(item))
        return item.__class__(contents)

def divide_string(item: str, divider: str = None) -> tuple[str, str]:
    """[summary]

    Args:
        key (str): [description]

    Returns:
        
        tuple[str, str]: [description]
        
    """
    if divider is None:
        divider = '_'
    if divider in item:
        suffix = item.split(divider)[-1]
        prefix = item[:-len(suffix) - 1]
    else:
        prefix = suffix = item
    return prefix, suffix


def drop_prefix(item: Union[Mapping[str, Any], Sequence[str]],
                prefix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Drops prefix from each item in a list or keys in a dict.

    Args:
        item (list(str) or dict(str: any)): iterable to be modified.
        prefix (str): prefix to be dropped

    Returns:
        list or dict with prefixes dropped.

    """
    try:
        return {k.rstrip(prefix): v for k, v in item.items()}
    except AttributeError:
        return [item.rstrip(prefix) for item in item]
    
def drop_suffix(item: Union[Mapping[str, Any], Sequence[str]],
                suffix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Drops suffix from each item in a list or keys in a dict.

    Args:
        item (list(str) or dict(str: any)): iterable to be modified.
        suffix (str): suffix to be dropped

    Returns:
        list or dict with suffixes dropped.

    """
    try:
        return {k.rstrip(suffix): v for k, v in item.items()}
    except AttributeError:
        return [item.rstrip(suffix) for item in item]

def is_item(item: Any) -> bool:
    """Returns if 'item' is iterable but is NOT a str type.

    Args:
        item (Any): object to be tested.

    Returns:
        bool: indicating whether 'item' is iterable but is not a str.

    """
    return (isinstance(item, collections.abc.Iterable) 
            and not isinstance(item, str))

def is_nested(dictionary: Mapping[Any, Any]) -> bool:
    """Returns if passed 'contents' is nested at least one-level.

    Args:
        dictionary (dict): dict to be tested.

    Returns:
        bool: indicating whether any value in the 'contents' is also a
            dict (meaning that 'contents' is nested).

    """
    return any(isinstance(v, dict) for v in dictionary.values())

def is_property(item: Any, instance: object) -> bool:
    """Returns if 'item' is a property of 'instance'.

    Args:
        item (Any): item to test to see if it is a property of 'instance'.
        instance (object): object to see if 'item' is a property of.

    Returns:
        bool: whether 'item' is a property of 'instance'.

    """
    return (isinstance(item, str) 
                and hasattr(instance.__class__, item) 
                and isinstance(getattr(type(instance), item), property))

