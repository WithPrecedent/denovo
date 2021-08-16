"""
types: denovo type protocols and type aliases
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:

    
"""
from __future__ import annotations
from collections.abc import Collection, Sequence, MutableMapping
from typing import Any, Optional, Protocol, TypeVar, Union, runtime_checkable

 
""" Composite Protocols """
        
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


""" Aliases"""

AdjacencyType = MutableMapping[Node, Union[set[Node], Sequence[Node]]]
ConnectionsType = Collection[Node]
DyadType = tuple[Sequence, Sequence]
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
