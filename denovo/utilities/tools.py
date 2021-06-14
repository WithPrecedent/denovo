"""
tools: denovo utility functions
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    how_soon_is_now (Callable): converts a current date and time to a str in the
        format described in the 'TIME_FORMAT' module-level attribute.
    beautify (Callable): provides a pretty str representation for an object. The
        function uses the 'NEW_LINE' and 'INDENT' module-level attributes for
        the values for new lines and length of an indentation.
    delistify (Callable): converts a list to a str, if it is passed a list.
    instancify (Callable): converts a class to an instance or adds kwargs to a
        passed instance as attributes.
    listify (Callable): converts passed item to a list.
    namify (Callable): returns hashable name for passed item.
    numify (Callable): attempts to convert passed item to a numerical type.
    pathlibify (Callable): converts a str to a pathlib object or leaves it as
        a pathlib object.
    snakify (Callable): converts string to snakecase.
    tuplify (Callable): converts a passed item to a tuple.
    typify (Callable): converts a str type to other common types, if possible.
    add_prefix (Callable): adds a str prefix to each item in a list (or list-
        like item) or each key in a dict (or dict-like item).
    add_suffix (Callable): adds a str suffix to each item in a list (or list-
        like item) or each key in a dict (or dict-like item).
    deduplicate (Callable): removes duplicate items from a list or list-like 
        item.
    divide_string (Callable): divides a str and returns a tuple of str based on
        the first or last appearance of the divider (but drops the divider from 
        the returned str).
    drop_prefix (Callable): removes a str prefix to each item in a list (or 
        list-like item) or each key in a dict (or dict-like item).
    drop_suffix (Callable): removes a str suffix to each item in a list (or 
        list-like item) or each key in a dict (or dict-like item).  
    is_iterable (Callable): returns whether an item is iterable but not a str.
    is_nested (Callable): returns whether a dict or dict-like item is nested.
    is_property (Callable): returns whether an attribute is actually a property.
    
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
import types
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

""" Module-Level Attributes """

DIVIDER: str = '_'
INDENT: str = '    '
NEW_LINE: str = '\n'
TIME_FORMAT: str = '%Y-%m-%d_%H-%M'

""" General Tools """

def how_soon_is_now(prefix: str = None) -> str:
    """Creates a string from current date and time.

    Args:
        prefix: a prefix to add to the returned str.
        
    Returns:
        str: with current date and time in 'TIME_FORMAT' format.

    """
    time_string = datetime.datetime.now().strftime(TIME_FORMAT)
    if prefix is None:
        return f'{prefix}_{time_string}'
    else:
        return time_string

""" Conversion Tools """

def beautify(item: object, 
             package: str = None, 
             exclude: List[str] = None,
             include_privates: bool = False) -> str:
    """Flexible tool to make prettier str represtentations of objects.

    Args:
        item (object): object to provide a str representation for.
        package (str): name of the package that the item is from. This is 
            entirely optional and defaults to None.

    Returns:
        str: pretty str representation of the object.
        
    """
    package = package or ''
    exclude = exclude or []
    representation = [NEW_LINE]
    representation.append(f'{package} {item.__class__.__name__}')
    print('test start rep', representation)
    attributes = item.__dict__
    if not include_privates:
        attributes = [a for a in attributes if not a.startswith('_')]
    attributes = [a for a in attributes if a not in exclude]
    for attribute in attributes:
        new_line = f'{INDENT}{attribute}:'
        contents = getattr(item, attribute)
        if isinstance(contents, dict):
            for key, value in contents.items():
                
                representation.append(textwrap.indent(f'{key}: {value}', 
                                                      INDENT))
        elif isinstance(contents, (list, tuple, set)):
            
            items = []
            for key in contents:
                items.append(f'{str(key)}')
            items = ', '.join(items)
            new_line = ' '.join([new_line, items])
            representation.append(new_line)
        else:
            representation.append(f'{INDENT}{attribute}: {str(contents)}')
    print('test representation end', representation)
    return NEW_LINE.join(representation)
            
def delistify(item: Any, default_value: Any = None) -> Any:
    """Converts 'item' to a str from a list, if it is a list.
    
    Args:
        item (Any): item to convert to a str from a list if it is a list.
        default_value (Any): value to return if 'item' is equivalent to a null
            value when passed. Defaults to None.
        
    Returns:
        Any: str, if item was a list, None or the default value if a null value
            was passed, or the item as it was passed if there previous two 
            conditions don't appply.

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
    """Returns 'item' as an instance with 'kwargs' as parameters/attributes.
    
    If 'item' is already an instance, kwargs are added as attributes to the
    existing 'item'.

    Args:
        item (Any): item to create an instance out of.

    Raises:
        TypeError: if 'item' is neither a class nor instance.
        
    Returns:
        object: a class instance with 'kwargs' as attributes or passed as 
            parameters (if 'item' is a class).
        
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

def snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): string to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()

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

def deduplicate(item: MutableSequence) -> MutableSequence:
    """Deduplicates list or other mutable sequence."""
    if isinstance(item, list):
        return list(dict.fromkeys(item))
    else:
        contents = list(dict.fromkeys(item))
        return item.__class__(contents)

def divide_string(item: str, 
                  divider: str = None,
                  return_last: bool = True,
                  raise_error: bool = False) -> tuple[str, str]:
    """Divides a str into 2 parts based on divider.

    Args:
        item (str): string to be divided.
        divider (str): str to divide 'item' upon. Defaults to None, in which
            case the function will use 'DIVIDER' as 'divider'.
        return_last (bool): whether to split 'item' upon the first (False) or
            last appearance of 'divider'.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        ValueError: if 'divider' is not in 'item' and 'raise_error' is True.
        
    Returns:
        tuple[str, str]: parts of 'item' on either side of 'divider' unless
            'divider' is not in 'item'.
        
    """
    if divider is None:
        divider = DIVIDER
    if divider in item:
        if return_last:
            suffix = item.split(divider)[-1]
        else:
            suffix = item.split(divider)[0]
        prefix = item[:-len(suffix) - 1]
    elif raise_error:
        raise ValueError(f'{divider} is not in {item}')
    else:
        prefix = suffix = item
    return prefix, suffix

def drop_prefix(item: Union[str, Mapping[str, Any], Sequence[str]],
                prefix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Drops prefix from each item in a list or keys in a dict.

    Args:
        item (list(str) or dict(str: any)): iterable to be modified.
        prefix (str): prefix to be dropped

    Returns:
        list or dict with prefixes dropped.

    """
    if isinstance(item, str):
        if item.startswith(prefix):
            return item[len(prefix):]
        else:
            return item
    else:
        try:
            return {drop_prefix(item = k, prefix = prefix): v 
                    for k, v in item.items()}
        except AttributeError:
            return [drop_prefix(item = i, prefix = prefix) for i in item]
    
def drop_suffix(item: Union[str, Mapping[str, Any], Sequence[str]],
                suffix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Drops suffix from each item in a list or keys in a dict.

    Args:
        item (list(str) or dict(str: any)): iterable to be modified.
        suffix (str): suffix to be dropped

    Returns:
        list or dict with suffixes dropped.

    """
    if isinstance(item, str):
        if item.endswith(suffix):
            return item[len(suffix):]
        else:
            return item
    else:
        try:
            return {drop_suffix(item = k, suffix = suffix): v 
                    for k, v in item.items()}
        except AttributeError:
            return [drop_suffix(item = i, suffix = suffix) for i in item]

def is_iterable(item: Any) -> bool:
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

""" Introspection Tools """

def get_functions(module: types.ModuleType) -> List[str]:
    """Returns list of string names of functions in a module."""
    return [m[0] for m in inspect.getmembers(module, inspect.isfunction)
            if m[1].__module__ == module.__name__]
    
def get_classes(module: types.ModuleType) -> List[Type]:
    """Returns list of string names of classes in a module."""
    return [m[0] for m in inspect.getmembers(module, inspect.isclass)
            if m[1].__module__ == module.__name__]