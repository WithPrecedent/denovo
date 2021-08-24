"""
types: denovo type protocols, aliases, and variables
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:

    
"""
from __future__ import annotations
import abc
from collections.abc import (Collection, Hashable, Iterable, Iterator, Sequence, 
                             MutableMapping)
import dataclasses
import inspect
from typing import Any, Optional, Type, TypeVar, Union

import denovo


""" Simplified Protocol """




""" Primitive Abstract Base Classes """

@dataclasses.dataclass
class Named(abc.ABC):
    """Automatically creates a sensible 'name' attribute.
    
    Automatically provides a 'name' attribute to a subclass, if it isn't 
    otherwise passed. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout denovo. For example, if a denovo 
            instance needs settings from a settings instance, 'name' should 
            match the appropriate section name in a settings instance. 
            Defaults to None. 

    """
    name: Optional[str] = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__() # type: ignore
        except AttributeError:
            pass

    """ Private Methods """
    
    def _get_name(self) -> str:
        """Returns snakecase of the class name.

        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return denovo.tools.snakify(self.__class__.__name__) # type: ignore
    
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() or hasattr(subclass, 'name'))
              



""" Containers Abstract Base Classes """

@dataclasses.dataclass # type: ignore
class Bunch(Collection[Any], abc.ABC):
    """Abstract base class for denovo collections.
  
    A Bunch differs from a general python Collection in 3 ways:
        1) It must include an 'add' method which provides the default mechanism
            for adding new items to the collection.'add' allows a subclass to 
            designate the preferred method of adding to the collections's stored 
            data.
        2) It allows the '+' operator to be used to join a Bunch subclass 
            instance of the same general type (Mapping, Sequence, tuple, etc.). 
            The '+' operator calls the Bunch subclass 'add' method to implement 
            how the added item(s) is/are added to the Bunch subclass instance.
        3) A subclass must include a 'subset' method with optional 'include' and
            'exclude' parameters for returning a subset of the Bunch subclass.
    
    Args:
        contents (Collection[Any]): stored iterable. Defaults to None.
              
    """
    contents: Collection[Any]
   
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def add(self, item: Any) -> None:
        """Adds 'item' to 'contents'.
        
        Subclasses must provide their own methods.
        
        """
        pass
    
    @abc.abstractmethod
    def subset(self, 
               include: Union[Sequence[Any], Any] = None, 
               exclude: Union[Sequence[Any], Any] = None) -> Bunch:
        """Returns a subclass with some items removed from 'contents'.
        
        Args:
            include (Union[Sequence[Any], Any]): items to include in the new 
                Bunch. Defaults to None.
            exclude (Union[Sequence[Any], Any]): items to exclude in the new 
                Bunch. Defaults to None.
        
        """
        pass
       
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() 
                or denovo.tools.has_methods(item = subclass, # type: ignore
                                            methods = ['add', 'subset', 
                                                       '__add__', '__iadd__', 
                                                       '__iter__', '__len__'])) 
          
    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(item = other)
        return

    def __iadd__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(item = other)
        return

    def __iter__(self) -> Iterator[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)

    
""" Composite Abstract Base Classes """

@dataclasses.dataclass
class Node(Hashable, abc.ABC):
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
        super().__init_subclass__(*args: Any, **kwargs: Any) # type: ignore
        cls.__hash__ = NodeWrapper.__hash__ # type: ignore
        cls.__eq__ = NodeWrapper.__eq__ # type: ignore
        cls.__ne__ = NodeWrapper.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or denovo.tools.snakify(self.__class__.__name__) # type: ignore
                
    """ Dunder Methods """

    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() 
                or denovo.tools.has_methods(item = subclass, # type: ignore
                                            methods = ['__hash__', '__eq__', 
                                                       '__ne__']))
        
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

    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equal to 'contents'.

        Args:
            item (Any): item to check versus 'contents'
            
        Returns:
            bool: if 'item' is in or equal to 'contents' (True). Otherwise, it
                returns False.

        """
        try:
            return item in self.contents # type: ignore
        except TypeError:
            try:
                return item is self.contents
            except TypeError:
                return item == self.contents # type: ignore
                
    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'contents'.

        Args:
            attribute (str): name of attribute to return.

        Raises:
            AttributeError: if 'attribute' is not found in 'contents'.

        Returns:
            Any: matching attribute.

        """
        try:
            return object.__getattribute__(
                object.__getattribute__(self, 'contents'), attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} is not in '
                f'{object.__getattribute__(self, "__name__")}') 

    def __setattr__(self, attribute: str, value: Any) -> None:
        """sets 'attribute' to 'value'.
        
        If 'attribute' exists in this class instance, its new value is set to
        'value.' Otherwise, 'attribute' and 'value' are set in what is stored
        in 'contents'

        Args:
            attribute (str): name of attribute to set.
            value (Any): value to store in 'attribute'.

        """
        if hasattr(self, attribute) or self.contents is None:
            object.__setattr__(self, attribute, value)
        else:
            object.__setattr__(self.contents, attribute, value)
            
    def __delattr__(self, attribute: str) -> None:
        """Deletes 'attribute'.
        
        If 'attribute' exists in this class instance, it is deleted. Otherwise, 
        this method attempts to delete 'attribute' from what is stored in 
        'contents'

        Args:
            attribute (str): name of attribute to set.
            value (Any): value to store in 'attribute'.

        Raises:
            AttributeError: if 'attribute' is neither found in a class instance
                nor in 'contents'.
            
        """
        try:
            object.__delattr__(self, attribute)
        except AttributeError:
            try:
                object.__delattr__(self.contents, attribute)
            except AttributeError:
                raise AttributeError(f'{attribute} is not in {self.__name__}') 
        
    
@dataclasses.dataclass # type: ignore
class Composite(Bunch, abc.ABC):

                      
    @abc.abstractproperty
    def nodes(self) -> set[Node]:
        """Returns all stored nodes as a set."""
        pass

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
            exclude (Optional[Nodes]): nodes to exclude in the new Composite. 
                Defaults to None.
                  
        """
        pass
    
    @abc.abstractmethod 
    def walk(self, 
             start: Node, 
             stop: Node, 
             path: Optional[Pipelines] = None) -> Pipelines:
        """Returns all paths in graph from 'start' to 'stop'.
        
        Args:
            start (Node): node to start paths from.
            stop (Node): node to stop paths.
            path (Pipelines): paths from 'start' to 'stop'. Defaults to None. 

        Returns:
            Pipelines: all paths from 'start' to 'stop'.
            
        """
        pass
 
    """ Dunder Methods """
 
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() 
                or (denovo.tools.has_methods(item = subclass, # type: ignore
                                             methods = ['add', 'delete', 
                                                        'merge', 'subset', 
                                                        'walk', '__add__'])
                    and denovo.tools.has_properties(item = subclass, # type: ignore
                                                attributes = 'nodes')))
  
    def __add__(self, other: Any) -> None:
        """Adds 'other' to the stored graph using the 'merge' method.

        Args:
            other (Any): another Composite or supported data structure.
            
        """
        self.merge(item = other)        
        return     
    
      
@dataclasses.dataclass # type: ignore
class Network(Composite, abc.ABC):


    """ Required Properties """
    
    @abc.abstractproperty
    def edges(self) -> Edges:
        """Returns instance as an edge list."""
        pass
       
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

    """ Dunder Methods """

    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() 
                or (super().__subclasshook__(subclass = subclass) 
                    and denovo.tools.has_methods(item = subclass, # type: ignore
                                                 attributes = ['add', 'delete', 
                                                               'merge', 'walk',
                                                               'subset'])
                    and denovo.tools.has_properties(item = subclass, # type: ignore
                                                    attributes = 'edges')))


@dataclasses.dataclass # type: ignore
class Directed(Network, abc.ABC):

    """ Required Properties """

    @abc.abstractproperty
    def endpoints(self) -> set[Node]:
        """Returns endpoint nodes as a set."""
        pass

    @abc.abstractproperty
    def paths(self) -> Pipelines:
        """Returns all paths as Pipelines."""
        pass
       
    @abc.abstractproperty
    def roots(self) -> set[Node]:
        """Returns root nodes as a set."""
        pass
    
    """ Required Methods """
    
    @abc.abstractmethod     
    def append(self, item: Any) -> None:
        """Appends 'item' to the endpoints.

        Appending creates an edge between every endpoint of this instance
        and the every root of 'item'.

        Args:
            item (Any): any supported data type which can be added.
      
        Raises:
            TypeError: if 'item' is not of a supported data type.  
               
        """
        pass
    
    @abc.abstractmethod 
    def prepend(self, item: Any) -> None:
        """Prepends 'item' to the roots.

        Prepending creates an edge between every endpoint of 'item' and every
        root of this instance.

        Args:
            item (Any): any supported data type which can be added.
            
        Raises:
            TypeError: if 'item' is not of a supported data type.
                
        """
        pass

    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() 
                or (super().__subclasshook__(subclass = subclass) 
                    and denovo.tools.has_methods(item = subclass, # type: ignore
                                                methods = ['add', 'delete', 
                                                            'merge', 'subset', 
                                                            'walk'])
                    and denovo.tools.has_properties(item = subclass, # type: ignore
                                                    attributes = ['endpoints',
                                                                'paths', 
                                                                'roots']))

@dataclasses.dataclass # type: ignore
class Graph(Directed, abc.ABC):
    """Base class for denovo graph data structures.
    
    Args:
        contents (Union[Adjacency, Matrix]): an adjacency list or adjacency
            matrix storing the contained graph.
                  
    """  
    contents: Union[Adjacency, Matrix] # type: ignore
    
    """ Required Properties """

    @abc.abstractproperty
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an adjacency list."""
        pass

    @abc.abstractproperty
    def matrix(self) -> Matrix:
        """Returns the stored graph as an adjacency matrix."""
        pass
    
    """ Required Methods """
    
    @abc.abstractclassmethod
    def from_adjacency(cls, adjacency: Adjacency) -> Graph:
        """Creates a Graph instance from an Adjacency instance."""
        pass
    
    @abc.abstractclassmethod
    def from_edges(cls, edges: Edges) -> Graph:
        """Creates a Graph instance from an Edges instance."""
        pass
    
    @abc.abstractclassmethod
    def from_matrix(cls, matrix: Matrix) -> Graph:
        """Creates a Graph instance from a Matrix instance."""
        pass
    
    @abc.abstractclassmethod
    def from_pipeline(cls, pipeline: Pipeline) -> Graph:
        """Creates a Graph instance from a Pipeline instance."""
        pass

    """ Public Methods """
    
    @classmethod
    def create(cls, source: Composite) -> Graph:
        """Creates an instance of a Graph from 'source'.
        
        Args:
            source (Composite): an adjacency list, adjacency matrix, edge list, 
                or pipeline which can used to create the stored graph.
                
        Returns:
            Graph: a Graph instance created based on 'source'.
                
        """
        if denovo.converters.is_adjacency_list(item = source): # type: ignore
            return cls.from_adjacency(adjacency = source) # type: ignore
        elif denovo.converters.is_adjacency_matrix(item = source): # type: ignore
            return cls.from_matrix(matrix = source) # type: ignore
        elif denovo.converters.is_edge_list(item = source): # type: ignore
            return cls.from_edges(edges = source) # type: ignore
        elif denovo.converters.is_pipeline(item = source): # type: ignore
            return cls.from_pipeline(pipeline = source) # type: ignore
        else:
            raise TypeError(
                f'create requires source to be an adjacency list, adjacency '
                f'matrix, edge list, or pipeline')      
      
    """ Dunder Methods """

    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (super().__subclasshook__(subclass = subclass) 
                and denovo.tools.has_methods(item = subclass, # type: ignore
                                             methods = ['from_adjacency',
                                                        'from_edges',
                                                        'from_matrix',
                                                        'from_pipeline'])
                and denovo.tools.has_properties(item = subclass, # type: ignore
                                                attributes = ['adjacency',
                                                              'matrix']))
        
    def __str__(self) -> str:
        """Returns prettier summary of the stored graph.

        Returns:
            str: a formatted str of class information and the contained 
                adjacency list.
            
        """
        return denovo.summary.beautify(item = self, package = 'denovo') # type: ignore
  
       
""" Aliases"""

_AdjacencyType = MutableMapping[Node, Union[set[Node], Sequence[Node]]]
_ConnectionsType = Collection[Node]
_DyadType = tuple[Sequence[Any], Sequence[Any]]
_EdgeType = tuple[Node, Node]
_EdgesType = Collection[_EdgeType]
_MatrixType = tuple[Sequence[Sequence[int]], Sequence[Node]]
_NodesType = Union[Node, _ConnectionsType]
_PipelineType = Sequence[Node]
_PipelinesType = Collection[_PipelineType]

""" Type Variables """

Adjacency = TypeVar('Adjacency', bound = _AdjacencyType)
Connections = TypeVar('Connections', bound = _ConnectionsType)
Dyad = TypeVar('Dyad', bound = _DyadType)
Edge = TypeVar('Edge', bound = _EdgeType)
Edges = TypeVar('Edges', bound = _EdgesType)
Matrix = TypeVar('Matrix', bound = _MatrixType)
Nodes = TypeVar('Nodes', bound = _NodesType)
Pipeline = TypeVar('Pipeline', bound = _PipelineType)
Pipelines = TypeVar('Pipelines', bound = _PipelinesType)
