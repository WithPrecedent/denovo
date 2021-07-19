"""
summary: functions for representing python objects as strings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    SummaryKind (object): data for a data type's representation.
    kinds (Dict): dictionary of different supported types with SummaryKind
        instances as values.
    beautify (Callable): provides a pretty str summary for an object. The
        function uses the 'LINE_BREAK' and 'INDENT' module-level items for
        the values for new lines and length of an indentation.
    beautify_mapping (Callable): returns a beautiful string repreentation of a
        dict or dict-like object.
    beautify_object (Callable): returns a beautiful string repreentation of a
        class instance and its attributes.
    beautify_sequence (Callable): returns a beautiful string repreentation of a
        list, set, tuple, list-like, set-like, or tuple-like object.
    beautify_string (Callable): returns a beautiful string repreentation of a
        str.
    _get_indent (Callable): determines the appropriate indentation for a 
        beautiful str.
    _classify_kind (Callable): called by 'beautify' to determine the appropriate
        function to beautify the passed 'item'.
         
ToDo:
    Clean up and add DocStrings
    Add a textwrap option when VERTICAL is False.
    
"""
from __future__ import annotations
import dataclasses
import inspect
import textwrap
from types import FunctionType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, Mapping, 
                    MutableMapping, MutableSequence, Optional, Sequence, Type, 
                    Union)

import denovo


LINE_BREAK: str = '\n'
WHITESPACE: str = ' '
TAB: int = 3
INDENT: str = WHITESPACE * TAB
MAX_WIDTH: int = 40
MAX_LENGTH: int = 20
INCOMPLETE: str = '...'
VERTICAL: bool = True


""" Public Classes """


@dataclasses.dataclass
class SummaryKind(object):
    """Contains formating information for different data types.
    
    Args:
        name (str): name of data type to be used in the str returned by 
            'beautify'.
        method (FunctionType): the function to use to beautify the particular
            data type.
        start (str): starting bracket for listing the contents of the data type.
            Defaults to ''.
        end (str): ending bracket for listing the contents of the data type.
            Defaults to ''.           
    
    """
    name: str
    method: FunctionType
    start: str = ''
    end: str = ''

""" Public Functions"""
    
def beautify(item: Any, 
             offsets: int = 1, 
             package: str = None,
             exclude: MutableSequence[str] = None,
             include_private: bool = False) -> str:
    """Returns a beautiful string representation of 'item'.

    Args:
        item (Any): item to provide a str representation of.
        offsets (int): number of tabs of whitespace to put before the str
            representation. Defaults to 1.
        package (str): name of associated package of 'item'. 'package' is only
            used if 'item' is an object. Defaults to None.
        exclude (MutableSequence[str]): if 'item' is an object, the names of
            attributes to exclude from the str representation. Defaults to None.
        include_private (bool): whether to include attributes with a single 
            leading underscore. Defaults to False.

    Returns:
        str: beautiful str representation of 'item'.
        
    """
    kind = _classify_kind(item = item)
    if kind is None:
        indent = _get_indent(offsets = offsets)
        summary = f'{indent}None'
    else:
        kwargs = {'item': item, 'kind': kind, 'offsets': offsets}
        if kind.name == 'object':
            exclude = exclude or []
            kwargs.update({'package': package, 
                        'exclude': exclude,
                        'include_private': include_private})
        summary = kind.method(**kwargs)
    return f'{LINE_BREAK}{summary}'
   
def beautify_mapping(item: MutableSequence, 
                     kind: Union[SummaryKind, Type], 
                     offsets: int) -> str:
    """Returns a beautiful string representation of a mapping data type.

    Args:
        item (MutableMapping): [description]
        offsets (int): [description]

    Returns:
        str: [description]
    """
    if not isinstance(kind, SummaryKind):
        kind = kinds[kind]
    indent = _get_indent(offsets = offsets)
    inner = _get_indent(offsets = offsets, extra = TAB)
    summary = [f'{indent}{kind.name}: {kind.start}{LINE_BREAK}']
    length = len(item)
    for i, (key, value) in enumerate(item.items()):
        if i == MAX_LENGTH:
            summary.append(f'{inner}{INCOMPLETE}, {kind.end}{LINE_BREAK}')
            break
        else:
            summary.append(f'{inner}{key}: {value}')
            if i + 1 == length:
                summary.append(f'{kind.end}')
            else:
                summary.append(f',')
            summary.append(f'{LINE_BREAK}')
    return ''.join(summary)

def beautify_object(item: MutableSequence, 
                    kind: Union[SummaryKind, Type], 
                    offsets: int,
                    package: str = None,
                    exclude: MutableSequence[str] = None,
                    include_private: bool = False) -> str:
    """[summary]

    Args:
        item (Any): item to provide a str representation of.
        offsets (int): number of tabs of whitespace to put before the str
            representation. Defaults to 1.
        package (str): name of associated package of 'item'. 'package' is only
            used if 'item' is an object. Defaults to None.
        exclude (MutableSequence[str]): if 'item' is an object, the names of
            attributes to exclude from the str representation. Defaults to None.
        include_private (bool): whether to include attributes with a single 
            leading underscore. Defaults to False.

    Returns:
        str: [description]
        
    """
    if not isinstance(kind, SummaryKind):
        kind = kinds[kind]
    if package is None:
        module = inspect.getmodule(item)
        if hasattr(module, '__package__'):
            package = module.__package__
    if kind.name == 'object':
        name = denovo.tools.namify(item = item)
    else:
        name = ''
    base = denovo.tools.snakify(item.__class__.__name__)
    indent = _get_indent(offsets = offsets)
    inner = _get_indent(offsets = offsets, extra = TAB)
    summary = [f'{indent}']
    if name and base and package:
        if name == base:
            summary.append(f'{package} {name}: {LINE_BREAK}')
        else:
            summary.append(f'{name}, ({package} {base}): {LINE_BREAK}')
    else:
        if name == base:
            summary.append(f'{name}: {LINE_BREAK}')
        else:
            summary.append(f'{name}, ({base}): {LINE_BREAK}')  
    if include_private:
        attributes = [a for a in item.__dict__.keys() if not a.startswith('__')]
    else:
        attributes = [a for a in item.__dict__.keys() if not a.startswith('_')]
    attributes = [a for a in attributes if a not in exclude]
    inner_offsets = offsets + 2
    for attribute in attributes:
        contents = getattr(item, attribute)
        summary.append(f'{inner}{attribute}: {kind.start}')
        summary.append(beautify(item = contents, offsets = inner_offsets))
    return ''.join(summary)

def beautify_sequence(item: Union[MutableSequence, set, tuple], 
                      kind: Union[SummaryKind, Type], 
                      offsets: int) -> str:
    """Returns a beautiful string representation of a 1-dimensional data type.

    Args:
        item (Union[MutableSequence, set, tuple]): the list, set, tuple, or 
            similar object to return a str representation for.
        kind (Union[SummaryKind, Type]): 
        offsets (int): [description]

    Returns:
        str: [description]
    """
    if not isinstance(kind, SummaryKind):
        kind = kinds[kind]
    indent = _get_indent(offsets = offsets)
    inner = _get_indent(offsets = offsets, extra = TAB)
    summary = [f'{indent}{kind.name}: {kind.start}{LINE_BREAK}']
    length = len(item)
    for i, sub_item in enumerate(item):
        if i == MAX_LENGTH:
            summary.append(f'{inner}{INCOMPLETE}, {kind.end}{LINE_BREAK}')
            break
        else:
            summary.append(f'{inner}{str(sub_item)}')
            if i + 1 == length:
                summary.append(f'{kind.end}')
            else:
                summary.append(f',')
            summary.append(f'{LINE_BREAK}')
    return ''.join(summary)

def beautify_string(item: MutableSequence, 
                    kind: Union[SummaryKind, Type], 
                    offsets: int) -> str:
    """[summary]

    Args:
        item (str): [description]
        offsets (int): [description]

    Returns:
        str: [description]
    """
    if not isinstance(kind, SummaryKind):
        kind = kinds[kind]
    indent = _get_indent(offsets = offsets)
    return f'{indent}{kind.name}: {kind.start}{item}{kind.end}'

""" Private Functions """

def _get_indent(offsets: int, extra: int = 0) -> str:
    """[summary]

    Args:
        offsets (int): [description]
        extra (int, optional): [description]. Defaults to 0.

    Returns:
        str: [description]
    """
    return offsets * INDENT + extra * WHITESPACE

def _classify_kind(item: Any) -> SummaryKind:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        str: [description]
    """
    if item is None:
        return None
    else:
        for kind, data in kinds.items():
            if isinstance(item, kind):
                return data
    return kinds[str]
       
# def _get_textwrapper() -> textwrap.TextWrapper:
#     """[summary]

#     Returns:
#         textwrap.TextWrapper: [description]
#     """
#     return textwrap.TextWrapper(
#         width = MAX_WIDTH,
#         tabsize = len(INDENT),
#         replace_whitespace = False,
#         drop_whitespace = False,
#         max_lines = MAX_LENGTH,
#         placeholder = '...')
    
""" Module Level Attributes """

kinds: Dict[str, SummaryKind] = {}
kinds[str] = SummaryKind(name = 'string',
                         method = beautify_string,
                         start = '',
                         end = '')
kinds[MutableMapping] = SummaryKind(name = 'dictionary',
                                    method = beautify_mapping,
                                    start = '{',
                                    end = '}')
kinds[MutableSequence] = SummaryKind(name = 'list',
                                     method = beautify_sequence,
                                     start = '[',
                                     end = ']')
kinds[Sequence] = SummaryKind(name = 'tuple',
                              method = beautify_sequence, 
                              start = '(',
                              end = ')')
kinds[set] = SummaryKind(name = 'set',
                         method = beautify_sequence,
                         start = '{',
                         end = '}')
kinds[object] = SummaryKind(name = 'object',
                            method = beautify_object,
                            start = '',
                            end = '')
