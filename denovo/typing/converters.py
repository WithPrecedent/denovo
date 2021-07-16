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

    
"""
from __future__ import annotations
import ast
import collections
import functools
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Generic, Hashable, Iterable, 
                    List, Literal, Mapping, MutableMapping, MutableSequence, 
                    Optional, Sequence, Set, Tuple, Type, TypeVar, Union)

import more_itertools

import denovo
from denovo.typing.types import (Adjacency, Chain, Composite, Connections, 
                                 DefaultDictionary, Dictionary, Dyad, Edge, 
                                 Edges, Group, Index, Integer, Kind, Listing, 
                                 Matrix, Nodes, Path, Pipeline, Pipelines, Real, 
                                 String)


""" String Format Templates for Converter Function Names """

FLEXIBLE: Callable = lambda: 'to_{}'.format
STRICT: Callable = lambda: '{}_to_{}'.format

""" Converter Registry and Registry Decorator """

catalog: denovo.containers.Catalog = denovo.containers.Catalog()

def converter(func: Callable) -> Callable:
    """Decorator for a converter registry.
    
    Args:
        func (Callable): an callable converter.
        
    Returns:
        Callable: with passed arguments.
        
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        catalog[name] = func
        return func(*args, **kwargs)
    return wrapper


""" Strict Simple Converters """

@converter
def dyad_to_dictionary(source: Dyad) -> Dictionary:
    """Converts a Dyad to a Dictionary."""
    return dict(zip(source))

@converter
def dyad_to_default_dictionary(source: Dyad, 
        default_factory: Any = None) -> DefaultDictionary:
    """Converts a Dyad to a DefaultDictionary."""
    return collections.defaultdict(default_factory, dict(zip(source)))

@converter
def integer_to_real(source: Integer) -> Real:
    """Converts an Integer to a Float."""
    return float(source)

@converter
def integer_to_string(source: Integer) -> String:
    """Converts an Integer to a String."""
    return str(source)

@converter
def listing_to_string(source: Listing) -> String:
    """Converts a Listing to a String."""
    return ', '.join(source)

@converter
def real_to_integer(source: Real) -> Integer:
    """Converts a Real to an Integer."""
    return int(source)

@converter
def real_to_string(source: Real) -> String:
    """Converts an Real to a String."""
    return str(source)

@converter
def string_to_integer(source: String) -> Integer:
    """Converts a String to an Integer."""
    return int(source)

@converter
def string_to_dictionary(source: String) -> Dictionary:
    """Convets a String to a dictionary."""
    return ast.literal_eval(source)

@converter
def string_to_disk(source: String) -> Path:
    """Converts a String to a Path."""
    return pathlib.Path(source)

@converter
def string_to_listing(source: String) -> Listing:
    """Converts String to a Listing."""
    return ast.literal_eval(source)

@converter
def string_to_real(source: String) -> Real:
    """Converts a String to an Real."""
    return float(source)

""" Strict Composite Converters """

@converter
def adjacency_to_edges(source: Adjacency) -> Edges:
    """Converts an adjacency list to an edge list."""
    edges = []
    for node, connections in source.items():
        for connection in connections:
            edges.append(tuple(node, connection))
    return edges

@converter
def adjacency_to_matrix(source: Adjacency) -> Matrix:
    """Converts an adjacency list to an adjacency matrix."""
    names = list(source.keys())
    matrix = []
    for i in range(len(source)): 
        matrix.append([0] * len(source))
        for j in source[i]:
            matrix[i][j] = 1
    return tuple(matrix, names)

@converter
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

@converter
def matrix_to_adjacency(source: Matrix) -> Adjacency:
    """Converts adjacency matrix to an adjacency list."""
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

@converter
def pipeline_to_adjacency(source: Pipeline) -> Adjacency:
    """Converts a pipeline to an adjacency list."""
    adjacency = collections.defaultdict(set)
    edges = more_itertools.windowed(source, 2)
    for edge_pair in edges:
        adjacency[edge_pair[0]] = {edge_pair[1]}
    return adjacency

""" Flexible Converters """

@converter
def to_index(source: Any) -> Index:
    return hash(source)

@converter     
def to_string(source: Any) -> String:
    """Converts 'source' to a String.
    
    Args:
        source (Any): source to convert to a String.

    Returns:
        String: derived from 'source'.

    """
    if source is None:
        return 'None'
    elif isinstance(source, Listing):
        return listing_to_string(source = source)
    elif isinstance(source, String):
        return source
    else:
        return str(source)

@converter    
def to_dictionary(source: Any) -> Dictionary:
    if isinstance(source, String):
    try:
        return ast.literal_eval()
    except Tu