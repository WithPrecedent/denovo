"""
structures: lightweight composite data structures
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Classes:
    Abstract Base Classes and Kind Types:
        Node (Hashable, ABC): base class that defines the criteria for a node in
            a composite denovo object. It also provides automatic hashablity if
            inherited from.
        Composite (Bunch, ABC): base class establishing necessary functionality
            of denovo composite objects. There is no value in inheriting from 
            Composite except to enforce the subclass requirements.
        Network (Composite, ABC): base class establishing criteria for denovo 
            composite objects with edges. There is no value in inheriting from 
            Network except to enforce the subclass requirements.
        Directed (Network, ABC): base class establishing criteria for denovo 
            composite objects with directed edges. There is no value in 
            inheriting from Directed except to enforce the subclass 
            requirements.
    Graph (Bunch): a lightweight directed acyclic graph (DAG) that serves as
        the base class for denovo composite structures. Internally, the graph is
        stored as an adjacency list. As a result, it should primarily be used
        for workflows or other uses that do form large graphs. In those
        instances, an adjacency matrix would be far more efficient.
    System (Graph): a lightweight directed acyclic graph (DAG). Internally, the 
        graph is stored as an adjacency list. As a result, it should primarily 
        be used for workflows or other uses that do require large graphs.
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
        
To Do:
    Add an Edge class and seamless support for it in Graph to allow for weights,
        direction, and other edge attributes.
    Complete Network which will use an adjacency matrix for internal storage.
    
"""
from __future__ import annotations
import abc
import collections
from collections.abc import Collection, Hashable, MutableMapping, Sequence
import collections.abc
import copy
import dataclasses
import itertools
from typing import Any, Callable, ClassVar, Optional, Type, Union

import more_itertools

import denovo

""" Composite-Related Kinds """

@dataclasses.dataclass
class Node(denovo.base.Kind):
    
    methods: ClassVar[Union[list[str], denovo.base.Signatures]] = [
        '__hash__', '__eq__', '__ne__']
    generic: ClassVar[Optional[Type[Any]]] = Hashable


@dataclasses.dataclass
class Composite(denovo.base.Kind):
    
    methods: ClassVar[Union[list[str], denovo.base.Signatures]] = [
        'add', 'delete', 'merge', 'subset', 'walk', '__add__']
    properties: ClassVar[list[str]] = ['nodes']


@dataclasses.dataclass
class Connections(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = Collection
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = Node


@dataclasses.dataclass
class Network(Composite):
    
    methods: ClassVar[Union[list[str], denovo.base.Signatures]] = [
        'connect', 'disconnect']
    properties: ClassVar[list[str]] = ['edges']


@dataclasses.dataclass
class Directed(Network):
    
    methods: ClassVar[Union[list[str], denovo.base.Signatures]] = [
        'prepend', 'append']
    properties: ClassVar[list[str]] = ['endpoints', 'paths', 'roots']


@dataclasses.dataclass
class Graph(Directed):
    
    methods: ClassVar[Union[list[str], denovo.base.Signatures]] = [
        'create']
    properties: ClassVar[list[str]] = ['adjacency', 'matrix']


@dataclasses.dataclass
class Adjacency(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = MutableMapping
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        str, Connections)


@dataclasses.dataclass
class Edge(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (Node, Node)


@dataclasses.dataclass
class Edges(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (Edge)
    

@dataclasses.dataclass
class Labels(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = Sequence
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = str


@dataclasses.dataclass
class RowColumn(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = Sequence
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = int
    
    
@dataclasses.dataclass
class RawMatrix(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        RowColumn, RowColumn)
    
    
@dataclasses.dataclass
class Matrix(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        RawMatrix, Labels)


@dataclasses.dataclass
class Pipeline(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = Sequence
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = Node


@dataclasses.dataclass
class Pipelines(denovo.base.Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = Collection
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = Pipeline


""" Node Base Class and Kind Type """

@dataclasses.dataclass
class Nodifier(Hashable, abc.ABC):
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
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        cls.__hash__ = Node.__hash__ # type: ignore
        cls.__eq__ = Node.__eq__ # type: ignore
        cls.__ne__ = Node.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or denovo.modify.snakify(self.__class__.__name__)
                
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
        
""" """

@dataclasses.dataclass # type: ignore
class Graph(object):
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
        if denovo.tools.is_adjacency_list(item = source):
            return cls.from_adjacency(adjacency = source) # type: ignore
        elif denovo.tools.is_adjacency_matrix(item = source):
            return cls.from_matrix(matrix = source) # type: ignore
        elif denovo.tools.is_edge_list(item = source):
            return cls.from_edges(edges = source) # type: ignore
        elif denovo.tools.is_pipeline(item = source): 
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
                and denovo.unit.has_methods(item = subclass,
                                             methods = ['from_adjacency',
                                                        'from_edges',
                                                        'from_matrix',
                                                        'from_pipeline'])
                and denovo.unit.has_properties(item = subclass,
                                                attributes = ['adjacency',
                                                              'matrix']))
        
    def __str__(self) -> str:
        """Returns prettier str representation of the stored graph.

        Returns:
            str: a formatted str of class information and the contained graph.
            
        """
        return denovo.recap.beautify(item = self, package = 'denovo') # type: ignore
 
  
@dataclasses.dataclass
class System(denovo.containers.Lexicon):
    """Base class for denovo directed graphs.
    
    System supports '+' to join two System instances (or data structures 
    supported by the 'create' method) using the 'append' method if an instance
    is the left operand or 'prepend' if an instance is the right operand (and 
    the left operand is not a System).
       
    Args:

                  
    """  
    contents: denovo.base.Dictionary = dataclasses.field(
        default_factory = dict)
    default_factory: Any = set
    
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an adjacency list."""
        return self.contents

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an edge list."""
        return denovo.tools.adjacency_to_edges(source = self.contents)

    @property
    def endpoints(self) -> set[Node]:
        """Returns endpoint nodes in the stored graph in a list."""
        return {k for k in self.contents.keys() if not self.contents[k]}

    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as an adjacency matrix."""
        return denovo.tools.adjacency_to_matrix(source = self.contents)
                      
    @property
    def nodes(self) -> set[Node]:
        """Returns all stored nodes in a list."""
        return set(self.contents.keys())

    @property
    def paths(self) -> Pipelines:
        """Returns all paths through the stored graph as Pipeline."""
        return self._find_all_paths(starts = self.roots, stops = self.endpoints)
       
    @property
    def roots(self) -> set[Node]:
        """Returns root nodes in the stored graph in a list."""
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        return {k for k in self.contents.keys() if k not in stops}
    
    """ Class Methods """
 
    @classmethod
    def from_adjacency(cls, adjacency: Adjacency) -> System:
        """Creates a System instance from an adjacency list."""
        return cls(contents = adjacency)
    
    @classmethod
    def from_edges(cls, edges: Edges) -> System:
        """Creates a System instance from an edge list."""
        return cls(contents = denovo.tools.edges_to_adjacency(
            source = edges))
    
    @classmethod
    def from_matrix(cls, matrix: Matrix) -> System:
        """Creates a System instance from an adjacency matrix."""
        return cls(contents = denovo.tools.matrix_to_adjacency(
            source = matrix))
    
    @classmethod
    def from_pipeline(cls, pipeline: Pipeline) -> System:
        """Creates a System instance from a Pipeline."""
        return cls(contents = denovo.tools.pipeline_to_adjacency(
            source = pipeline))
       
    """ Public Methods """

    def add(self, 
            node: Node,
            ancestors: Nodes = None,
            descendants: Nodes = None) -> None:
        """Adds 'node' to the stored graph.
        
        Args:
            node (Node): a node to add to the stored graph.
            ancestors (Nodes): node(s) from which 'node' should be connected.
            descendants (Nodes): node(s) to which 'node' should be connected.

        Raises:
            KeyError: if some nodes in 'descendants' or 'ancestors' are not in 
                the stored graph.
                
        """
        if descendants is None:
            self.contents[node] = set()
        elif denovo.tools.is_property(item = descendants, instance = self):
            self.contents = set(getattr(self, descendants))
        else:
            descendants = denovo.convert.listify(descendants)
            descendants = [self._stringify(n) for n in descendants]
            missing = [n for n in descendants if n not in self.contents]
            if missing:
                raise KeyError(f'descendants {str(missing)} are not in the '
                               f'stored graph.')
            else:
                self.contents[node] = set(descendants)
        if ancestors is not None:  
            if denovo.tools.is_property(item = ancestors, instance = self):
                start = list(getattr(self, ancestors))
            else:
                ancestors = denovo.convert.listify(ancestors)
                missing = [n for n in ancestors if n not in self.contents]
                if missing:
                    raise KeyError(f'ancestors {str(missing)} are not in the '
                                   f'stored graph.')
                else:
                    start = ancestors
            for starting in start:
                if node not in self[starting]:
                    self.connect(start = starting, stop = node)                 
        return 

    def append(self, item: Union[Composite]) -> None:
        """Appends 'item' to the endpoints of the stored graph.

        Appending creates an edge between every endpoint of this instance's
        stored graph and the every root of 'item'.

        Args:
            item (Union[Composite]): another Graph, 
                an adjacency list, an edge list, an adjacency matrix, or one or
                more nodes.
            
        Raises:
            TypeError: if 'source' is neither a Graph, Adjacency, Edges, Matrix,
                or Nodes type.
                
        """
        if isinstance(item, Composite):
            current_endpoints = list(self.endpoints)
            new_graph = self.create(source = item)
            self.merge(item = new_graph)
            for endpoint in current_endpoints:
                for root in new_graph.roots:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError('item must be a System, Adjacency, Edges, '
                            'Matrix, Pipeline, or Node type')
        return
  
    def connect(self, start: Node, stop: Node) -> None:
        """Adds an edge from 'start' to 'stop'.

        Args:
            start (Node): name of node for edge to start.
            stop (Node): name of node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError('The start of an edge cannot be the same as the '
                             'stop in a System because it is acyclic')
        elif start not in self:
            self.add(node = start)
        elif stop not in self:
            self.add(node = stop)
        if stop not in self.contents[start]:
            self.contents[start].add(self._stringify(stop))
        return

    def delete(self, node: Node) -> None:
        """Deletes node from graph.
        
        Args:
            node (Node): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'node' is not in 'contents'.
            
        """
        try:
            del self.contents[node]
        except KeyError:
            raise KeyError(f'{node} does not exist in the graph')
        self.contents = {k: v.discard(node) for k, v in self.contents.items()}
        return

    def disconnect(self, start: Node, stop: Node) -> None:
        """Deletes edge from graph.

        Args:
            start (Node): starting node for the edge to delete.
            stop (Node): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' is not a node in the stored graph..

        """
        try:
            self.contents[start].discard(stop)
        except KeyError:
            raise KeyError(f'{start} does not exist in the graph')
        return

    def merge(self, item: Union[Composite]) -> None:
        """Adds 'item' to this Graph.

        This method is roughly equivalent to a dict.update, just adding the
        new keys and values to the existing graph. It converts 'item' to an 
        adjacency list that is then added to the existing 'contents'.
        
        Args:
            item (Union[Composite]): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, Adjacency, Edges, Matrix, 
                or Nodes type.
            
        """
        if isinstance(item, System):
            adjacency = item.adjacency
        elif isinstance(item, Adjacency):
            adjacency = item
        elif isinstance(item, Edges):
            adjacency = denovo.tools.edges_to_adjacency(source = item)
        elif isinstance(item, Matrix):
            adjacency = denovo.tools.matrix_to_adjacency(source = item)
        elif isinstance(item, (list, tuple, set)):
            adjacency = denovo.tools.pipeline_to_adjacency(source = item)
        elif isinstance(item, Node):
            adjacency = {item: set()}
        else:
            raise TypeError('item must be a System, Adjacency, Edges, '
                            'Matrix, Pipeline, or Node type')
        self.contents.update(adjacency)
        return

    def prepend(self, item: Union[Composite]) -> None:
        """Prepends 'item' to the roots of the stored graph.

        Prepending creates an edge between every endpoint of 'item' and every
        root of this instance;s stored graph.

        Args:
            item (Union[Composite]): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, Adjacency, Edges, Matrix, 
                or Nodes type.
                
        """
        if isinstance(item, Composite):
            current_roots = list(self.roots)
            new_graph = self.create(source = item)
            self.merge(item = new_graph)
            for root in current_roots:
                for endpoint in new_graph.endpoints:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError('item must be a System, Adjacency, Edges, '
                            'Matrix, Pipeline, or Node type')
        return
      
    def subset(self, 
               include: Union[Any, Sequence[Any]] = None,
               exclude: Union[Any, Sequence[Any]] = None) -> System:
        """Returns a new System without a subset of 'contents'.
        
        All edges will be removed that include any nodes that are not part of
        the new subgraph.
        
        Any extra attributes that are part of a System (or a subclass) will be
        maintained in the returned subgraph.

        Args:
            include (Union[Any, Sequence[Any]]): nodes which should be included
                with any applicable edges in the new subgraph.
            exclude (Union[Any, Sequence[Any]]): nodes which should not be 
                included with any applicable edges in the new subgraph.

        Returns:
           System: with only key/value pairs with keys not in 'subset'.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        else:
            if include:
                excludables = [k for k in self.contents if k not in include]
            else:
                excludables = []
            excludables.extend([i for i in self.contents if i in exclude])
            new_graph = copy.deepcopy(self)
            for node in more_itertools.always_iterable(excludables):
                new_graph.delete(node = node)
        return new_graph
    
    def walk(self, 
             start: Node, 
             stop: Node, 
             path: Optional[Pipeline] = None) -> Pipeline:
        """Returns all paths in graph from 'start' to 'stop'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (Node): node to start paths from.
            stop (Node): node to stop paths.
            path (Pipeline): a path from 'start' to 'stop'. Defaults to an 
                empty list. 

        Returns:
            Pipeline: a list of possible paths (each path is a list 
                nodes) from 'start' to 'stop'.
            
        """
        if path is None:
            path = []
        path = path + [start]
        if start == stop:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self.walk(
                    start = node, 
                    stop = stop, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    """ Private Methods """

    def _find_all_paths(self, starts: Nodes, stops: Nodes) -> Pipeline:
        """Returns all paths between 'starts' and 'stops'.

        Args:
            start (Union[Node, Sequence[Node]]): starting points for 
                paths through the System.
            ends (Union[Node, Sequence[Node]]): endpoints for paths 
                through the System.

        Returns:
            Pipeline: list of all paths through the System from all 'starts' 
                to all 'ends'.
            
        """
        all_paths = []
        for start in more_itertools.always_iterable(starts):
            for end in more_itertools.always_iterable(stops):
                paths = self.walk(start = start, stop = end)
                if paths:
                    if all(isinstance(path, Node) for path in paths):
                        all_paths.append(paths)
                    else:
                        all_paths.extend(paths)
        return all_paths
    
    """ Dunder Methods """

    def __add__(self, other: Union[Composite]) -> None:
        """Adds 'other' to the stored graph using the 'append' method.

        Args:
            other (Union[Composite]): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        """
        self.append(item = other)     
        return 

    def __radd__(self, other: Union[Composite]) -> None:
        """Adds 'other' to the stored graph using the 'prepend' method.

        Args:
            other (Union[Composite]): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        """
        self.prepend(item = other)     
        return 



# @dataclasses.dataclass
# class Network(Graph):
#     """Base class for connected denovo data structures.
    
#     Graph stores a directed acyclic graph (DAG) as an adjacency list. Despite 
#     being called an adjacency "list," the typical and most efficient way to 
#     store one is using a python dict. a denovo Graph inherits from a Lexicon 
#     in order to allow use of its extra functionality over a plain dict.
    
#     Graph supports '+' and '+=' to be used to join two denovo Graph instances. A
#     properly formatted adjacency list could also be the added object.
    
#     Graph internally supports autovivification where a list is created as a 
#     value for a missing key. This means that a Graph need not inherit from 
#     defaultdict.
    
#     Args:
#         contents (Adjacency): an adjacency list where the keys are nodes and the 
#             values are nodes which the key is connected to. Defaults to an empty 
#             dict.
                  
#     """  
#     contents: Matrix = dataclasses.field(default_factory = dict)
    
#     """ Properties """

#     @property
#     def adjacency(self) -> Adjacency:
#         """Returns the stored graph as an adjacency list."""
#         return.contents

#     @property
#     def breadths(self) -> Pipeline:
#         """Returns all paths through the Graph using breadth-first search.
        
#         Returns:
#             Pipeline: returns all paths from 'roots' to 'endpoints' in a list 
#                 of lists of nodes.
                
#         """
#         return._find_all_paths(starts = self.roots, 
#                                     ends = self.endpoints,
#                                     depth_first = False)

#     @property
#     def depths(self) -> Pipeline:
#         """Returns all paths through the Graph using depth-first search.
        
#         Returns:
#             Pipeline: returns all paths from 'roots' to 'endpoints' in a list 
#                 of lists of nodes.
                
#         """
#         return._find_all_paths(starts = self.roots, 
#                                     ends = self.endpoints,
#                                     depth_first = True)
     
#     @property
#     def edges(self) -> Edges:
#         """Returns the stored graph as an edge list."""
#         return adjacency_to_edges(source = self.contents)

#     @property
#     def endpoints(self) -> listing[Node]:
#         """Returns a list of endpoint nodes in the stored graph.."""
#         return [k for k in self.contents.keys() if not self.contents[k]]

#     @property
#     def matrix(self) -> Matrix:
#         """Returns the stored graph as an adjacency matrix."""
#         return adjacency_to_matrix(source = self.contents)
                      
#     @property
#     def nodes(self) -> Dict[str, Node]:
#         """Returns a dict of node names as keys and nodes as values.
        
#         Because Graph allows various Node objects to be used as keys,
#         including the Nodes class, there isn't an obvious way to access already
#         stored nodes. This property creates a new dict with str keys derived
#         from the nodes (looking first for a 'name' attribute) so that a user
#         can access a node. 
        
#         This property is not needed if the stored nodes are all strings.
        
#         Returns:
#             Dict[str, Node]: keys are the name or has of nodes and the 
#                 values are the nodes themselves.
            
#         """
#         return {self._stringify(n): n for n in self.contents.keys()}
  
#     @property
#     def roots(self) -> listing[Node]:
#         """Returns root nodes in the stored graph..

#         Returns:
#             listing[Node]: root nodes.
            
#         """
#         stops = list(itertools.chain.from_iterable(self.contents.values()))
#         return [k for k in self.contents.keys() if k not in stops]
    
#     """ Class Methods """
    
#     @classmethod
#     def create(cls, source: Union[Adjacency, Edges, Matrix]) -> Graph:
#         """Creates an instance of a Graph from 'source'.
        
#         Args:
#             source (Union[Adjacency, Edges, Matrix]): an adjacency list, 
#                 adjacency matrix, or edge list which can used to create the
#                 stored graph.
                
#         Returns:
#             Graph: a Graph instance created based on 'source'.
                
#         """
#         if is_adjacency_list(item = source):
#             return cls.from_adjacency(adjacency = source)
#         elif is_adjacency_matrix(item = source):
#             return cls.from_matrix(matrix = source)
#         elif is_edge_list(item = source):
#             return cls.from_adjacency(edges = source)
#         else:
#             raise TypeError(
#                 f'create requires source to be an adjacency list, adjacency '
#                 f'matrix, or edge list')
           
#     @classmethod
#     def from_adjacency(cls, adjacency: Adjacency) -> Graph:
#         """Creates a Graph instance from an adjacency list.
        
#         'adjacency' should be formatted with nodes as keys and values as lists
#         of names of nodes to which the node in the key is connected.

#         Args:
#             adjacency (Adjacency): adjacency list used to 
#                 create a Graph instance.

#         Returns:
#             Graph: a Graph instance created based on 'adjacent'.
              
#         """
#         return cls(contents = adjacency)
    
#     @classmethod
#     def from_edges(cls, edges: Edges) -> Graph:
#         """Creates a Graph instance from an edge list.

#         'edges' should be a list of tuples, where the first item in the tuple
#         is the node and the second item is the node (or name of node) to which
#         the first item is connected.
        
#         Args:
#             edges (Edges): Edge list used to create a Graph 
#                 instance.
                
#         Returns:
#             Graph: a Graph instance created based on 'edges'.

#         """
#         return cls(contents = edges_to_adjacency(source = edges))
    
#     @classmethod
#     def from_matrix(cls, matrix: Matrix) -> Graph:
#         """Creates a Graph instance from an adjacency matrix.

#         Args:
#             matrix (Matrix): adjacency matrix used to create a Graph instance. 
#                 The values in the matrix should be 1 (indicating an edge) and 0 
#                 (indicating no edge).
 
#         Returns:
#             Graph: a Graph instance created based on 'matrix'.
                        
#         """
#         return cls(contents = matrix_to_adjacency(source = matrix))
    
#     @classmethod
#     def from_pipeline(cls, pipeline: Pipeline) -> Graph:
#         """Creates a Graph instance from a Pipeline.

#         Args:
#             pipeline (Pipeline): serial pipeline used to create a Graph
#                 instance.
 
#         Returns:
#             Graph: a Graph instance created based on 'pipeline'.
                        
#         """
#         return cls(contents = pipeline_to_adjacency(source = pipeline))
       
#     """ Public Methods """
    
#     def add(self, 
#             node: Node,
#             ancestors: Nodes = None,
#             descendants: Nodes = None) -> None:
#         """Adds 'node' to 'contents' with no corresponding edges.
        
#         Args:
#             node (Node): a node to add to the stored graph.
#             ancestors (Nodes): node(s) from which node should be connected.
#             descendants (Nodes): node(s) to which node should be connected.

#         """
#         if descendants is None:
#             self.contents[node] = []
#         elif descendants in self:
#             self.contents[node] = denovo.convert.listify(descendants)
#         else:
#             missing = [n for n in descendants if n not in self.contents]
#             raise KeyError(f'descendants {missing} are not in the stored graph.')
#         if ancestors is not None:  
#             if (isinstance(ancestors, Node) and ancestors in self
#                     or (isinstance(ancestors, (listing, tuple, set)) 
#                         and all(isinstance(n, Node) for n in ancestors)
#                         and all(n in self.contents for n in ancestors))):
#                 start = ancestors
#             elif (hasattr(self.__class__, ancestors) 
#                     and isinstance(getattr(type(self), ancestors), property)):
#                 start = getattr(self, ancestors)
#             else:
#                 missing = [n for n in ancestors if n not in self.contents]
#                 raise KeyError(f'ancestors {missing} are not in the stored graph.')
#             for starting in more_itertools.always_iterable(start):
#                 if node not in [starting]:
#                     self.connect(start = starting, stop = node)                 
#         return 

#     def append(self, 
#                source: Union[Graph, Adjacency, Edges, Matrix, Nodes]) -> None:
#         """Adds 'source' to this Graph.

#         Combining creates an edge between every endpoint of this instance's
#         Graph and the every root of 'source'.

#         Args:
#             source (Union[Graph, Adjacency, Edges, Matrix, Nodes]): another 
#                 Graph to join with this one, an adjacency list, an edge list, an
#                 adjacency matrix, or Nodes.
            
#         Raises:
#             TypeError: if 'source' is neither a Graph, Adjacency, Edges, Matrix,
#                 or Nodes type.
            
#         """
#         if isinstance(source, Graph):
#             if self.contents:
#                 current_endpoints = self.endpoints
#                 self.contents.update(source.contents)
#                 for endpoint in current_endpoints:
#                     for root in source.roots:
#                         self.connect(start = endpoint, stop = root)
#             else:
#                 self.contents = source.contents
#         elif isinstance(source, Adjacency):
#             self.append(source = self.from_adjacency(adjacecny = source))
#         elif isinstance(source, Edges):
#             self.append(source = self.from_edges(edges = source))
#         elif isinstance(source, Matrix):
#             self.append(source = self.from_matrix(matrix = source))
#         elif isinstance(source, Nodes):
#             if isinstance(source, (listing, tuple, set)):
#                 new_graph = Graph()
#                 edges = more_itertools.windowed(source, 2)
#                 for edge_pair in edges:
#                     new_graph.add(node = edge_pair[0], descendants = edge_pair[1])
#                 self.append(source = new_graph)
#             else:
#                 self.add(node = source)
#         else:
#             raise TypeError(
#                 'source must be a Graph, Adjacency, Edges, Matrix, or Nodes '
#                 'type')
#         return
  
#     def connect(self, start: Node, stop: Node) -> None:
#         """Adds an edge from 'start' to 'stop'.

#         Args:
#             start (Node): name of node for edge to start.
#             stop (Node): name of node for edge to stop.
            
#         Raises:
#             ValueError: if 'start' is the same as 'stop'.
            
#         """
#         if start == stop:
#             raise ValueError(
#                 'The start of an edge cannot be the same as the stop')
#         else:
#             if stop not in self.contents:
#                 self.add(node = stop)
#             if start not in self.contents:
#                 self.add(node = start)
#             if stop not in self.contents[start]:
#                 self.contents[start].append(self._stringify(stop))
#         return

#     def delete(self, node: Node) -> None:
#         """Deletes node from graph.
        
#         Args:
#             node (Node): node to delete from 'contents'.
        
#         Raises:
#             KeyError: if 'node' is not in 'contents'.
            
#         """
#         try:
#             del self.contents[node]
#         except KeyError:
#             raise KeyError(f'{node} does not exist in the graph')
#         self.contents = {
#             k: v.remove(node) for k, v in self.contents.items() if node in v}
#         return

#     def disconnect(self, start: Node, stop: Node) -> None:
#         """Deletes edge from graph.

#         Args:
#             start (Node): starting node for the edge to delete.
#             stop (Node): ending node for the edge to delete.
        
#         Raises:
#             KeyError: if 'start' is not a node in the stored graph..
#             ValueError: if 'stop' does not have an edge with 'start'.

#         """
#         try:
#             self.contents[start].remove(stop)
#         except KeyError:
#             raise KeyError(f'{start} does not exist in the graph')
#         except ValueError:
#             raise ValueError(f'{stop} is not connected to {start}')
#         return

#     def merge(self, source: Union[Graph, Adjacency, Edges, Matrix]) -> None:
#         """Adds 'source' to this Graph.

#         This method is roughly equivalent to a dict.update, just adding the
#         new keys and values to the existing graph. It converts the supported
#         formats to an adjacency list that is then added to the existing 
#         'contents'.
        
#         Args:
#             source (Union[Graph, Adjacency, Edges, Matrix]): another Graph to 
#                 add to this one, an adjacency list, an edge list, or an
#                 adjacency matrix.
            
#         Raises:
#             TypeError: if 'source' is neither a Graph, Adjacency, Edges, or 
#                 Matrix type.
            
#         """
#         if isinstance(source, Graph):
#             source = source.contents
#         elif isinstance(source, Adjacency):
#             pass
#         elif isinstance(source, Edges):
#             source = self.from_edges(edges = source).contents
#         elif isinstance(source, Matrix):
#             source = self.from_matrix(matrix = source).contents
#         else:
#             raise TypeError(
#                 'source must be a Graph, Adjacency, Edges, or Matrix type to '
#                 'update')
#         self.contents.update(source)
#         return
  
#     def subgraph(self, 
#                  include: Union[Any, Sequence[Any]] = None,
#                  exclude: Union[Any, Sequence[Any]] = None) -> Graph:
#         """Returns a new Graph without a subset of 'contents'.
        
#         All edges will be removed that include any nodes that are not part of
#         the new subgraph.
        
#         Any extra attributes that are part of a Graph (or a subclass) will be
#         maintained in the returned subgraph.

#         Args:
#             include (Union[Any, Sequence[Any]]): nodes which should be included
#                 with any applicable edges in the new subgraph.
#             exclude (Union[Any, Sequence[Any]]): nodes which should not be 
#                 included with any applicable edges in the new subgraph.

#         Returns:
#             Graph: with only key/value pairs with keys not in 'subset'.

#         """
#         if include is None and exclude is None:
#             raise ValueError('Either include or exclude must not be None')
#         else:
#             if include:
#                 excludables = [k for k in self.contents if k not in include]
#             else:
#                 excludables = []
#             excludables.extend([i for i in self.contents if i not in exclude])
#             new_graph = copy.deepcopy(self)
#             for node in more_itertools.always_iterable(excludables):
#                 new_graph.delete(node = node)
#         return new_graph

#     def walk(self, 
#              start: Node, 
#              stop: Node, 
#              path: Pipeline = None,
#              depth_first: bool = True) -> Pipeline:
#         """Returns all paths in graph from 'start' to 'stop'.

#         The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
#         Args:
#             start (Node): node to start paths from.
#             stop (Node): node to stop paths.
#             path (Pipeline): a path from 'start' to 'stop'. Defaults to an 
#                 empty list. 

#         Returns:
#             Pipeline: a list of possible paths (each path is a list 
#                 nodes) from 'start' to 'stop'.
            
#         """
#         if path is None:
#             path = []
#         path = path + [start]
#         if start == stop:
#             return [path]
#         if start not in self.contents:
#             return []
#         if depth_first:
#             method = self._depth_first_search
#         else:
#             method = self._breadth_first_search
#         paths = []
#         for node in self.contents[start]:
#             if node not in path:
#                 new_paths = self.walk(
#                     start = node, 
#                     stop = stop, 
#                     path = path,
#                     depth_first = depth_first)
#                 for new_path in new_paths:
#                     paths.append(new_path)
#         return paths

#     """ Private Methods """

#     def _stringify(self, node: Any) -> str:
#         """[summary]

#         Args:
#             node (Any): [description]

#         Returns:
#             str: [description]
            
#         """        
#         if isinstance(node, Node):
#             return node
#         else:
#             try:
#                 return node.name
#             except AttributeError:
#                 try:
#                     return denovo.modify.snakify(node.__name__)
#                 except AttributeError:
#                     return denovo.modify.snakify(node.__class__.__name__)


#     def _all_paths_bfs(self, start, stop):
#         """

#         """
#         if start == stop:
#             return [start]
#         visited = {start}
#         queue = collections.deque([(start, [])])
#         while queue:
#             current, path = queue.popleft()
#             visited.add(current)
#             for connected in self[current]:
#                 if connected == stop:
#                     return path + [current, connected]
#                 if connected in visited:
#                     continue
#                 queue.append((connected, path + [current]))
#                 visited.add(connected)   
#         return []

#     def _breadth_first_search(self, node: Node) -> Pipeline:
#         """Returns a breadth first search path through the Graph.

#         Args:
#             node (Node): node to start the search from.

#         Returns:
#             Pipeline: nodes in a path through the Graph.
            
#         """        
#         visited = set()
#         queue = [node]
#         while queue:
#             vertex = queue.pop(0)
#             if vertex not in visited:
#                 visited.add(vertex)
#                 queue.extend(set(self[vertex]) - visited)
#         return list(visited)
       
#     def _depth_first_search(self, 
#         node: Node, 
#         visited: listing[Node]) -> Pipeline:
#         """Returns a depth first search path through the Graph.

#         Args:
#             node (Node): node to start the search from.
#             visited (listing[Node]): list of visited nodes.

#         Returns:
#             Pipeline: nodes in a path through the Graph.
            
#         """  
#         if node not in visited:
#             visited.append(node)
#             for edge in self[node]:
#                 self._depth_first_search(node = edge, visited = visited)
#         return visited
  
#     def _find_all_paths(self, 
#         starts: Union[Node, Sequence[Node]],
#         stops: Union[Node, Sequence[Node]],
#         depth_first: bool = True) -> Pipeline:
#         """[summary]

#         Args:
#             start (Union[Node, Sequence[Node]]): starting points for 
#                 paths through the Graph.
#             ends (Union[Node, Sequence[Node]]): endpoints for paths 
#                 through the Graph.

#         Returns:
#             Pipeline: list of all paths through the Graph from all
#                 'starts' to all 'ends'.
            
#         """
#         all_paths = []
#         for start in more_itertools.always_iterable(starts):
#             for end in more_itertools.always_iterable(stops):
#                 paths = self.walk(start = start, 
#                                   stop = end, 
#                                   depth_first = depth_first)
#                 if paths:
#                     if all(isinstance(path, Node) for path in paths):
#                         all_paths.append(paths)
#                     else:
#                         all_paths.extend(paths)
#         return all_paths
            
#     """ Dunder Methods """

#     def __add__(self, other: Graph) -> None:
#         """Adds 'other' Graph to this Graph.

#         Adding another graph uses the 'join' method. Read that method's 
#         docstring for further details about how the graphs are added 
#         together.
        
#         Args:
#             other (Graph): a second Graph to join with this one.
            
#         """
#         self.join(graph = other)        
#         return

#     def __iadd__(self, other: Graph) -> None:
#         """Adds 'other' Graph to this Graph.

#         Adding another graph uses the 'join' method. Read that method's 
#         docstring for further details about how the graphs are added 
#         together.
        
#         Args:
#             other (Graph): a second Graph to join with this one.
            
#         """
#         self.join(graph = other)        
#         return

#     def __contains__(self, nodes: Nodes) -> bool:
#         """[summary]

#         Args:
#             nodes (Nodes): [description]

#         Returns:
#             bool: [description]
            
#         """
#         if isinstance(nodes, (listing, tuple, set)):
#             return all(n in self.contents for n in nodes)
#         elif isinstance(nodes, Node):
#             return nodes in self.contents
#         else:
#             return False   
        
#     def __getitem__(self, key: Node) -> Any:
#         """Returns value for 'key' in 'contents'.

#         Args:
#             key (Node): key in 'contents' for which a value is sought.

#         Returns:
#             Any: value stored in 'contents'.

#         """
#         return.contents[key]

#     def __setitem__(self, key: Node, value: Any) -> None:
#         """sets 'key' in 'contents' to 'value'.

#         Args:
#             key (Node): key to set in 'contents'.
#             value (Any): value to be paired with 'key' in 'contents'.

#         """
#         self.contents[key] = value
#         return

#     def __delitem__(self, key: Node) -> None:
#         """Deletes 'key' in 'contents'.

#         Args:
#             key (Node): key in 'contents' to delete the key/value pair.

#         """
#         del self.contents[key]
#         return

#     def __missing__(self) -> list:
#         """Returns an empty list when a key doesn't exist.

#         Returns:
#             list: an empty list.

#         """
#         return []
    
#     def __str__(self) -> str:
#         """Returns prettier summary of the Graph.

#         Returns:
#             str: a formatted str of class information and the contained 
#                 adjacency list.
            
#         """
#         new_line = '\n'
#         tab = '    '
#         summary = [f'{new_line}denovo {self.__class__.__name__}']
#         summary.append('adjacency list:')
#         for node, edges in self.contents.items():
#             summary.append(f'{tab}{node}: {str(edges)}')
#         return new_line.join(summary) 


   
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
#     denovo.base.Kind.register(item = kind, name = name)