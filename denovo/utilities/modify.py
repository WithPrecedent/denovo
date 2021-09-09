"""
modifiers: functions that modify stored data without changing the data type
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Adders:
        add_prefix (Callable, dispatcher): adds a str prefix to item.
        add_suffix (Callable, dispatcher): adds a str suffix to item.
    Dividers:
        cleave (Callable, dispatcher): divides an item into 2 parts based on
            'divider'.
        separate (Callable, dispatcher): divides an item into n+1 parts based on
            'divider'.
    Subtractors:
        deduplicate (Callable, dispatcher): removes duplicate data from an item.
        drop_prefix (Callable, dispatcher): removes a str prefix from an item.
        drop_substring (Callable, dispatcher): removes a substring from an item.
        drop_suffix (Callable, dispatcher): removes a str suffix from an item.
    Other: 
        capitalify (Callable): converts a snake case str to capital case.
        snakify (Callable): converts a capital case str to snake case.
        
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
import re
from typing import Any

import denovo


""" Adders """

@denovo.decorators.dispatcher 
def add_prefix(item: Any, prefix: str, divider: str = '') -> Any:
    """Adds 'prefix' to 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')
 
@add_prefix.register # type: ignore
def add_prefix(item: str, prefix: str, divider: str = '') -> str:
    """Adds 'prefix' to 'item' with 'divider' in between."""
    return divider.join([prefix, item])
 
@add_prefix.register # type: ignore
def add_prefix(item: Mapping[str, Any], 
               prefix: str, 
               divider: str = '') -> Mapping[str, Any]:
    """Adds 'prefix' to keys in 'item' with 'divider' in between."""
    contents = {add_prefix(item = k, prefix = prefix, divider = divider): v 
                for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)
 
@add_prefix.register # type: ignore
def add_prefix(item: Sequence[str], 
               prefix: str, 
               divider: str = '') -> Sequence[str]:
    """Adds 'prefix' to items in 'item' with 'divider' in between."""
    contents = [add_prefix(item = i, prefix = prefix, divider = divider) 
                for i in item]
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)
 
@add_prefix.register # type: ignore
def add_prefix(item: Set[str], 
               prefix: str, 
               divider: str = '') -> Set[str]:
    """Adds 'prefix' to items in 'item' with 'divider' in between."""
    contents = {add_prefix(item = i, prefix = prefix, divider = divider) 
                for i in item}
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@add_prefix.register # type: ignore
def add_prefix(item: tuple[str, ...], 
               prefix: str, 
               divider: str = '') -> tuple[str, ...]:
    """Adds 'prefix' to items in 'item' with 'divider' in between."""
    return tuple([add_prefix(item = i, prefix = prefix, divider = divider) 
                  for i in item])

@denovo.decorators.dispatcher 
def add_suffix(item: Any, suffix: str, divider: str = '') -> Any:
    """Adds 'suffix' to 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        suffix (str): suffix to be added to 'item'.
        divider (str): str to add between 'item' and 'suffix'. Defaults to '',
            which means no divider will be added.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')
 
@add_suffix.register # type: ignore
def add_suffix(item: str, suffix: str, divider: str = '') -> str:
    """Adds 'suffix' to 'item' with 'divider' in between."""
    return divider.join([item, suffix])
 
@add_suffix.register # type: ignore
def add_suffix(item: Mapping[str, Any], 
               suffix: str, 
               divider: str = '') -> Mapping[str, Any]:
    """Adds 'suffix' to keys in 'item' with 'divider' in between."""
    contents = {add_suffix(item = k, suffix = suffix, divider = divider): v 
                for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)
 
@add_suffix.register # type: ignore
def add_suffix(item: Sequence[str], 
               suffix: str, 
               divider: str = '') -> Sequence[str]:
    """Adds 'suffix' to items in 'item' with 'divider' in between."""
    contents = [add_suffix(item = i, suffix = suffix, divider = divider) 
                for i in item]
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)
 
@add_suffix.register # type: ignore
def add_suffix(item: Set[str], 
               suffix: str, 
               divider: str = '') -> Set[str]:
    """Adds 'suffix' to items in 'item' with 'divider' in between."""
    contents = {add_suffix(item = i, suffix = suffix, divider = divider) 
                for i in item}
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@add_suffix.register # type: ignore
def add_suffix(item: tuple[str, ...], 
               suffix: str, 
               divider: str = '') -> tuple[str, ...]:
    """Adds 'suffix' to items in 'item' with 'divider' in between."""
    return tuple([add_suffix(item = i, suffix = suffix, divider = divider) 
                  for i in item])

""" Dividers """

@denovo.decorators.dispatcher
def cleave(item: Any, 
           divider: Any,
           return_last: bool = True,
           raise_error: bool = False) -> tuple[Any, Any]:
    """Divides 'item' into 2 parts based on 'divider'.

    Args:
        item (Any): item to be divided.
        divider (Any): item to divide 'item' upon.
        return_last (bool): whether to split 'item' upon the first (False) or
            last appearance of 'divider'.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        TypeError: if no registered function supports the type of 'item'. 
        ValueError: if 'divider' is not in 'item' and 'raise_error' is True.
        
    Returns:
        tuple[Any, Any]: parts of 'item' on either side of 'divider' unless
            'divider' is not in 'item'.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@cleave.register # type: ignore
def cleave(item: str, 
           divider: str = '_',
           return_last: bool = True,
           raise_error: bool = False) -> tuple[str, str]:
    """Divides 'item' into 2 parts based on 'divider'"""
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

@denovo.decorators.dispatcher
def separate(item: Any, 
             divider: Any,
             raise_error: bool = False) -> tuple[Any, ...]:
    """Divides 'item' into n+1 parts based on 'divider'.

    Args:
        item (Any): item to be divided.
        divider (Any): item to divide 'item' upon.
        raise_error (bool): whether to raise an error if 'divider' is not in 
            'item' or to return a tuple containing 'item' twice.

    Raises:
        TypeError: if no registered function supports the type of 'item'. 
        ValueError: if 'divider' is not in 'item' and 'raise_error' is True.
        
    Returns:
        tuple[Any, ...]: parts of 'item' on either side of 'divider' unless
            'divider' is not in 'item'.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@separate.register # type: ignore
def separate(item: str, 
             divider: str = '_',
             raise_error: bool = False) -> tuple[Any, ...]:
    """Divides 'item' into n+1 parts based on 'divider'"""
    if divider in item:
        return item.split(divider)
    elif raise_error:
        raise ValueError(f'{divider} is not in {item}')
    else:
        return tuple([item])
 
""" Subtractors """

@denovo.decorators.dispatcher
def deduplicate(item: Any) -> Any:
    """Deduplicates contents of 'item.
    
    Args:
        item (Any): item to deduplicate.

    Raises:
        TypeError: if no registered function supports the type of 'item'.     
        
    Returns:
        Any: deduplicated item.
        
    """
    raise TypeError(f'item is not a supported type for {__name__}')

@deduplicate.register # type: ignore
def deduplicate(item: Sequence[Any]) -> Sequence[Any]:
    """Deduplicates contents of 'item."""
    contents = list(dict.fromkeys(item))
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__(contents)
        return vessel(contents)

@deduplicate.register # type: ignore
def deduplicate(item: tuple[Any, ...]) -> tuple[Any, ...]:
    """Deduplicates contents of 'item."""
    return tuple(list(dict.fromkeys(item)))
    
@denovo.decorators.dispatcher
def drop_prefix(item: Any, prefix: str, divider: str = '') -> Any:
    """Drops 'prefix' from 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
            
    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_prefix.register # type: ignore
def drop_prefix(item: str, prefix: str, divider: str = '') -> str:
    """Drops 'prefix' from 'item' with 'divider' in between."""
    prefix = ''.join([prefix, divider])
    if item.startswith(prefix):
        return item[len(prefix):]
    else:
        return item

@drop_prefix.register # type: ignore
def drop_prefix(item: Mapping[str, Any], 
                prefix: str, 
                divider: str = '') -> Mapping[str, Any]:
    """Drops 'prefix' from keys in 'item' with 'divider' in between."""
    contents = {drop_prefix(item = k, prefix = prefix, divider = divider): v
                for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_prefix.register # type: ignore
def drop_prefix(item: Sequence[str], 
                prefix: str, 
                divider: str = '') -> Sequence[str]:
    """Drops 'prefix' from items in 'item' with 'divider' in between."""
    contents = [drop_prefix(item = i, prefix = prefix, divider = divider) 
                for i in item] 
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_prefix.register # type: ignore
def drop_prefix(item: Set[str], prefix: str, divider: str = '') -> Set[str]:
    """Drops 'prefix' from items in 'item' with 'divider' in between."""
    contents = {drop_prefix(item = i, prefix = prefix, divider = divider) 
                for i in item}   
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)   

@drop_prefix.register # type: ignore
def drop_prefix(item: tuple[str, ...], 
                prefix: str, 
                divider: str = '') -> tuple[str, ...]:
    """Drops 'prefix' from items in 'item' with 'divider' in between."""
    return tuple([drop_prefix(item = i, prefix = prefix, divider = divider) 
                  for i in item])       
    
@denovo.decorators.dispatcher
def drop_substring(item: Any, substring: str) -> Any:
    """Drops 'substring' from 'item' with a possible 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        substring (str): substring to be added to 'item'.
            
    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_substring.register # type: ignore
def drop_substring(item: str, substring: str) -> str:
    """Drops 'substring' from 'item'."""
    if substring in item:
        return item.replace(substring, '')
    else:
        return item

@drop_substring.register # type: ignore
def drop_substring(item: Mapping[str, Any], substring: str) -> Mapping[str, Any]:
    """Drops 'substring' from keys in 'item'."""
    contents = {drop_substring(item = k, substring = substring): v
                for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_substring.register # type: ignore
def drop_substring(item: Sequence[str], substring: str) -> Sequence[str]:
    """Drops 'substring' from items in 'item'."""
    contents = [drop_substring(item = i, substring = substring) for i in item] 
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_substring.register # type: ignore
def drop_substring(item: Set[str], substring: str) -> Set[str]:
    """Drops 'substring' from items in 'item'."""
    contents = {drop_substring(item = i, substring = substring) for i in item}   
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)   

@drop_substring.register # type: ignore
def drop_substring(item: tuple[str, ...], substring: str) -> tuple[str, ...]:
    """Drops 'substring' from items in 'item'."""
    return tuple([drop_substring(item = i, substring = substring) 
                  for i in item])    
     
@denovo.decorators.dispatcher
def drop_suffix(item: Any, suffix: str, divider: str = '') -> Any:
    """Drops 'suffix' from 'item' with 'divider' in between.
    
    Args:
        item (Any): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Raises:
        TypeError: if no registered function supports the type of 'item'.
        
    Returns:
        Any: modified item.

    """
    raise TypeError(f'item is not a supported type for {__name__}')

@drop_suffix.register # type: ignore
def drop_suffix(item: str, suffix: str, divider: str = '') -> str:
    """Drops 'suffix' from 'item' with 'divider' in between."""
    suffix = ''.join([suffix, divider])
    if item.endswith(suffix):
        return item[:len(suffix)]
    else:
        return item

@drop_suffix.register # type: ignore
def drop_suffix(item: Mapping[str, Any], 
                suffix: str, 
                divider: str = '') -> Mapping[str, Any]:
    """Drops 'suffix' from keys in 'item' with 'divider' in between."""
    contents = {drop_suffix(item = k, suffix = suffix, divider = divider): v
                for k, v in item.items()}
    if isinstance(item, dict):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_suffix.register # type: ignore
def drop_suffix(item: Sequence[str], 
                suffix: str, 
                divider: str = '') -> Sequence[str]:
    """Drops 'suffix' from items in 'item' with 'divider' in between."""
    contents = [drop_suffix(item = i, suffix = suffix, divider = divider) 
                for i in item]
    if isinstance(item, list):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)

@drop_suffix.register # type: ignore
def drop_suffix(item: Set[str], suffix: str, divider: str = '') -> Set[str]:
    """Drops 'suffix' from items in 'item' with 'divider' in between."""
    contents = {drop_suffix(item = i, suffix = suffix, divider = divider) 
                for i in item}      
    if isinstance(item, set):
        return contents
    else:
        vessel = item.__class__
        return vessel(contents)   

@drop_suffix.register # type: ignore
def drop_suffix(item: tuple[str, ...], 
                suffix: str, 
                divider: str = '') -> tuple[str, ...]:
    """Drops 'suffix' from items in 'item' with 'divider' in between."""
    return tuple([drop_suffix(item = i, suffix = suffix, divider = divider) 
                  for i in item])        

""" Other Modifiers """

def capitalify(item: str) -> str:
    """Converts a snake case str to capital case.

    Args:
        item (str): str to convert.

    Returns:
        str: 'item' converted to capital case.

    """
    return item.replace('_', ' ').title().replace(' ', '')

def snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): str to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()
