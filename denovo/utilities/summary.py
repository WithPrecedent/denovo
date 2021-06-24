"""
summary: functions for representing python objects as strings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    beautify (Callable): provides a pretty str summary for an object. The
        function uses the 'LINE_BREAK' and 'INDENT' module-level items for
        the values for new lines and length of an indentation.
        
ToDo:
    Clean up and add DocStrings
    
"""
from __future__ import annotations
import dataclasses
import inspect
import textwrap
from types import FunctionType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


LINE_BREAK: str = '\n'
WHITESPACE: str = ' '
TAB: int = 3
INDENT: str = WHITESPACE * TAB
MAX_WIDTH: int = 40
MAX_LENGTH: int = 20
INCOMPLETE: str = '...'
VERTICAL: bool = True


@dataclasses.dataclass
class SummaryKind(object):
    
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
    """[summary]

    Args:
        item (Any): [description]
        offsets (int, optional): [description]. Defaults to 1.
        package (str, optional): [description]. Defaults to None.
        exclude (MutableSequence[str], optional): [description]. Defaults to None.
        include_private (bool, optional): [description]. Defaults to False.

    Returns:
        str: [description]
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

def beautify_sequence(item: MutableSequence, 
                      kind: Union[Type, SummaryKind], 
                      offsets: int) -> str:
    """[summary]

    Args:
        item (MutableSequence): [description]
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
   
def beautify_mapping(item: MutableSequence, 
                     kind: Union[Type, SummaryKind], 
                     offsets: int) -> str:
    """[summary]

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
                    kind: Union[Type, SummaryKind], 
                    offsets: int,
                    package: str = None,
                    exclude: MutableSequence[str] = None,
                    include_private: bool = False) -> str:
    """[summary]

    Args:
        item (MutableSequence): [description]
        offsets (int): [description]
        package (str, optional): [description]. Defaults to None.
        exclude (MutableSequence[str], optional): [description]. Defaults to None.
        include_private (bool, optional): [description]. Defaults to False.

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

def beautify_string(item: MutableSequence, 
                    kind: Union[Type, SummaryKind], 
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
       
def _get_textwrapper() -> textwrap.TextWrapper:
    """[summary]

    Returns:
        textwrap.TextWrapper: [description]
    """
    return textwrap.TextWrapper(
        width = MAX_WIDTH,
        tabsize = len(INDENT),
        replace_whitespace = False,
        drop_whitespace = False,
        max_lines = MAX_LENGTH,
        placeholder = '...')
    
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
kinds[Set] = SummaryKind(name = 'set',
                         method = beautify_sequence,
                         start = '{',
                         end = '}')
kinds[object] = SummaryKind(name = 'object',
                            method = beautify_object,
                            start = '',
                            end = '')
