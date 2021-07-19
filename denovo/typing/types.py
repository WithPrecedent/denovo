"""
types:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    catalog (Catalog): a catalog of all Kind subclasses.
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
    hint: ClassVar[Annotated]
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'catalog' dict."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library'.
        catalog[cls.name] = cls

    """ Dunder Methods """
    
    @classmethod
    def __class_getitem__(cls, item) -> str:
        """Returns annotation type for the class."""
        return str(cls.hint[item])
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        return isinstance(instance, denovo.tools.tuplify(cls.comparison))
    
    @classmethod
    def __subclasscheck__(cls, subclass: Type) -> bool:
        return issubclass(subclass, denovo.tools.tuplify(cls.comparison))
    
    
""" Basic Types """
         
@dataclasses.dataclass
class String(Kind):
    
    name: ClassVar[str] = 'string'
    comparison: ClassVar[Union[Type, tuple[Type]]] = str
    hint: ClassVar[Annotated] = str
    
    """ Static Methods """

    @staticmethod
    def from_integer(source: Integer) -> String:
        """Converts an Integer to a String."""
        return denovo.typing.converters.integer_to_string(source = source)

    @staticmethod
    def from_listing(source: Listing) -> String:
        """Converts a Listing to a String."""
        return denovo.typing.converters.listing_to_string(source = source)
    
    @staticmethod
    def from_path(source: Path) -> String:
        """Converts a Path to a String."""
        return denovo.typing.converters.path_to_string(source = source)

    @staticmethod
    def from_real(source: Real) -> String:
        """Converts a Real to a String."""
        return denovo.typing.converters.real_to_string(source = source)
    
    @staticmethod
    def to_dictionary(source: String) -> Dictionary:
        """Converts a String to a dictionary."""
        return denovo.typing.converters.string_to_dictionary(source = source)

    @staticmethod
    def to_path(source: String) -> Path:
        """Converts a String to a Path."""
        return denovo.typing.converters.string_to_path(source = source)

    @staticmethod
    def to_listing(source: String) -> Listing:
        """Converts String to a Listing."""
        return denovo.typing.converters.string_to_listing(source = source)

    @staticmethod
    def to_real(source: String) -> Real:
        """Converts a String to a Real."""
        return denovo.typing.converters.string_to_real(source = source)
    
    
@dataclasses.dataclass
class Path(Kind):
    
    name: ClassVar[str] = 'path'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([pathlib.Path, str])
    hint: ClassVar[Annotated] = Union[pathlib.Path, str]
    
    """ Static Methods """
    
    @staticmethod
    def to_string(source: Path) -> String:
        """Converts a Path to a String."""
        return denovo.typing.converters.path_to_string(source = source)  
       
    
@dataclasses.dataclass
class Index(Kind):
    
    name: ClassVar[str] = 'index'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Hashable
    hint: ClassVar[Annotated] = Hashable


@dataclasses.dataclass
class Integer(Kind):
    
    name: ClassVar[str] = 'integer'
    comparison: ClassVar[Union[Type, tuple[Type]]] = int
    hint: ClassVar[Annotated] = int 
    
    """ Static Methods """
    
    @staticmethod
    def from_real(source: Real) -> Integer:
        """Converts a Real to an Integer."""
        return denovo.typing.converters.real_to_integer(source = source)
    
    @staticmethod
    def from_string(source: String) -> Integer:
        """Converts an Integer to a String."""
        return denovo.typing.converters.string_to_integer(source = source)
        
    @staticmethod
    def to_real(source: Integer) -> Real:
        """Converts an Integer to a String."""
        return denovo.typing.converters.integer_to_real(source = source)
    
    @staticmethod
    def to_string(source: Integer) -> String:
        """Converts an Integer to a String."""
        return denovo.typing.converters.integer_to_string(source = source)


@dataclasses.dataclass
class Real(Kind):
    
    name: ClassVar[str] = 'real'
    comparison: ClassVar[Union[Type, tuple[Type]]] = float
    hint: ClassVar[Annotated] = float
    
    """ Static Methods """
    
    @staticmethod
    def from_real(source: Real) -> Integer:
        """Converts a Real to an Integer."""
        return denovo.typing.converters.real_to_integer(source = source)
    
    @staticmethod
    def from_string(source: String) -> Real:
        """Converts a Real to a String."""
        return denovo.typing.converters.string_to_real(source = source)
        
    @staticmethod
    def to_integer(source: Real) -> Integer:
        """Converts a Real to an Integer."""
        return denovo.typing.converters.real_to_integer(source = source)
    
    @staticmethod
    def to_string(source: Real) -> String:
        """Converts a Real to a String."""
        return denovo.typing.converters.real_to_string(source = source)


""" Container Types """

@dataclasses.dataclass
class Dictionary(Kind):
    
    name: ClassVar[str] = 'dictionary'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableMapping
    hint: ClassVar[Annotated] = MutableMapping[Hashable, Any] 

    """ Static Methods """
    
    @staticmethod
    def from_dyad(source: Dyad) -> Dictionary:
        """Converts a Dyad to a Dictionary."""
        return denovo.typing.converters.dyad_to_dictionary(source = source)   
    
    @staticmethod
    def to_dyad(source: Dictionary) -> Dyad:
        """Converts a Dictionary to a Dyad."""
        return denovo.typing.converters.dictionary_to_dyad(source = source)   
    
    
# @dataclasses.dataclass
# class DefaultDictionary(Kind):
    
#     name: ClassVar[str] = 'default_dictionary'
#     comparison: ClassVar[Union[Type, tuple[Type]]] = MutableMapping
#     hint: ClassVar[Annotated] = MutableMapping[Index, Any]
    
#     """ Dunder Methods """
    
#     @classmethod
#     def __instancecheck__(cls, instance: Any) -> bool:
#         return (isinstance(instance, denovo.tools.tuplify(cls.comparison))
#                 and hasattr(instance, 'default_factory'))

#     """ Static Methods """
    
#     @staticmethod
#     def from_dyad(source: Dyad) -> Dictionary:
#         """Converts a Dyad to a Dictionary."""
#         return denovo.typing.converters.dyad_to_default_dictionary(source = source)   
    
#     @staticmethod
#     def to_dyad(source: Dictionary) -> Dyad:
#         """Converts a Dictionary to a Dyad."""
#         return denovo.typing.converters.dictionary_to_dyad(source = source)   
    

@dataclasses.dataclass
class Chain(Kind, abc.ABC):
    
    name: ClassVar[str] = 'chain'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Sequence
    hint: ClassVar[Annotated] = Sequence 
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        return (isinstance(instance, cls.comparison)
                and not isinstance(instance, String))
        
        
@dataclasses.dataclass
class Listing(Kind):
    
    name: ClassVar[str] = 'listing'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableSequence
    hint: ClassVar[Annotated] = MutableSequence
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        return (isinstance(instance, cls.comparison)
                and not isinstance(instance, String))
            

@dataclasses.dataclass
class Dyad(Kind):
    
    name: ClassVar[str] = 'dyad'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Sequence
    hint: ClassVar[Annotated] = Sequence[Sequence]
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        return (isinstance(instance, denovo.tools.tuplify(cls.comparison)) 
                and len(instance) == 2
                and isinstance(instance[0], cls.comparison)
                and isinstance(instance[1], cls.comparison))


@dataclasses.dataclass
class Group(Kind):
    
    name: ClassVar[str] = 'group'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([set, tuple, Chain])
    hint: ClassVar[Annotated] = Union[set, tuple, Chain]

     
""" Composite Types """

@dataclasses.dataclass
class Adjacency(Kind):
    
    name: ClassVar[str] = 'adjacency'
    comparison: ClassVar[Union[Type, tuple[Type]]] = MutableMapping
    hint: ClassVar[Annotated] = MutableMapping[Hashable, set[Hashable]]    

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        if isinstance(instance, cls.comparison):
            edges = list(instance.values())
            nodes = list(itertools.chain(instance.values()))
            return (all(isinstance(e, (set)) for e in edges)
                    and all(isinstance(n, Hashable) for n in nodes))   
        else:
            return False

             
@dataclasses.dataclass
class Edge(Kind):
    
    name: ClassVar[str] = 'edge'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple
    hint: ClassVar[Annotated] = tuple[Hashable, Hashable]  

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an edge."""
        return (isinstance(instance, cls.comparison)
                and len(instance) == 2 
                and all(isinstance(i, Index) for i in instance))      


@dataclasses.dataclass
class Edges(Kind):
    
    name: ClassVar[str] = 'edges'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Chain
    hint: ClassVar[Annotated] = Sequence[Edge]    

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an edge list."""
        return (isinstance(instance, Listing) 
                and all(isinstance(i, Edge) for i in instance))
 
 
@dataclasses.dataclass
class Connections(Kind):
    
    name: ClassVar[str] = 'connections'
    comparison: ClassVar[Union[Type, tuple[Type]]] = set
    hint: ClassVar[Annotated] = set[Hashable] 

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a set of connections."""
        return (isinstance(instance, Listing) 
                and all(isinstance(i, Edge) for i in instance))       
 
 
@dataclasses.dataclass
class Matrix(Kind):
    
    name: ClassVar[str] = 'matrix'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple
    hint: ClassVar[Annotated] = tuple[MutableSequence[MutableSequence[
        Integer]], MutableSequence[Index]]    

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an adjacency matrix."""
        return (isinstance(instance, cls.comparison) 
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
    hint: ClassVar[Annotated] = Sequence[Index]  

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a pipeline."""
        return (isinstance(instance, cls.comparison)
                and all(isinstance(i, Index) for i in instance))           
 
 
@dataclasses.dataclass
class Pipelines(Kind):
    
    name: ClassVar[str] = 'pipelines'
    comparison: ClassVar[Union[Type, tuple[Type]]] = Chain
    hint: ClassVar[Annotated] = Sequence[Sequence[Index]]   

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a pipeline."""
        return (isinstance(instance, cls.comparison)
                and all(isinstance(i, Index) for i in instance))   


@dataclasses.dataclass
class Nodes(Kind):
    
    name: ClassVar[str] = 'nodes'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([Index, Pipeline])
    hint: ClassVar[Annotated] = Union[Hashable, Sequence] 


@dataclasses.dataclass
class Composite(Kind):
    
    name: ClassVar[str] = 'graphs'
    comparison: ClassVar[Union[Type, tuple[Type]]] = tuple([Adjacency, 
                                                            Edges,
                                                            Matrix, 
                                                            Nodes])
    hint: ClassVar[Annotated] = Union[Adjacency, Edges, Matrix, Nodes]
