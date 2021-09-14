"""
tools: functions that convert types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

All tools should follow one of two forms. For conversion of a known type
to another type, the function name should be:
    f'{source type}_to_{output type}'
For a conversion from an unknown type to another type, the function name should
be:
    f'to_{output type}'
     
Contents:
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
        
    adjacency_to_edges (Callable): converts adjacency list to edge list.
    adjacency_to_matrix (Callable): converts adjacency list to adjacency matrix.
    edges_to_adjacency (Callable): converts edge list to an adjacency list.
    matrix_to_adjacency (Callable): converts adjacency matrix to an adjacency 
        list.
    pipeline_to_adjacency (Callable): converts pipeline to an adjacency list.

ToDo:
    Add more flexible tools.
    
"""
from __future__ import annotations
import ast
import collections
from collections.abc import (Collection, Hashable, Iterable, Mapping, 
                             MutableMapping, MutableSequence, Sequence, Set)
import functools
import inspect
import pathlib
import re
from typing import Any, Callable, Optional, Type, Union

import more_itertools

import denovo
from denovo.types import (
    Adjacency, Dyad, Edges, Matrix, Operation, Pipeline)


""" Class Related Tools """

def instancify(item: Union[Type[Any], object], **kwargs: Any) -> Any:
    """Returns 'item' as an instance with 'kwargs' as parameters/attributes.
    
    If 'item' is already an instance, kwargs are added as attributes to the
    existing 'item'.

    Args:
        item (Union[Type, object])): class to make an instance out of by passing
            kwargs or an instance to add kwargs to as attributes.

    Raises:
        TypeError: if 'item' is neither a class nor instance.
        
    Returns:
        object: a class instance with 'kwargs' as attributes or passed as 
            parameters (if 'item' is a class).
        
    """         
    if inspect.isclass(item):
        return item(**kwargs) # type: ignore
    elif isinstance(item, object):
        for key, value in kwargs.items():
            setattr(item, key, value)
        return item
    else:
        raise TypeError('item must be a class or class instance')

def kwargify(item: Type[Any], args: tuple[Any]) -> dict[Hashable, Any]:
    """Converts args to kwargs.
    
    Args:
        args (tuple): arguments without keywords passed to 'item'.
        item (Type): the item with annotations used to construct kwargs.
        
    Returns
        dict[Hashable, Any]: kwargs based on 'args' and 'item'.
    
    """
    annotations = item.__annotations__.keys()
    return dict(zip(annotations, args))
    
""" Flexible Converters """
         
def listify(item: Any, default: Optional[Any] = None) -> Any:
    """Returns passed item as a list (if not already a list).

    Args:
        item (Any): item to be transformed into a list to allow proper 
            iteration.
        default (Optional[Any]): the default value to return if 'item' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default' is set to 
            [].

    Returns:
        Union[MutableSequence[Any], Any]: a passed list, 'item' converted to a 
            list, or 'default'.

    """
    if item is None:
        if default is None:
            return []
        elif default in ['None', 'none']:
            return None
        else:
            return default
    elif isinstance(item, MutableSequence) and not isinstance(item, str):
        return item
    else:
        return [item]
                 
def numify(item: Any, raise_error: bool = False) -> Union[int, float, Any]:
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
        Union[int, float, str]: converted to numeric type, if possible.

    """
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            if raise_error:
                raise TypeError('item not able to be converted to a numeric '
                                'type')
            else:
                return item
        
def stringify(item: Any, default: Optional[Any] = None) -> Any:
    """Converts 'item' to a str from a Sequence.
    
    Args:
        item (Any): item to convert to a str from a list if it is a list.
        default (Any): value to return if 'item' is equivalent to a null
            value when passed. Defaults to None.
    
    Raises:
        TypeError: if 'item' is not a str or list-like object.
        
    Returns:
        Any: str, if item was a list, None or the default value if a null value
            was passed, or the item as it was passed if there previous two 
            conditions don't appply.

    """
    if item is None:
        if default is None:
            return ''
        elif default in ['None', 'none']: 
            return None
        else:
            return default
    elif isinstance(item, str):
        return item
    elif isinstance(item, Sequence):
        return ', '.join(item)
    else:
        raise TypeError('item must be str or a sequence')
    
def tuplify(item: Any, default: Optional[Any] = None) -> Any:
    """Returns passed item as a tuple (if not already a tuple).

    Args:
        item (Any): item to be transformed into a tuple.
        default (Any): the default value to return if 'item' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default'
            is set to ().

    Returns:
        tuple[Any]: a passed tuple, 'item' converted to a tuple, or 
            'default'.

    """
    if item is None:
        if default is None:
            return tuple()
        elif default in ['None', 'none']:
            return None
        else:
            return default
    elif isinstance(item, tuple):
        return item
    elif isinstance(item, Iterable):
        return tuple(item)
    else:
        return tuple([item])
        
def typify(item: str) -> Union[Sequence[Any], int, float, bool, str]:
    """Converts stings to appropriate, supported datatypes.

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
                return [typify(i) for i in item]
            else:
                return item

""" File Related Converters """

def pathlibify(item: Union[str, pathlib.Path]) -> pathlib.Path:
    """Converts string 'path' to pathlib.Path object.

    Args:
        item (Union[str, pathlib.Path]): either a string summary of a
            path or a pathlib.Path object.

    Returns:
        pathlib.Path object.

    Raises:
        TypeError if 'path' is neither a str or pathlib.Path type.

    """
    if isinstance(item, str):
        return pathlib.Path(item)
    elif isinstance(item, pathlib.Path):
        return item
    else:
        raise TypeError('item must be str or pathlib.Path type')
                         
""" Converters """

@denovo.decorators.dispatcher 
def to_adjacency(source: Any) -> Adjacency:
    """Converts 'source' to an Adjacency.
    
    Args:
        source (Any): source to convert to an Adjacency.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Adjacency: derived from 'source'.

    """
    if isinstance(source, Adjacency):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_adjacency.register # type: ignore
def edges_to_adjacency(source: Edges) -> Adjacency:
    """Converts and edge list to an adjacency list."""
    adjacency = collections.defaultdict(set)
    for edge_pair in source:
        if edge_pair[0] not in adjacency:
            adjacency[edge_pair[0]] = {edge_pair[1]}
        else:
            adjacency[edge_pair[0]].add(edge_pair[1])
        if edge_pair[1] not in adjacency:
            adjacency[edge_pair[1]] = set()
    return adjacency

@to_adjacency.register # type: ignore 
def matrix_to_adjacency(source: Matrix) -> Adjacency:
    """Converts a Matrix to an Adjacency."""
    matrix = source[0]
    names = source[1]
    name_mapping = dict(zip(range(len(matrix)), names))
    raw_adjacency = {
        i: [j for j, adjacent in enumerate(row) if adjacent] 
        for i, row in enumerate(matrix)}
    adjacency = collections.defaultdict(set)
    for key, value in raw_adjacency.items():
        new_key = name_mapping[key]
        new_values = set()
        for edge in value:
            new_values.add(name_mapping[edge])
        adjacency[new_key] = new_values
    return adjacency

@to_adjacency.register # type: ignore 
def pipeline_to_adjacency(source: Pipeline) -> Adjacency:
    """Converts a Pipeline to an Adjacency."""
    adjacency = collections.defaultdict(set)
    edges = more_itertools.windowed(source, 2)
    for edge_pair in edges:
        adjacency[edge_pair[0]] = {edge_pair[1]}
    return adjacency

@denovo.decorators.dispatcher   
def to_dict(source: Any) -> MutableMapping[Hashable, Any]:
    """Converts 'source' to a MutableMapping.
    
    Args:
        source (Any): source to convert to a MutableMapping.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        MutableMapping: derived from 'source'.

    """
    if isinstance(source, MutableMapping):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_dict.register # type: ignore   
def dyad_to_dict(source: Dyad) -> MutableMapping[Hashable, Any]:
    """Converts a Dyad to a MutableMapping."""
    return dict(zip(source))

@denovo.decorators.dispatcher   
def to_dyad(source: Any) -> Dyad:
    """Converts 'source' to a Dyad.
    
    Args:
        source (Any): source to convert to a Dyad.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Dyad: derived from 'source'.

    """
    if isinstance(source, Dyad):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')
    
@to_dyad.register # type: ignore
def dict_to_dyad(source: MutableMapping) -> Dyad:
    """Converts a MutableMapping to a Dyad."""
    return zip(*source)

@denovo.decorators.dispatcher   
def to_edges(source: Any) -> Edges:
    """Converts 'source' to an Edges.
    
    Args:
        source (Any): source to convert to an Edges.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Edges: derived from 'source'.

    """
    if isinstance(source, Edges):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')
    
@to_edges.register # type: ignore
def adjacency_to_edges(source: Adjacency) -> Edges:
    """Converts an Adjacency to an Edges."""
    edges = []
    for node, connections in source.items():
        for connection in connections:
            edges.append(tuple(node, connection))
    return edges

@denovo.decorators.dispatcher   
def to_index(source: Any) -> Hashable:
    """Converts 'source' to an Hashable.
    
    Args:
        source (Any): source to convert to a Hashable.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Hashable: derived from 'source'.

    """
    if isinstance(source, Hashable):
        return source
    else:
        try:
            return hash(source)
        except TypeError:
            try:
                return str(source)
            except TypeError:
                try:
                    return denovo.modify.snakify(source.__name__)
                except AttributeError:
                    return denovo.modify.snakify(source.__class__.__name__)
                except AttributeError:
                    raise TypeError(f'source cannot be converted because it is ' 
                                    f'an unsupported type: '
                                    f'{type(source).__name__}')

@to_index.register # type: ignore
def str_to_index(source: str) -> Hashable:
    """Converts a str to an Hashable."""
    return source

@denovo.decorators.dispatcher   
def to_int(source: Any) -> int:
    """Converts 'source' to a pathlib.Path.
    
    Args:
        source (Any): source to convert to a int.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        int: derived from 'source'.

    """
    if isinstance(source, int):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_int.register # type: ignore
def str_to_int(source: str) -> int:
    """Converts a str to an int."""
    return int(source)

@to_int.register # type: ignore
def float_to_int(source: float) -> int:
    """Converts a float to an int."""
    return int(source)

@denovo.decorators.dispatcher   
def to_list(source: Any) -> list[Any]:
    """Converts 'source' to a list.
    
    Args:
        source (Any): source to convert to a list.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        list[Any]: derived from 'source'.

    """
    if isinstance(source, list[Any]):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_list.register # type: ignore
def str_to_listing(source: str) -> list[Any]:
    """Converts a str to a list."""
    return ast.literal_eval(source)

@denovo.decorators.dispatcher   
def to_matrix(source: Any) -> Matrix:
    """Converts 'source' to a Edges.
    
    Args:
        source (Any): source to convert to a Matrix.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Matrix: derived from 'source'.

    """
    if isinstance(source, Matrix):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_matrix.register # type: ignore 
def adjacency_to_matrix(source: Adjacency) -> Matrix:
    """Converts an Adjacency to a Matrix."""
    names = list(source.keys())
    matrix = []
    for i in range(len(source)): 
        matrix.append([0] * len(source))
        for j in source[i]:
            matrix[i][j] = 1
    return tuple(matrix, names)

@denovo.decorators.dispatcher   
def to_float(source: Any) -> float:
    """Converts 'source' to a float.
    
    Args:
        source (Any): source to convert to a float.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        float: derived from 'source'.

    """
    if isinstance(source, float):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_float.register # type: ignore
def int_to_float(source: int) -> float:
    """Converts an int to a float."""
    return float(source)

@to_float.register # type: ignore
def str_to_float(source: str) -> float:
    """Converts a str to a float."""
    return float(source)

@denovo.decorators.dispatcher   
def to_path(source: Any) -> pathlib.Path:
    """Converts 'source' to a pathlib.Path.
    
    Args:
        source (Any): source to convert to a pathlib.Path.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        pathlib.Path: derived from 'source'.

    """
    if isinstance(source, pathlib.Path):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_path.register # type: ignore   
def str_to_path(source: str) -> pathlib.Path:
    """Converts a str to a pathlib.Path."""
    return pathlib.pathlib.Path(source)

@denovo.decorators.dispatcher   
def to_str(source: Any) -> str:
    """Converts 'source' to a str.
    
    Args:
        source (Any): source to convert to a str.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        str: derived from 'source'.

    """
    if isinstance(source, str):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_str.register # type: ignore
def int_to_str(source: int) -> str:
    """Converts an int to a str."""
    return str(source)

@to_str.register # type: ignore
def float_to_str(source: float) -> str:
    """Converts an float to a str."""
    return str(source)

@to_str.register # type: ignore
def list_to_str(source: list[Any]) -> str:
    """Converts a list to a str."""
    return ', '.join(source)
   
@to_str.register 
def none_to_str(source: None) -> str:
    """Converts None to a str."""
    return 'None'

@to_str.register # type: ignore
def path_to_str(source: pathlib.Path) -> str:
    """Converts a pathlib.Path to a str."""
    return str(source)

""" Converter Registry and Registry Decorator """

catalog: denovo.containers.Catalog = denovo.containers.Catalog()

 
def bondafide(_wrapped: Optional[Type[Any]] = None, 
              *,
              include: Optional[list[str]] = None, 
              exclude: Optional[list[str]] = None) -> Any:
    """Wraps a python dataclass and validates/converts attributes.
    
    """
    include = include or []
    exclude = exclude or []
    def validator(wrapped: Type[Any]) -> Any:
        @functools.wraps(wrapped)
        def wrapper(*args: Any, **kwargs: Any) -> object:
            kwargs.update(denovo.tools.kwargify(args = args, item = wrapped))
            instance = wrapped(**kwargs)
            attributes = include or wrapped.__annotations__.keys()
            attributes = [a for a in attributes if a not in exclude] # type: ignore
            for attribute in attributes:
                try:
                    kind = wrapped.__annotations__[attribute]
                    key = kind.__name__
                    value = getattr(instance, attribute)
                    if not isinstance(value, kind):
                        converter = catalog[key]
                        new_value = converter(source = value)
                        setattr(instance, attribute, new_value)
                except KeyError:
                    pass
            return instance
        return wrapper
    if _wrapped is None:
        return validator
    else:
        return validator(wrapped = _wrapped)
    
   