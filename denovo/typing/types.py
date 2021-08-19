"""
types: denovo type protocols, aliases, and variables
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:

    
"""
from __future__ import annotations
import abc
from collections.abc import Collection, Hashable, Sequence, MutableMapping
import dataclasses
import inspect
from typing import Any, Optional, Type, TypeVar, Union

import denovo

 
""" Composite Abstract Base Classes """

@dataclasses.dataclass
class Node(denovo.core.containers.Proxy, Hashable): # type: ignore 
    """Vertex wrapper to provide hashability to any object.
    
    Node acts a basic wrapper for any item stored in a denovo Structure. An
    denovo Structure does not require Node instances to be stored. Rather, they
    are offered as a convenient type which is also used internally in denovo.
    
    By inheriting from Proxy, a Node will act as a pass-through class for access
    methods seeking attributes not in a Node instance but rather stored in 
    'contents'.
    
    Args:
        contents (Any): any stored item(s). Defaults to None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout denovo. For example, if a denovo 
            instance needs settings from a settings instance, 'name' should 
            match the appropriate section name in a settings instance. 
            Defaults to None. 
        

    """
    contents: Optional[Any] = None
    name: Optional[str] = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as Node.
        
        This is necessary because dataclasses, by design, do not automatically 
        inherit the hash and equivalance dunder methods from their super 
        classes.
        
        """
        super().__init_subclass__(*args, **kwargs)
        cls.__hash__ = NodeWrapper.__hash__ # type: ignore
        cls.__eq__ = NodeWrapper.__eq__ # type: ignore
        cls.__ne__ = NodeWrapper.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or denovo.tools.snakify(self.__class__.__name__) # type: ignore
                
    """ Dunder Methods """

    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents too Nodes with
        the same name from being used in a composite object that uses a dict as
        its base storage type.
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Makes Node hashable so that it can be used as a key in a dict.

        Args:
            other (object): other object to test for equivalance.
            
        Returns:
            bool: whether 'name' is the same as 'other.name'.
            
        """
        try:
            return str(self.name) == str(other.name) # type: ignore
        except AttributeError:
            return str(self.name) == other

    def __ne__(self, other: object) -> bool:
        """Completes equality test dunder methods.

        Args:
            other (Node): other object to test for equivalance.
           
        Returns:
            bool: whether 'name' is not the same as 'other.name'.
            
        """
        return not(self == other)

    @classmethod
    def __subclasshook__(self, subclass: Type[Any]) -> bool:
        """[summary]

        Args:
            subclass (Type[Any]): [description]

        Returns:
            bool: [description]
            
        """
        return (denovo.tools.is_method(subclass, '__hash__') # type: ignore
                and denovo.tools.is_method(subclass, '__eq__') # type: ignore
                and denovo.tools.is_method(subclass, '__ne__')) # type: ignore
        
    
@dataclasses.dataclass # type: ignore
class Composite(abc.ABC):

    """ Required Methods """
    
    @abc.abstractclassmethod
    def create(cls, source: Any) -> Composite:
        """Creates an instance of a Composite from 'source'.
        
        Args:
            source (Any): supported data structure.
                
        Returns:
            Composite: a Composite instance created based on 'source'.
                
        """
        pass
    
    @abc.abstractmethod 
    def add(self, 
            node: Node,
            ancestors: Optional[Nodes] = None,
            descendants: Optional[Nodes] = None) -> None:
        """Adds 'node' to the stored Composite.
        
        Args:
            node (Node): a node to add to the stored Composite.
            ancestors (Nodes): node(s) from which 'node' should be connected to
                'node'.
            descendants (Nodes): node(s) to which 'node' should be connected to
                'node'.

        """
        pass
    
    @abc.abstractmethod 
    def delete(self, node: Node) -> None:
        """Deletes node from Composite.
        
        Args:
            node (Node): node to delete from 'contents'.
  
        """
        pass
    
    @abc.abstractmethod 
    def merge(self, item: Any) -> None:
        """Adds 'item' to this Composite.

        This method is roughly equivalent to a dict.update, adding nodes to the 
        existing Composite. 
        
        Args:
            item (Any): another Composite or supported data structure.
            
        """
        pass
    
    @abc.abstractmethod 
    def subset(self, 
               include: Optional[Nodes] = None,
               exclude: Optional[Nodes] = None) -> Composite:
        """Returns a Composite with some items removed from 'contents'.
        
        Args:
            include (Optional[Nodes]): nodes to include in the new Composite. 
                Defaults to None.
            exclude (Nodes): nodes to exclude in the new Composite. Defaults to 
                None.
                  
        """
        pass


@dataclasses.dataclass # type: ignore
class Network(Composite, abc.ABC):

    """ Required Methods """
    
    @abc.abstractmethod     
    def connect(self, start: Node, stop: Node) -> None:
        """Adds an edge from 'start' to 'stop'.

        Args:
            start (Node): name of node for edge to start.
            stop (Node): name of node for edge to stop.

        """
        pass
    
    @abc.abstractmethod 
    def disconnect(self, start: Node, stop: Node) -> None:
        """Deletes edge from Composite.

        Args:
            start (Node): starting node for the edge to delete.
            stop (Node): ending node for the edge to delete.

        """
        pass


""" Aliases"""

AdjacencyType = MutableMapping[Node, Union[set[Node], Sequence[Node]]]
ConnectionsType = Collection[Node]
DyadType = tuple[Sequence[Any], Sequence[Any]]
EdgeType = tuple[Node, Node]
EdgesType = Collection[EdgeType]
MatrixType = tuple[Sequence[Sequence[int]], Sequence[Node]]
NodesType = Union[Node, ConnectionsType]
PipelineType = Sequence[Node]
PipelinesType = Collection[PipelineType]

""" Type Variables """

Adjacency = TypeVar('Adjacency', bound = AdjacencyType)
Connections = TypeVar('Connections', bound = ConnectionsType)
Dyad = TypeVar('Dyad', bound = DyadType)
Edge = TypeVar('Edge', bound = EdgeType)
Edges = TypeVar('Edges', bound = EdgesType)
Matrix = TypeVar('Matrix', bound = MatrixType)
Nodes = TypeVar('Nodes', bound = NodesType)
Pipeline = TypeVar('Pipeline', bound = PipelineType)
Pipelines = TypeVar('Pipelines', bound = PipelinesType)
