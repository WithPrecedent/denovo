"""
types:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    Adjacency (Type): annotation type for an adjacency list.
    Matrix (Type): annotation type for an adjacency matrix.
    Edge (Type): annotation type for a tuple of edge endpoints.
    Edges (Type): annotation type for an edge list.
    Pipeline (Type): annotation type for a pipeline.
    Pipelines (Type): annotation type for pipelines.
    Nodes (Type): annotation type for one or more nodes.

ToDo:
    add date types and appropriate conversion functions
    Combine 'comparison' and 'annotation' attributes for Kind to allow using
        type hints for instance and subclass checks (and removing the need for
        'annotation' attribute inclusion in type hints). First stab with
        Typeguard didn't work, but it might be a good tool to try again.
    Add adaptations for post 3.9 depreciation of various annotation types in the
        typing module.
    
"""
from __future__ import annotations
import abc
import dataclasses
import itertools
import pathlib
from typing import (Annotated, Any, Callable, ClassVar, Dict, Generic, Hashable, 
                    Iterable, List, Literal, Mapping, MutableMapping, 
                    MutableSequence, Optional, Sequence, Set, Text, Tuple, 
                    Type, TypeVar, Union)

import more_itertools

import denovo


KindType = TypeVar('KindType')

kinds: Dict[str, Kind] = {}


""" Base Type """

@dataclasses.dataclass
class Kind(Generic[KindType], abc.ABC):
    """Base class for generic types used by denovo.
    
    Args:
    
    
    """
    name: ClassVar[str]
    comparison: ClassVar[Union[Type, Tuple[Type]]]
    annotation: ClassVar[Annotated]
    sources: ClassVar[Tuple[Kind]]
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'kinds' dict."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library'.
        kinds[cls.name] = cls

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
    comparison: ClassVar[Union[Type, Tuple[Type]]] = str
    annotation: ClassVar[Annotated] = Text
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Listing])   

    
@dataclasses.dataclass
class Path(Kind):
    
    name: ClassVar[str] = 'disk'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = pathlib.Path
    annotation: ClassVar[Annotated] = pathlib.Path
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([String])  
   
             
@dataclasses.dataclass
class Index(Kind):
    
    name: ClassVar[str] = 'index'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Hashable
    annotation: ClassVar[Annotated] = Hashable
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])  


@dataclasses.dataclass
class Integer(Kind):
    
    name: ClassVar[str] = 'integer'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = int
    annotation: ClassVar[Annotated] = int
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Real, String]) 


@dataclasses.dataclass
class Real(Kind):
    
    name: ClassVar[str] = 'real'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = float
    annotation: ClassVar[Annotated] = float
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Integer, String]) 


""" Container Types """

@dataclasses.dataclass
class Dictionary(Kind):
    
    name: ClassVar[str] = 'dictionary'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableMapping
    annotation: ClassVar[Annotated] = MutableMapping[Hashable, Any]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Dyad])    


@dataclasses.dataclass
class DefaultDictionary(Kind):
    
    name: ClassVar[str] = 'default_dictionary'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableMapping
    annotation: ClassVar[Annotated] = MutableMapping[Index, Any]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Dyad])
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, denovo.tools.tuplify(self.comparison))
                and hasattr(instance, 'default_factory'))


@dataclasses.dataclass
class Chain(Kind, abc.ABC):
    
    name: ClassVar[str] = 'chain'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Sequence
    annotation: ClassVar[Annotated] = Sequence 
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([String])  
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, self.comparison)
                and not isinstance(instance, String))
        
        
@dataclasses.dataclass
class Listing(Kind):
    
    name: ClassVar[str] = 'listing'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableSequence
    annotation: ClassVar[Annotated] = MutableSequence
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([String]) 
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, self.comparison)
                and not isinstance(instance, String))
            

@dataclasses.dataclass
class Dyad(Kind):
    
    name: ClassVar[str] = 'dyad'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableSequence
    annotation: ClassVar[Annotated] = MutableSequence
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([String]) 
    
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
    comparison: ClassVar[Union[Type, Tuple[Type]]] = tuple([Set, Tuple, Chain])
    annotation: ClassVar[Annotated] = Union[Set, Tuple, Chain]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Chain])  

     
""" Composite Types """

@dataclasses.dataclass
class Adjacency(Kind):
    
    name: ClassVar[str] = 'adjacency'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableMapping
    annotation: ClassVar[Annotated] = MutableMapping[Hashable, Set[Hashable]]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Edges, Matrix, Nodes])     

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
    comparison: ClassVar[Union[Type, Tuple[Type]]] = tuple
    annotation: ClassVar[Annotated] = Tuple[Hashable, Hashable]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])     

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
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Chain
    annotation: ClassVar[Annotated] = Sequence[Edge]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Adjacency, Matrix, Nodes])     

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is an edge list."""
        return (isinstance(instance, Listing) 
                and all(isinstance(i, Edge) for i in instance))
 
 
@dataclasses.dataclass
class Connections(Kind):
    
    name: ClassVar[str] = 'connections'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Set
    annotation: ClassVar[Annotated] = Set[Hashable]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])     

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is a set of connections."""
        return (isinstance(instance, Listing) 
                and all(isinstance(i, Edge) for i in instance))       
 
 
@dataclasses.dataclass
class Matrix(Kind):
    
    name: ClassVar[str] = 'matrix'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = tuple
    annotation: ClassVar[Annotated] = Tuple[MutableSequence[MutableSequence[
        Integer]], MutableSequence[Index]]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Adjacency, Edges, Nodes])     

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
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Chain
    annotation: ClassVar[Annotated] = Sequence[Index]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])     

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is a pipeline."""
        return (isinstance(instance, self.comparison)
                and all(isinstance(i, Index) for i in instance))           
 
 
@dataclasses.dataclass
class Pipelines(Kind):
    
    name: ClassVar[str] = 'pipelines'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Chain
    annotation: ClassVar[Annotated] = Sequence[Sequence[Index]]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])     

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        """Returns whether 'instance' is a pipeline."""
        return (isinstance(instance, self.comparison)
                and all(isinstance(i, Index) for i in instance))   


@dataclasses.dataclass
class Nodes(Kind):
    
    name: ClassVar[str] = 'nodes'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = tuple([Index, Pipeline])
    annotation: ClassVar[Annotated] = Union[Hashable, Sequence]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])     


@dataclasses.dataclass
class Composite(Kind):
    
    name: ClassVar[str] = 'graphs'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = tuple([Adjacency, 
                                                            Edges,
                                                            Matrix, 
                                                            Nodes])
    annotation: ClassVar[Annotated] = Union[Adjacency, Edges, Matrix, Nodes]
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([])   

