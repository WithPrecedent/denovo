"""
types:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    KindType (TypeVar): Base generic type for denovo typing system.
    Kind (KindType, ABC): base class for denovo typing system.
    
    Adjacency (Kind): annotation type for an adjacency list.
    Matrix (Kind): annotation type for an adjacency matrix.
    Edge (Kind): annotation type for a tuple of edge endpoints.
    Edges (Kind): annotation type for an edge list.
    Pipeline (Kind): annotation type for a pipeline.
    Pipelines (Kind): annotation type for pipelines.
    Nodes (Kind): annotation type for one or more nodes.

ToDo:
    Add date types and appropriate conversion functions
    Combine 'comparison' and 'annotation' attributes for Kind to allow using
        type hints for instance and subclass checks (and removing the need for
        'annotation' attribute inclusion in type hints). First stab with
        Typeguard didn't work, but it might be a good tool to try again.
    Add adaptations for post 3.9 depreciation of various annotation types in the
        typing module.
    
"""
from __future__ import annotations
import abc
from collections.abc import (Container, Hashable, Iterable, Iterator, 
                             Generator, Callable, Collection, Sequence, 
                             MutableSequence, Set, MutableSet, Mapping, 
                             MutableMapping, MappingView, ItemsView, KeysView, 
                             ValuesView)
import dataclasses
import itertools
import pathlib
from typing import (Annotated, Any, ClassVar, Generic, Literal, Optional, Type,
                    TypeVar, Union)

import more_itertools

import denovo


catalog: denovo.containers.Catalog = denovo.containers.Catalog()


""" Base Type """

@dataclasses.dataclass
class Kind(abc.ABC):
    """Base class for generic types used by denovo.
    
    Args:
    
    
    """
    name: ClassVar[str]
    comparison: ClassVar[Union[Type, tuple[Type]]]
    annotation: ClassVar[Annotated]
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'catalog' dict."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library'.
        catalog[cls.name] = cls

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return isinstance(instance, denovo.tools.tuplify(self.comparison))
    
    @classmethod
    def __subclasscheck__(self, subclass: Type) -> bool:
        return issubclass(subclass, denovo.tools.tuplify(self.comparison))
    
    
""" Basic Types """
         
@dataclasses.dataclass
class String(Kind):
    
    name: ClassVar[str] = 'string'
    comparison: ClassVar[Union[Type, tuple[Type]]] = str
    annotation: ClassVar[Annotated] = str

    
@dataclasses.dataclass
class Path(Kind):
    
    name: ClassVar[str] = 'disk'
    comparison: ClassVar[Union[Type, tuple[Type]]] = pathlib.Path
    annotation: ClassVar[Annotated] = pathlib.Path
   
             
@dataclasses.dataclass
class Index(Kind):
    
    name: ClassVar[str] = 'index'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Hashable
    annotation: ClassVar[Annotated] = Hashable


@dataclasses.dataclass
class Integer(Kind):
    
    name: ClassVar[str] = 'integer'
    comparison: ClassVar[Union[Type, tuple[Type]]] = int
    annotation: ClassVar[Annotated] = int 


@dataclasses.dataclass
class Real(Kind):
    
    name: ClassVar[str] = 'real'
    comparison: ClassVar[Union[Type, tuple[Type]]] = float
    annotation: ClassVar[Annotated] = float


""" Container Types """

@dataclasses.dataclass
class Dictionary(Kind):
    
    name: ClassVar[str] = 'dictionary'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableMapping
    annotation: ClassVar[Annotated] = MutableMapping[Hashable, Any] 


@dataclasses.dataclass
class DefaultDictionary(Kind):
    
    name: ClassVar[str] = 'default_dictionary'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableMapping
    annotation: ClassVar[Annotated] = MutableMapping[Index, Any]
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, denovo.tools.tuplify(self.comparison))
                and hasattr(instance, 'default_factory'))


@dataclasses.dataclass
class Chain(Kind, abc.ABC):
    
    name: ClassVar[str] = 'chain'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Sequence
    annotation: ClassVar[Annotated] = Sequence 
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, self.comparison)
                and not isinstance(instance, String))
        
        
@dataclasses.dataclass
class Listing(Kind):
    
    name: ClassVar[str] = 'listing'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableSequence
    annotation: ClassVar[Annotated] = MutableSequence
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, self.comparison)
                and not isinstance(instance, String))
            

@dataclasses.dataclass
class Dyad(Kind):
    
    name: ClassVar[str] = 'dyad'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Sequence
    annotation: ClassVar[Annotated] = Sequence[Sequence]
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, denovo.tools.tuplify(self.comparison)) 
                and len(instance) == 2
                and isinstance(instance[0], self.comparison)
                and isinstance(instance[1], self.comparison))


@dataclasses.dataclass
class Group(Kind):
    
    name: ClassVar[str] = 'group'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([Set, tuple, Chain])
    annotation: ClassVar[Annotated] = Union[Set, tuple, Chain]

     
""" Composite Types """

@dataclasses.dataclass
class Adjacency(Kind):
    
    name: ClassVar[str] = 'adjacency'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableMapping
    annotation: ClassVar[Annotated] = MutableMapping[Hashable, Set[Hashable]]    

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        if isinstance(instance, self.comparison):
            edges = list(instance.values())
            nodes = list(itertools.chain(instance.values()))
            return (all(isinstance(e, (Set)) for e in edges)
                    and all(isinstance(n, Hashable) for n in nodes))   
        else:
            return False

             
@dataclasses.dataclass
class Edge(Kind):
    
    name: ClassVar[str] = 'edge'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple
    annotation: ClassVar[Annotated] = tuple[Hashable, Hashable]  

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is an edge."""
        return (isinstance(instance, self.comparison)
                and len(instance) == 2 
                and all(isinstance(i, Index) for i in instance))      


@dataclasses.dataclass
class Edges(Kind):
    
    name: ClassVar[str] = 'edges'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Chain
    annotation: ClassVar[Annotated] = Sequence[Edge]    

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is an edge list."""
        return (isinstance(instance, Listing) 
                and all(isinstance(i, Edge) for i in instance))
 
 
@dataclasses.dataclass
class Connections(Kind):
    
    name: ClassVar[str] = 'connections'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Set
    annotation: ClassVar[Annotated] = Set[Hashable] 

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is a set of connections."""
        return (isinstance(instance, Listing) 
                and all(isinstance(i, Edge) for i in instance))       
 
 
@dataclasses.dataclass
class Matrix(Kind):
    
    name: ClassVar[str] = 'matrix'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple
    annotation: ClassVar[Annotated] = tuple[MutableSequence[MutableSequence[
        Integer]], MutableSequence[Index]]    

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is an adjacency matrix."""
        return (isinstance(instance, self.comparison) 
                and len(instance) == 2
                and isinstance(instance[1], Sequence) 
                and all(isinstance(i, Sequence) for i in instance[0])
                and all(isinstance(n, Index) for n in instance[1])
                and all(isinstance(e, Integer) 
                        for e in list(more_itertools.collapse(instance[0]))))
 
 
@dataclasses.dataclass
class Pipeline(Kind):
    
    name: ClassVar[str] = 'pipeline'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Chain
    annotation: ClassVar[Annotated] = Sequence[Index]  

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is a pipeline."""
        return (isinstance(instance, self.comparison)
                and all(isinstance(i, Index) for i in instance))           
 
 
@dataclasses.dataclass
class Pipelines(Kind):
    
    name: ClassVar[str] = 'pipelines'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Chain
    annotation: ClassVar[Annotated] = Sequence[Sequence[Index]]   

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is a pipeline."""
        return (isinstance(instance, self.comparison)
                and all(isinstance(i, Index) for i in instance))   


@dataclasses.dataclass
class Nodes(Kind):
    
    name: ClassVar[str] = 'nodes'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([Index, Pipeline])
    annotation: ClassVar[Annotated] = Union[Hashable, Sequence] 


@dataclasses.dataclass
class Composite(Kind):
    
    name: ClassVar[str] = 'graphs'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([Adjacency, 
                                                            Edges,
                                                            Matrix, 
                                                            Nodes])
    annotation: ClassVar[Annotated] = Union[Adjacency, Edges, Matrix, Nodes]
