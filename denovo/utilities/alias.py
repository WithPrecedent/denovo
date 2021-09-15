"""
alias: simple denovo type aliases
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Operation: generic, flexible Callable type alias.
    Signatures: dict of Signatures type.
    Wrappable: type for an item that can be wrapped by a decorator.
    Type Variables:
        Adjacency (TypeVar): defines a raw adjacency list type.
        Connections (TypeVar): defines set of network connections type.
        Dyad (TypeVar): defines a double sequence type.
        Edge (TypeVar): defines a composite edge.
        Edges (TypeVar): defines a collection of Edges.
        Matrix (TypeVar): defines a raw adjacency matrix type.
        Nodes (TypeVar): defines a type for a single Node or a collection of 
            Nodes.
        Pipeline (TypeVar): defines a sequence of Nodes.
        Pipelines (TypeVar): defines a collection of Pipelines.
    
"""
from __future__ import annotations
from collections.abc import Hashable, MutableMapping

import inspect
from typing import Any, Callable, Type, Union


""" Type Aliases """

# Alias for a generic dict with no type restrictions.
Dictionary = MutableMapping[Hashable, Any]
# Simpler alias for generic callable.
Operation = Callable[..., Any]
# Shorter alias for a dict of Signature types.
Signatures = MutableMapping[str, inspect.Signature]
# Shorter alias for things that can be wrapped.
Wrappable = Union[object, Type[Any], Operation]

""" Type Variables """

# Adjacency = TypeVar(
#     'Adjacency', 
#     bound = MutableMapping[Node, Union[set[Node], Sequence[Node]]])
# Connections = TypeVar(
#     'Connections', 
#     bound = Collection[Node])
# Dyad = TypeVar(
#     'Dyad', 
#     bound = tuple[Sequence[Any], Sequence[Any]])
# Edge = TypeVar(
#     'Edge', 
#     bound = tuple[Node, Node])
# Edges = TypeVar(
#     'Edges', 
#     bound = Collection[tuple[Node, Node]])
# Matrix = TypeVar(
#     'Matrix', 
#     bound = tuple[Sequence[Sequence[int]], Sequence[Node]])
# Nodes = TypeVar(
#     'Nodes', 
#     bound = Union[Node, Collection[Node]])
# Pipeline = TypeVar(
#     'Pipeline', 
#     bound = Sequence[Node])
# Pipelines = TypeVar(
#     'Pipelines', 
#     bound = Collection[Sequence[Node]])



# """ Aliases"""

# _AdjacencyType = MutableMapping[Node, Union[set[Node], Sequence[Node]]]
# _ConnectionsType = Collection[Node]
# _DyadType = tuple[Sequence[Any], Sequence[Any]]
# _EdgeType = tuple[Node, Node]
# _EdgesType = Collection[_EdgeType]
# _MatrixType = tuple[Sequence[Sequence[int]], Sequence[Node]]
# _NodesType = Union[Node, _ConnectionsType]
# _PipelineType = Sequence[Node]
# _PipelinesType = Collection[_PipelineType]

# """ Type Variables """

# Adjacency = TypeVar('Adjacency', bound = _AdjacencyType)
# Connections = TypeVar('Connections', bound = _ConnectionsType)
# Dyad = TypeVar('Dyad', bound = _DyadType)
# Edge = TypeVar('Edge', bound = _EdgeType)
# Edges = TypeVar('Edges', bound = _EdgesType)
# Matrix = TypeVar('Matrix', bound = _MatrixType)
# Nodes = TypeVar('Nodes', bound = _NodesType)
# Pipeline = TypeVar('Pipeline', bound = _PipelineType)
# Pipelines = TypeVar('Pipelines', bound = _PipelinesType)

# for item in ['Adjacency', 'Connections', 'Dyad', 'Edge', 'Edges', 'Matrix', 
#              'Nodes', 'Pipeline', 'Pipelines']:
#     print(denovo.modify.snakify(item))
#     print(item)
#     name = denovo.modify.snakify(item)
#     # kind = globals()[f'_{item}Type']
#     kind = globals()[item]
#     denovo.framework.Kind.register(item = kind, name = name)