"""
representation: functions for representing python objects as strings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    beautify (Callable): provides a pretty str representation for an object. The
        function uses the 'NEW_LINE' and 'INDENT' module-level attributes for
        the values for new lines and length of an indentation.
        
ToDo:

"""
from __future__ import annotations
import abc
import dataclasses
import textwrap
from types import FunctionType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


SPACE: str = ' '
TAB: int = 2
INDENT: str = SPACE * TAB
NEW_LINE: str = '\n'
WIDTH: int = 40


@dataclasses.dataclass
class RepresentationFormat(object):
    
    kind: Union[Type, Tuple[Type]]
    start: str = ''
    end: str = ''
    comma_separated: bool = True
    
    def __post_init__(self) -> None:
        self.offset = len(self.start) + 2
                                                       
    
formats: Dict = {}
formats['dict'] = RepresentationFormat(kind = Mapping,
                                       start = '{',
                                       end = '}')
formats['list'] = RepresentationFormat(kind = MutableSequence,
                                       start = '[',
                                       end = ']')
formats['set'] = RepresentationFormat(kind = Set,
                                      start = '{',
                                      end = '}')
formats['string'] = RepresentationFormat(kind = str)
formats['tuple'] = RepresentationFormat(kind = Sequence,
                                        start = '(',
                                        end = ')')

    
def beautify(item: object, 
             package: str = None, 
             exclude: MutableSequence[str] = None,
             include_private: bool = False,
             indents: int = 1) -> str:
    """Flexible tool to make prettier str represtentations of objects.

    Args:
        item (object): object to provide a str representation for.
        package (str): name of the package that the item is from. This is 
            entirely optional and defaults to None.

    Returns:
        str: pretty str representation of the object.
        
    """
    package = package or __package__ or ''
    exclude = exclude or []
    effigy = [NEW_LINE]
    if package:
        effigy.append(f'{package} ')
    effigy.append(item.__class__.__name__)
    print('test start rep', effigy)
    if include_private:
        attributes = [a for a in item.__dict__.keys() if not a.startswith('__')]
    else:
        attributes = [a for a in item.__dict__.keys() if not a.startswith('_')]
    attributes = [a for a in attributes if a not in exclude]
    for attribute in attributes:
        contents = getattr(item, attribute)
        method = get_beautify_method(item = contents)
        print('test attribute contents', contents)
        effigy.append(method(attribute = attribute,
                             contents = contents,
                             indents = indents))
    print('test effigy end', effigy)
    return NEW_LINE.join(effigy)

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

def beautify_list(attribute: str, contents: Sequence, indents: int) -> str:
    first_indent = INDENT * indents
    other_indent = INDENT * indents + ' ' * len(attribute) + '   '
    representation = [first_indent, attribute, ': [']
    length = len(contents)
    for i, item in enumerate(contents):
        beautiful_item = beautify(item = item)
        if i == 0:
            text_to_add = _first_line(attribute = attribute,
                                      contents = item,
                                      indents = indents,
                                      start_bracket = '[')
        elif i == length - 1:
            text_to_add = _last_line(attribute = attribute,
                                     contents = item,
                                     indents = indents,
                                     start_bracket = '[')
        else:
            text_to_add = _middle_line(indents = )
        
        representation.extend([text_to_add, NEW_LINE])
    representation.append([']'])
    return ''.join(representation)
   
def beautify_dict(attribute: str, contents: Mapping, indents: int) -> str:
    representation = [INDENT * indents, '{', NEW_LINE]
    print('init rep', representation)
    for key, value in contents.keys():
        representation.append(f'{beautify(key)}: {beautify(value)}')
        representation.append(NEW_LINE)
    representation.append(['}'])
    return ''.join(representation)

def beautify_other(attribute: str, contents: Any, indents: int) -> str:
    return str(contents)

def beautify_set(attribute: str, contents: Set, indents: int) -> str:
    representation = ', '.join(contents)
    return ''.join(['{', representation, '}'])

def beautify_string(attribute: str, contents: Set) -> str:
    return str(contents)

def beautify_tuple(attribute: str, contents: Set, indents: int) -> str:
    representation = ', '.join(contents)
    return ''.join(['(', representation, ')'])

def _calculate_offset(indents: int, 
                      attribute: str,
                      format: RepresentationFormat,
                      first_line: bool = False) -> str:
    if first_line:
        return indents * INDENT
    else:
        return indents * INDENT + (len(attribute) + len(format.offset)) * SPACE

def _first_line(attribute: str,
                contents: str,
                offset: int,
                kind: RepresentationFormat) -> str:
    return f'{SPACE * offset}{attribute}: {kind.start}{contents},'

def _middle_line(indents: int,
                 contents: str,
                 kind: RepresentationFormat) -> str:
    return f'{INDENT * indents}{SPACE * (len(kind.start) + len(attribute) + 2)}{contents},'

def _last_line(indents: int,
                 contents: str,
                 kind: RepresentationFormat) -> str:
    return (f'{INDENT * indents}{SPACE * (len(end_bracket) + 2)}'
            f'{contents}{end_bracket}')
  

