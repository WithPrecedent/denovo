"""
memory: memory conservation functions
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    add_slots (Callable): adds '__slots__' to a python dataclass.

ToDo:

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)


def add_slots(item: Type) -> Type:
    """Adds slots to dataclass with default values.
    
    Derived from code here: 
    https://gitquirks.com/ericvsmith/dataclasses/blob/master/dataclass_tools.py
    
    Args:
        item: class to add slots to
        
    Raises:
        TypeError: if '__slots__' is already in item.
        
    Returns:
        object: class with '__slots__' added.
        
    """
    if '__slots__' in item.__dict__:
        raise TypeError(f'{item.__name__} already contains __slots__')
    else:
        item_dict = dict(item.__dict__)
        field_names = tuple(f.name for f in dataclasses.field(item))
        item_dict['__slots__'] = field_names
        for field_name in field_names:
            item_dict.pop(field_name, None)
        item_dict.pop('__dict__', None)
        qualname = getattr(item, '__qualname__', None)
        item = type(item)(item.__name__, item.__bases__, item_dict)
        if qualname is not None:
            item.__qualname__ = qualname
    return item
