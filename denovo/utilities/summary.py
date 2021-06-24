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
TAB: int = 2
INDENT: str = WHITESPACE * TAB
WIDTH: int = 40
LENGTH: int = 20
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
    exclude = exclude or []
    summary = [LINE_BREAK]
    kind = _classify_kind(item = item)
    method = globals()[f'beautify_{kind}']
    kwargs = {'item': item, 'offsets': offsets}
    if kind == 'object':
        kwargs.update({'package': package, 
                       'exclude': exclude,
                       'include_private': include_private})
    summary.append(method(**kwargs))
    summary.append(LINE_BREAK)
    return ''.join(summary)

def beautify_sequence(item: MutableSequence, kind: str, offsets: int) -> str:
    """[summary]

    Args:
        item (MutableSequence): [description]
        offsets (int): [description]

    Returns:
        str: [description]
    """
    kind = kinds[kind]
    indent = _get_indent(offsets = offsets)
    summary = [f'{indent}list: {kind.start}']
    length = len(item)
    for i, sub_item in enumerate(item):
        inner_indent = _get_indent(offsets = offsets, extra = TAB)
        summary.append(f'{inner_indent}{str(sub_item)}, ')
        if VERTICAL and length != i + 1:
            summary.append(LINE_BREAK)
        elif length == i + 1:
            summary.append(brackets[1])
    return ''.join(summary)
   
def beautify_mapping(item: MutableMapping, kind: str, offsets: int) -> str:
    """[summary]

    Args:
        item (MutableMapping): [description]
        offsets (int): [description]

    Returns:
        str: [description]
    """
    brackets = kinds['dict']
    indent = _get_indent(offsets = offsets)
    summary = [f'{indent}dict: {brackets[0]}']
    length = len(item)
    for i, (key, value) in enumerate(item.items()):
        inner_indent = _get_indent(offsets = offsets, extra = TAB)
        summary.append(f'{inner_indent}{str(key)}: {str(value)}, ')
        if VERTICAL and length != i + 1:
            summary.append(LINE_BREAK)
        elif length == i + 1:
            summary.append(brackets[1])
    return ''.join(summary)

def beautify_object(item: MutableSequence, 
                    kind: str,
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
    print('beautifying object')
    if package is None:
        module = inspect.getmodule(item)
        if hasattr(module, '__package__'):
            package = module.__package__
    name = denovo.tools.namify(item = item)
    print('test name', name)
    base = denovo.tools.snakify(item.__class__.__name__)
    print('test base', base)
    brackets = kinds['object']
    indent = _get_indent(offsets = offsets)
    preamble = [indent]
    if name and base and package:
        if name == base:
            preamble.append(f'{package} {name}: ')
        else:
            preamble.append(f'{name}, ({package} {base}): ')
    else:
        if name == base:
            preamble.append(f'{name}: ')
        else:
            preamble.append(f'{name}, ({base}): ')  
    summary = [''.join(preamble)]
    print('test preamble', summary)
    if include_private:
        attributes = [a for a in item.__dict__.keys() if not a.startswith('__')]
    else:
        attributes = [a for a in item.__dict__.keys() if not a.startswith('_')]
    attributes = [a for a in attributes if a not in exclude]
    inner_offsets = offsets + 1
    for attribute in attributes:
        contents = getattr(item, attribute)
        summary.append(f'{attribute}: {brackets[0]}')
        effigy = beautify(item = contents, offsets = inner_offsets)
        print('test effigy', effigy)
        summary.append(effigy)
        summary.append(brackets[1])
        summary.append(LINE_BREAK)
    print('test summary', summary)
    return ''.join(summary)

def beautify_string(item: str, offsets: int) -> str:
    """[summary]

    Args:
        item (str): [description]
        offsets (int): [description]

    Returns:
        str: [description]
    """
    brackets = kinds['str']
    indent = _get_indent(offsets = offsets)
    return [f'{indent}str: {brackets[0]}{item}{brackets[1]}']

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

def _classify_kind(item: Any) -> str:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        str: [description]
    """
    if isinstance(item, str):
        return 'str'
    elif isinstance(item, MutableMapping):
        return 'dict'
    elif isinstance(item, MutableSequence):
        return 'list'
    elif isinstance(item, Sequence):
        return 'tuple'
    elif isinstance(item, Set):
        return 'set'
    else:
        return 'object'
    
def _get_textwrapper() -> textwrap.TextWrapper:
    """[summary]

    Returns:
        textwrap.TextWrapper: [description]
    """
    return textwrap.TextWrapper(
        width = WIDTH,
        tabsize = len(INDENT),
        replace_whitespace = False,
        drop_whitespace = False,
        max_lines = LENGTH,
        placeholder = '...')
    
""" Module Level Attributes """

kinds: Dict[str, SummaryKind] = {dict: SummaryKind(name = 'dictionary',
                                                   method = beautify_mapping,
                                                   start = '{',
                                                   end = '}'),
                                 list: SummaryKind(name = 'list',
                                                   method = beautify_sequence,
                                                   start = '[',
                                                   end = ']'), 
                                 object: SummaryKind(name = None,
                                                     method = beautify_object,
                                                     start = '',
                                                     end = ''),
                                 set: SummaryKind(name = 'set',
                                                  method = beautify_sequence,
                                                  start = '{',
                                                  end = '}'),
                                 str: SummaryKind(name = 'string',
                                                  method = beautify_string,
                                                  start = '',
                                                  end = ''),
                                 tuple: SummaryKind(name = 'tuple',
                                                    method = beautify_sequence,
                                                    start = '(',
                                                    end = ')')}