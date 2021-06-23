"""
representation: functions for representing python objects as strings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    beautify (Callable): provides a pretty str representation for an object. The
        function uses the 'NEW_LINE' and 'INDENT' module-level items for
        the values for new lines and length of an indentation.
        
ToDo:

"""
from __future__ import annotations
import abc
import dataclasses
import inspect
import textwrap
from types import FunctionType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


WHITESPACE: str = ' '
OFFSET: int = 2
INDENT: str = WHITESPACE * OFFSET
NEW_LINE: str = '\n'
WIDTH: int = 40
KINDS: Dict[str, Tuple[str, str]] = {'dict': tuple('{', '}'), 
                                     'list': tuple('[', ']'),
                                     'object': tuple('', ''),
                                     'set': tuple('{', '}'),
                                     'string': tuple('', ''),
                                     'tuple': tuple('(', ')')}


@dataclasses.dataclass
class Designer(object):
    
    package: str = ''
    whitespace: str = ' '
    tab: int = 2
    line_break: str = '\n'
    width: int = 40
    length: int = 20
    textwrapper: textwrap.TextWrapper = None
    brackets: MutableMapping[str, Tuple[str, str]] = dataclasses.field(
        default_factory = lambda: KINDS)
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        self.textwrapper = self.textwrapper or self._build_textwrapper()
        self.package = self.package or __package__ or ''
    
    """ Properties """
    
    @property
    def offset(self) -> str:
        return self.whitespace * self.tab
    
    """ Public Methods """
    
    def beautify(self, 
                 item: object,
                 package: str = None, 
                 exclude: MutableSequence[str] = None,
                 include_private: bool = False) -> object:
        package = package or self.package or ''
        first_line = self.beautify_first_line()
        
        
        
        
        
        return beautify(item = item, 
                        package = package, 
                        exclude = exclude, 
                        include_private = include_private)

    """ Private Methods """
    
    def _build_textwrapper(self) -> None:
        self.textwrapper = textwrap.TextWrapper(
            width = self.width,
            initial_indent = self.offset,
            subsequent_indent = self.offset * 2,
            tabsize = len(self.offset),
            replace_whitespace = False,
            drop_whitespace = False,
            max_lines = self.length,
            placeholder = '...')
        return self
    
def beautify(item: Any, 
             package: str = None, 
             offsets: int = 1, 
             exclude: MutableSequence[str] = None,
             include_private: bool = False) -> str:
    """Flexible tool to make prettier str represtentations of objects.

    Args:
        item (object): object to provide a str representation for.
        package (str): name of the package that the item is from. This is 
            entirely optional and defaults to None.

    Returns:
        str: pretty str representation of the object.
        
    """
    exclude = exclude or []
    effigy = [NEW_LINE]
    kind = _classify_kind(item = item)
    method = globals()[f'beautify_{kind}']
    kwargs = {'item': item, 'offsets': offsets}
    if kind == 'object':
        kwargs.update({'package': package, 
                       'exclude': exclude,
                       'include_private': include_private})
    effigy.append(method(**kwargs))
    effigy.append(NEW_LINE)
    return ''.join(effigy)


def get_beautify_method(item: Any) -> FunctionType:
    """[summary]

    Args:
        item (Any):

    Returns:
        FunctionType:
        
    """
    # if isinstance(item, denovo.quirks.Veneer):
    #     return beautify_other
    if isinstance(item, str):
        return beautify_string
    elif isinstance(item, Mapping):
        return beautify_dict
    elif isinstance(item, MutableSequence):
        return beautify_list
    elif isinstance(item, Sequence):
        return beautify_tuple
    elif isinstance(item, Set):
        return beautify_set
    else:
        return beautify_other

def beautify_list(item: str, contents: Sequence, indents: int) -> str:
    first_indent = INDENT * indents
    other_indent = INDENT * indents + ' ' * len(item) + '   '
    representation = [first_indent, item, ': [']
    length = len(contents)
    for i, item in enumerate(contents):
        beautiful_item = beautify(item = item)
        if i == 0:
            text_to_add = _first_line(item = item,
                                      contents = item,
                                      indents = indents,
                                      start_bracket = '[')
        elif i == length - 1:
            text_to_add = _last_line(item = item,
                                     contents = item,
                                     indents = indents,
                                     start_bracket = '[')
        else:
            text_to_add = _middle_line(indents = )
        
        representation.extend([text_to_add, NEW_LINE])
    representation.append([']'])
    return ''.join(representation)
   
def beautify_dict(item: str, contents: Mapping, indents: int) -> str:
    representation = [INDENT * indents, '{', NEW_LINE]
    print('init rep', representation)
    for key, value in contents.keys():
        representation.append(f'{beautify(key)}: {beautify(value)}')
        representation.append(NEW_LINE)
    representation.append(['}'])
    return ''.join(representation)

def beautify_other(item: str, contents: Any, indents: int) -> str:
    return str(contents)

def beautify_set(item: str, contents: Set, indents: int) -> str:
    representation = ', '.join(contents)
    return ''.join(['{', representation, '}'])

def beautify_string(item: str, contents: Set) -> str:
    return str(contents)

def beautify_tuple(item: str, contents: Set, indents: int) -> str:
    representation = ', '.join(contents)
    return ''.join(['(', representation, ')'])

def _calculate_offset(indents: int, 
                      item: str,
                      format: RepresentationFormat,
                      first_line: bool = False) -> str:
    if first_line:
        return indents * INDENT
    else:
        return indents * INDENT + (len(item) + len(format.offset)) * WHITESPACE


def _classify_kind(item: Any) -> str:
    if isinstance(item, str):
        return 'string'
    elif isinstance(item, MutableMapping):
        return 'dictionary'
    elif isinstance(item, MutableSequence):
        return 'list'
    elif isinstance(item, Sequence):
        return 'tuple'
    elif isinstance(item, Set):
        return 'set'
    else:
        return 'object'
    
def _create_preamble(item: Any, package: str, kind: str, offsets: int) -> str:
    """[summary]

    Args:
        item (Any): [description]
        offsets (int): [description]

    Returns:
        str: [description]
    """
    preamble = [INDENT * offsets]
    if isinstance(item, (str, list, set, tuple, dict)):
        preamble.append(f'{kind}: ')  
    else:
        name = denovo.tools.namify(item = item)
        base = item.__class__.__name__
        if not package:
            module = inspect.getmodule(item)
            package = module.__package__ or None
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
    preamble.append(KINDS[kind][0])
    preamble.append(NEW_LINE)
    return ''.join(preamble)

def _middle_line(indents: int,
                 contents: str,
                 kind: str) -> str:
    return f'{INDENT * indents}{WHITESPACE * (len(kind.start) + len(item) + 2)}{contents},'

def _last_line(indents: int,
                 contents: str,
                 kind: str) -> str:
    bracket = KINDS[kind][0]
    return (f'{INDENT * indents}{WHITESPACE * (len(bracket) + 2)}'
            f'{contents}{bracket}')
  

