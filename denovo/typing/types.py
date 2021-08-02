"""
types:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    catalog (Catalog): a catalog of all Kind subclasses.
    Kind (KindType, ABC): base class for denovo typing system.
    
    Adjacency (Kind, Protocol): annotation type for an adjacency list.
    Matrix (Kind, Protocol): annotation type for an adjacency matrix.
    Edge (Kind, Protocol): annotation type for a tuple of edge endpoints.
    Edges (Kind, Protocol): annotation type for an edge list.
    Pipeline (Kind, Protocol): annotation type for a pipeline.
    Pipelines (Kind, Protocol): annotation type for pipelines.
    Nodes (Kind, Protocol): annotation type for one or more nodes.

ToDo:
    Add date types and appropriate conversion functions
    Combine 'comparison' and 'hint' attributes for Kind to allow using
        type hints for instance and subclass checks (and removing the need for
        'hint' attribute inclusion in type hints). First stab with
        Typeguard didn't work, but it might be a good tool to try again.
    Finish convenience staticmethods
    
"""
from __future__ import annotations
import abc
from collections.abc import (Container, Hashable, Iterable, Iterator, 
                             Generator, Callable, Collection, Sequence, 
                             MutableSequence, MutableSet, Mapping, 
                             MutableMapping, MappingView, ItemsView, KeysView, 
                             ValuesView)
import dataclasses
import itertools
import pathlib
from types import GenericAlias
from typing import (Annotated, Any, ClassVar, Literal, Optional, Protocol, Type,
                    TypeVar, Union, runtime_checkable)

import more_itertools

import denovo


catalog: denovo.containers.Catalog = denovo.containers.Catalog()



""" Base Protocol """

@dataclasses.dataclass
class Kind(abc.ABC):
    """Base class for generic types used by denovo.
    
    Args:
    
    
    """
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, *args, **kwargs):
        """Adds 'cls' to 'catalog' dict."""
        super().__init_subclass__(*args, **kwargs)
        # Adds subclasses to 'catalog'.
        name = denovo.tools.snakify(cls.__name__)
        catalog[cls.name] = name
        # Stores 'name' in '__name__' to make Kind subclasses act the same as
        # builtin python types.
        cls.__name__ = name


""" General Protocols and Type Aliases """


@dataclasses.dataclass
class Listing(Kind):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a Listing."""
        return (isinstance(instance, MutableSequence) 
                and not isinstance(instance, str))
    

Group: Type = Union[set, tuple, Listing]
        

@dataclasses.dataclass
class Dyad(Protocol[Listing[Listing]]):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Dyad."""
        return (isinstance(instance, denovo.tools.tuplify(Listing)) 
                and len(instance) == 2
                and isinstance(instance[0], Listing)
                and isinstance(instance[1], Listing))


""" Structure Protocols and Type Aliases """


@runtime_checkable
class Adjacency(Protocol[MutableMapping]):
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Adjacency."""
        if isinstance(instance, MutableMapping):
            edges = list(instance.values())
            nodes = list(itertools.chain(instance.values()))
            return (all(isinstance(e, (set)) for e in edges)
                    and all(isinstance(n, Hashable) for n in nodes))   
        else:
            return False


@runtime_checkable
class Connections(Protocol[set[Hashable]]):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Connections."""
        return (isinstance(instance, set) 
                and all(isinstance(i, Hashable) for i in instance))       
 
             
@runtime_checkable
class Edge(Protocol[tuple[Hashable]]):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Edge."""
        return (isinstance(instance, tuple)
                and len(instance) == 2 
                and all(isinstance(i, Hashable) for i in instance))      


@runtime_checkable
class Edges(Protocol[Listing[Edge]]):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Edges."""
        return (isinstance(instance, Group) 
                and all(isinstance(i, Edge) for i in instance))
 

@runtime_checkable
class Matrix(Protocol[tuple]):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Matrix."""
        return (isinstance(instance, tuple) 
                and len(instance) == 2
                and isinstance(instance[1], Sequence) 
                and all(isinstance(i, Sequence) for i in instance[0])
                and all(isinstance(n, Hashable) for n in instance[1])
                and all(isinstance(e, int) 
                        for e in list(more_itertools.collapse(instance[0]))))
 
@runtime_checkable
class Pipeline(Protocol[Listing[Hashable]]):
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Pipeline."""
        return (isinstance(instance, Listing)
                and all(isinstance(i, Hashable) for i in instance))           
 
 
@runtime_checkable
class Pipelines(Protocol[Group[Pipeline]]):

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Pipelines."""
        return (isinstance(instance, Group)
                and all(isinstance(i, Pipeline) for i in instance))   


Nodes: Type = Union[Hashable, Pipeline]

Composite: Type = Union[Adjacency, Edges,Matrix, Nodes]
