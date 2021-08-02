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
import dataclasses
import functools
import inspect
import pathlib
import types
from typing import Any, Callable, Optional, Union

import more_itertools

import denovo
from denovo.typing.types import (Adjacency, Composite, Connections, 
                                 Dictionary, Dyad, Edge, Edges, Group, Index, 
                                 Integer, Kind, Listing, Matrix, Nodes, Path, 
                                 Pipeline, Pipelines, Real, String)


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
def to_dictionary(source: Any) -> Dictionary:
    """Converts 'source' to a Dictionary.
    
    Args:
        source (Any): source to convert to a Dictionary.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Dictionary: derived from 'source'.

    """
    if isinstance(source, Dictionary):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_dictionary.register   
def dyad_to_dictionary(source: Dyad) -> Dictionary:
    """Converts a Dyad to a Dictionary."""
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
def dictionary_to_dyad(source: Dictionary) -> Dyad:
    """Converts a Dictionary to a Dyad."""
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
def to_index(source: Any) -> Index:
    """Converts 'source' to an Index.
    
    Args:
        source (Any): source to convert to a Index.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Index: derived from 'source'.

    """
    if isinstance(source, Index):
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
                                    f'an unsupported type: {type(source).__name__}')

@to_index.register
def string_to_index(source: String) -> Index:
    """Converts a String to an Index."""
    return source

@denovo.decorators.dispatcher   
def to_integer(source: Any) -> Integer:
    """Converts 'source' to a Path.
    
    Args:
        source (Any): source to convert to a Integer.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Integer: derived from 'source'.

    """
    if isinstance(source, Integer):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_integer.register
def string_to_integer(source: String) -> Integer:
    """Converts a String to an Integer."""
    return int(source)

@to_integer.register
def real_to_integer(source: Real) -> Integer:
    """Converts a Real to an Integer."""
    return int(source)

@denovo.decorators.dispatcher   
def to_listing(source: Any) -> Listing:
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

@to_listing.register
def string_to_listing(source: String) -> Listing:
    """Converts a String to a Listing."""
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
def to_real(source: Any) -> Real:
    """Converts 'source' to a Real.
    
    Args:
        source (Any): source to convert to a Real.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Real: derived from 'source'.

    """
    if isinstance(source, Real):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_real.register
def integer_to_real(source: Integer) -> Real:
    """Converts an Integer to a Real."""
    return float(source)

@to_real.register
def string_to_real(source: String) -> Real:
    """Converts a String to a Real."""
    return float(source)

@denovo.decorators.dispatcher   
def to_path(source: Any) -> Path:
    """Converts 'source' to a Path.
    
    Args:
        source (Any): source to convert to a Path.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        Path: derived from 'source'.

    """
    if isinstance(source, Path):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_path.register   
def string_to_path(source: String) -> Path:
    """Converts a String to a Path."""
    return pathlib.Path(source)

@denovo.decorators.dispatcher   
def to_string(source: Any) -> String:
    """Converts 'source' to a String.
    
    Args:
        source (Any): source to convert to a String.

    Raises:
        TypeError: if 'source' is a type that is not registered.

    Returns:
        String: derived from 'source'.

    """
    if isinstance(source, String):
        return source
    else:
        raise TypeError(f'source cannot be converted because it is an '
                        f'unsupported type: {type(source).__name__}')

@to_string.register
def integer_to_string(source: Integer) -> String:
    return str(source)

@to_string.register
def real_to_string(source: Real) -> String:
    return str(source)

@to_string.register 
def listing_to_string(source: Listing) -> String:
    return ', '.join(source)
   
@to_string.register 
def none_to_string(source: None) -> String:
    return 'None'

@to_string.register
def path_to_string(source: Path) -> String:
    """Converts a Path to a String."""
    return str(source)
