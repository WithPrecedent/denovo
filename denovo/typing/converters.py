"""
converters: functions that convert types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

All converters should follow one of two forms. For conversion of a known type
to another type, the function name should be:
    f'{source type}_to_{output type}'
For a conversion from an unknown type to another type, the function name should
be:
    f'to_{output type}'
     
Contents:
    is_adjacency_list (Callable): tests if an object is an adjacency list.
    is_adjacency_matrix (Callable): tests if an object is an adjacency matrix.
    is_edge_list (Callable): tests if an object is an edge list.
    is_pipeline (Callable): tests if an object is a pipeline.
    adjacency_to_edges (Callable): converts adjacency list to edge list.
    adjacency_to_matrix (Callable): converts adjacency list to adjacency matrix.
    edges_to_adjacency (Callable): converts edge list to an adjacency list.
    matrix_to_adjacency (Callable): converts adjacency matrix to an adjacency 
        list.
    pipeline_to_adjacency (Callable): converts pipeline to an adjacency list.

ToDo:
    Add more flexible converters.
    
"""
from __future__ import annotations
import ast
import collections
from collections.abc import Hashable, MutableMapping, MutableSequence
import dataclasses
import functools
import pathlib
from typing import Any, Callable, Optional, Type, Union

import more_itertools

import denovo
from denovo.typing.types import (Adjacency, Composite, Connections, Dyad, Edge, 
                                 Edges, Group, Kind, Listing, Matrix, Nodes, 
                                 Order, Pipeline, Pipelines, Repeater)


""" Converter Registry and Registry Decorator """

catalog: denovo.containers.Catalog = denovo.containers.Catalog()

 
def bondafide(_wrapped: Optional[dataclasses.dataclass] = None, 
              *,
              include: Optional[list[str]] = None, 
              exclude: Optional[list[str]] = None):
    """Wraps a python dataclass and validates/converts attributes.
    
    """
    include = include or []
    exclude = exclude or []
    def validator(wrapped: dataclasses.dataclass):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            kwargs.update(denovo.tools.kwargify(args = args, item = wrapped))
            instance = wrapped(**kwargs)
            attributes = include or wrapped.__annotations__.keys()
            attributes = [a for a in attributes if a not in exclude]  
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

@to_adjacency.register 
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

@to_adjacency.register 
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

@to_adjacency.register 
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

@to_dict.register   
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
    
@to_dyad.register
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
    
@to_edges.register
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
                    return denovo.tools.snakify(source.__name__)
                except AttributeError:
                    return denovo.tools.snakify(source.__class__.__name__)
                except AttributeError:
                    raise TypeError(f'source cannot be converted because it is ' 
                                    f'an unsupported type: '
                                    f'{type(source).__name__}')

@to_index.register
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

@to_int.register
def str_to_int(source: str) -> int:
    """Converts a str to an int."""
    return int(source)

@to_int.register
def float_to_int(source: float) -> int:
    """Converts a float to an int."""
    return int(source)

@denovo.decorators.dispatcher   
def to_list(source: Any) -> Listing:
    """Converts 'source' to a Listing.
    
    Args:
        source (Any): source to convert to a Listing.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Listing: derived from 'source'.

    """
    if isinstance(source, Listing):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_list.register
def str_to_listing(source: str) -> Listing:
    """Converts a str to a Listing."""
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

@to_matrix.register 
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

@to_float.register
def int_to_float(source: int) -> float:
    """Converts an int to a float."""
    return float(source)

@to_float.register
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

@to_path.register   
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

@to_str.register
def int_to_str(source: int) -> str:
    """Converts an int to a str."""
    return str(source)

@to_str.register
def float_to_str(source: float) -> str:
    """Converts an float to a str."""
    return str(source)

@to_str.register 
def list_to_str(source: Listing) -> str:
    """Converts a list to a str."""
    return ', '.join(source)
   
@to_str.register 
def none_to_str(source: None) -> str:
    """Converts None to a str."""
    return 'None'

@to_str.register
def path_to_str(source: pathlib.Path) -> str:
    """Converts a pathlib.Path to a str."""
    return str(source)
