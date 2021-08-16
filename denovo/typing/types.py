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
from typing import (Annotated, Any, ClassVar, Literal, Optional, Protocol, Type,
                    TypeVar, Union, runtime_checkable)
from typing_extensions import runtime

import more_itertools

import denovo


catalog: denovo.containers.Catalog = denovo.containers.Catalog() # type: ignore


""" Base Protocol """

class Kind(abc.ABC):
    """Base class for type protocols used by denovo."""
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, 
                          *args: Optional[tuple[Any, ...]], 
                          **kwargs: Optional[dict[Hashable, Any]]) -> None:
        """Adds 'cls' to 'catalog' dict."""
        super().__init_subclass__(*args, **kwargs) # type: ignore
        # Adds subclasses to 'catalog' amd 'names'.
        name = denovo.utilities.tools.snakify(cls.__name__)
        catalog[name] = cls
        # Stores 'name' in '__name__' to make Kind subclasses act the same as
        # builtin python types.
        if not hasattr(cls, '__name__') or not cls.__name__:
            cls.__name__ = name


""" Basic Protocols, Types, and Type Aliases """

    
class Group(Collection[Any], Kind, abc.ABC):
    """Collection (not necessarily ordered) protocol that excludes strings."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a Group."""
        return (isinstance(instance, Collection) 
                and not isinstance(instance, str))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Group."""
        return (issubclass(subclass, Collection) 
                and not issubclass(subclass, str))
 
 
class Listing(MutableSequence[Any], Kind, abc.ABC):
    """MutableSequence protocol that excludes strings."""
    
    __name__: str = 'list'
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a Listing."""
        return (isinstance(instance, MutableSequence) 
                and not isinstance(instance, str))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Listing."""
        return (issubclass(subclass, MutableSequence) 
                and not issubclass(subclass, str))


class Order(Sequence[Any], Kind, abc.ABC):
    """Sequence protocol that excludes strings."""
    
    __name__: str = 'tuple'
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is a Sequence."""
        return (isinstance(instance, Sequence) 
                and not isinstance(instance, str))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Sequence."""
        return (issubclass(subclass, Sequence) 
                and not issubclass(subclass, str))
 

class Repeater(Iterable[Any], Kind, abc.ABC):
    """Iterable protocol that excludes strings."""
    
    __name__: str = 'Iterable'
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an Iterable."""
        return (isinstance(instance, Iterable) 
                and not isinstance(instance, str))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is an Iterable."""
        return (issubclass(subclass, Iterable) 
                and not issubclass(subclass, str))
        
   
class Dyad(Kind):
    """Protocol for two Orders that may be zipped into a dict."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Dyad."""
        return (isinstance(instance, Order) 
                and len(instance) == 2
                and isinstance(instance[0], Order)
                and isinstance(instance[1], Order))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Dyad."""
        return (issubclass(subclass, Order) 
                and not issubclass(subclass, str))
     
         
""" Composite Protocols, Types, and Type Aliases """
   
        
@runtime_checkable
class Node(Protocol):
    """Protocol requirements for a Node in a Composite."""
        
    """ Required Methods """

    def __hash__(self) -> int:
        """Nodes must be hashable for indexing.
        
        Returns:
            int: to identify node.
            
        """
        pass

    def __eq__(self, other: Node) -> bool:
        """Nodes must be able to be compared.

        Args:
            other (Node): other Node instance to test for equivalance.
            
        Returns:
            bool: of whether the 'other' and self are equivalent.
            
        """
        pass

    def __ne__(self, other: Node) -> bool:
        """Nodes must be able to be compared.

        Args:
            other (Node): other Node instance to test for equivalance.
            
        Returns:
            bool: of whether the 'other' and self are not equivalent.
            
        """
        pass

    def __str__(self) -> str:
        """Nodes must be able to be represented as strings."""
        pass   

   
@runtime_checkable
class Composite(Protocol):
    
    contents: Repeater
      
    """ Required Methods """
    
    @classmethod
    def create(cls, source: Any) -> Composite:
        """Creates an instance of a Composite from 'source'.
        
        Args:
            source (Any): supported data structure.
                
        Returns:
            Composite: a Composite instance created based on 'source'.
                
        """
        pass
       
    def add(self, 
            node: Node,
            ancestors: Optional[Union[Node, Pipeline]] = None,
            descendants: Optional[Union[Node, Pipeline]] = None) -> None:
        """Adds 'node' to the stored Composite.
        
        Args:
            node (Node): a node to add to the stored Composite.
            ancestors (Union[Node, Pipeline]): node(s) from which 'node' should 
                be connected.
            descendants (Union[Node, Pipeline]): node(s) to which 'node' should 
                be connected.

        """
        pass

    def connect(self, start: Node, stop: Node) -> None:
        """Adds an edge from 'start' to 'stop'.

        Args:
            start (Node): name of node for edge to start.
            stop (Node): name of node for edge to stop.

        """
        pass

    def delete(self, node: Node) -> None:
        """Deletes node from Composite.
        
        Args:
            node (Node): node to delete from 'contents'.
  
        """
        pass

    def disconnect(self, start: Node, stop: Node) -> None:
        """Deletes edge from Composite.

        Args:
            start (Node): starting node for the edge to delete.
            stop (Node): ending node for the edge to delete.

        """
        pass

    def merge(self, item: Any) -> None:
        """Adds 'item' to this Composite.

        This method is roughly equivalent to a dict.update, adding nodes to the 
        existing Composite. 
        
        Args:
            item (Any): another Composite or supported data structure.
            
        """
        pass

    def subset(self, 
               include: Optional[Group] = None,
               exclude: Optional[Group] = None) -> Composite:
        """Returns a Composite with some items removed from 'contents'.
        
        Args:
            include (Optional[Group]): nodes to include in the new Composite.
                Defaults to None.
            exclude (Group[Node]): nodes to exclude in the new Composite.
                Defaults to None.
                  
        """
        pass


class Adjacency(Kind):
    """Protocol for an adjacency list representation of a Composite."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Adjacency."""
        if isinstance(instance, MutableMapping):
            edges = list(instance.values())
            nodes = list(itertools.chain(instance.values()))
            return (all(isinstance(e, (set)) for e in edges)
                    and all(isinstance(n, Node) for n in nodes))   
        else:
            return False

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is an Adjacency."""
        return issubclass(subclass, MutableMapping)
        

class Connections(Kind):
    """Protocol for a Group of hashable items in a composite structure."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Connections."""
        return (isinstance(instance, Group) 
                and all(isinstance(i, Node) for i in instance))       

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Connections."""
        return issubclass(subclass, Group)
    
                
class Edge(Kind):
    """Protocol for an edge in a Composite."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Edge."""
        return (isinstance(instance, tuple)
                and len(instance) == 2 
                and all(isinstance(i, Node) for i in instance))      

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is an Edge."""
        return issubclass(subclass, tuple)
    

class Edges(Kind):
    """Protocol for a Group of Edge in a Composite."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Edges."""
        return (isinstance(instance, Group) 
                and all(isinstance(i, Edge) for i in instance))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is an Edges."""
        return issubclass(subclass, Group)
     

class Matrix(Kind):
    """Protocol for an adjacency matrix representation of a Composite."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Matrix."""
        return (isinstance(instance, tuple) 
                and len(instance) == 2
                and isinstance(instance[1], Order) 
                and all(isinstance(i, Order) for i in instance[0])
                and all(isinstance(n, Node) for n in instance[1])
                and all(isinstance(e, int) 
                        for e in list(more_itertools.collapse(instance[0]))))

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Matrix."""
        return issubclass(subclass, tuple)
       

class Pipeline(Kind):
    """Protocol for an Order of hashable items."""
        
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Pipeline."""
        return (isinstance(instance, Order)
                and all(isinstance(i, Node) for i in instance))           

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Pipeline."""
        return issubclass(subclass, Order)
     
 
class Pipelines(Kind):
    """Protocol for a Group of Pipeline."""
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Returns whether 'instance' is an instance of Pipelines."""
        return (isinstance(instance, Group)
                and all(isinstance(i, Pipeline) for i in instance))   

    @classmethod
    def __subclasscheck__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a Pipelines."""
        return issubclass(subclass, Group)
    

Nodes = Union[Node, Connections]   
