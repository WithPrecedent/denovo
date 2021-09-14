"""
types: denovo type protocols, aliases, and variables
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

The base class types in denovo serve two purposes (unless otherwise noted):
    1) They can be base classes that can be inherited from with attributes,
        methods, and properties.
    2) They act as de facto protocols that allow non-inherited and 
        non-registered classes/instances to be recognized as subclasses/
        instances if they meet certain criteria.
It is this second purpose that attempts to bridge the demands of static type 
checkers and runtime type checking that currently is impossible with the typing
module in python. It also affords users greater flexibility in designing 
compatible classes without hassling with inheritance or abstract base class
registration.

Contents:
    Type Aliases:
        Operation: generic, flexible Callable type alias.
        Signatures: dict of Signatures type.
        Wrappable: type for an item that can be wrapped by a decorator.
    Module Level Variables:
        BUILTINS (dict): mapping with str names of builtin in a types and values
            as the (generic) type to compare against.
        registry (dict): using the module '__getattr__' function, 'registry' 
            acts as a constantly updated registry of Kind subclasses and 
            BUILTINS. Until a tree structure is built for the Kind registry, the 
            order of 'registry' determines the order of matching. So, BUILTINS 
            are always placed at the bottom of the dict to prioritize user 
            created classes.
    Simplified Protocol System:
        Kind (ABC): denovo protocol class which allows classes to be defined in
             manner that facilitates static and runtime type checking including
             attributes, properties, methods, and method signatures.
        dispatcher (Callable, object): decorator for denovo's dispatch system 
            which has greater functionality to the python singledispatch method 
            using the Kind protocol system. It is also fully compatible with 
            python builtin types.
        identify (Callable): determines the matching Kind or builtin python 
            type.
        kindify (Callable): convenience function for creating Kind subclasses.
    Abstract Base Class Types:
        Named (ABC): base class that requires a 'name' attribute and, if
            inherited, automatically provides a value for 'name'.
        Bunch (Collection, ABC): base class for denovo collections that requires
            subclasses to have 'add' and 'subset' methods. 
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

ToDo:
    Convert Kind registry into a tree for a more complex typing match search.
    Add Keystone base class with automatic type validation, subclass 
        registration, and instance registration.
       
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Iterator, MutableMapping, MutableSequence, Sequence, 
    Set)
import copy
import dataclasses
import datetime
import functools
import inspect
from typing import (
    Any, Callable, ClassVar, Optional, Type, TypeVar, Union, get_type_hints)

import denovo


""" Type Aliases """

Operation = Callable[..., Any]
Signatures = MutableMapping[str, inspect.Signature]
Wrappable = Union[object, Type[Any], Operation]

""" Module Level Variables """

BUILTINS: dict[str, Type[Any]] = {
    'bool': bool,
    'complex': complex,
    'datetime': datetime.datetime,
    'dict': MutableMapping,
    'float': float,
    'int': int,
    'bytes': bytes,
    'list': MutableSequence,
    'set': Set,
    'str': str,
    'tuple': Sequence}

""" Module Attribute Accessor """

def __getattr__(attribute: str) -> Any:
    """Adds module level access to 'registry' and 'matcher'."""
    if attribute in ['registry']:
        _get_registry()
    else:
        raise AttributeError(
            f'{attribute} not found in {globals()["__module__"]}')    

def _get_registry() -> MutableMapping[str, Type[Any]]:
    complete = copy.deepcopy(Kind._registry)
    complete.update(BUILTINS)
    return complete 
    
""" Simplified Protocol System """

@dataclasses.dataclass
class Kind(abc.ABC):
    """Base class for easy protocol typing.
    
    Kind must be subclassed either directly or by using the helper function
    'kindify'. All of its attributes are stored as class-level variables and 
    subclasses are not designed to be instanced.
    
    Args:
        attributes (ClassVar[list[str]]): a list of the str names of attributes
            that are neither methods nor properties. Defaults to an empty list.
        methods: ClassVar[list[str]] = a list of str names of methods. Defaults 
            to an empty list.
        properties: ClassVar[list[str]] = a list of str names of properties. 
            Defaults to an empty list.
        signatures: ClassVar[Signatures]  = a dict with keys as 
            str names of methods and values as inspect.Signature classes. 
            Defaults to an empty dict.
    
    """
    attributes: ClassVar[list[str]] = []
    methods: ClassVar[list[str]] = []
    properties: ClassVar[list[str]] = []
    signatures: ClassVar[Signatures] = {}
    _registry: ClassVar[MutableMapping[str, Type[Any]]] = {}
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs: Any):
        """Adds 'cls' to '_registry'."""
        try:
            super().__init_subclass__(**kwargs) # type: ignore
        except AttributeError:
            pass
        if abc.ABC in cls.__bases__:
            key = denovo.modify.snakify(cls.__name__)
            cls._registry[key] = cls

    """ Properties """
    
    @property
    def matcher(self) -> dict[Union[Type[Any], Kind], str]:
        """Returns internal registry with builtin types added."""
        return {v: k for k, v in self.registry.items()}
    
    @property
    def registry(self) -> dict[str, Union[Type[Any], Kind]]:
        """Returns internal registry with builtin types added."""
        return _get_registry() # type: ignore
    
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Tests whether 'subclass' has the relevant characteristics."""
        return denovo.check.is_kind(item = subclass, kind = cls) # type: ignore


@dataclasses.dataclass
class dispatcher(object):
    """Decorator for a dispatcher.
    
    dispatcher violates the normal python convention of naming classes in
    capital case because it is only designed to be used as a callable decorator,
    where lowercase names are the norm.
    
    decorator attempts to solve two shortcomings of the current python 
    singledispatch framework: 
        1) It checks for subtypes of passed items that serve as the basis for
            the dispatcher. As of python 3.10, singledispatch tests the type of
            a passed argument was equivalent to a stored type which precludes
            testing of subtypes.
        2) It supports the denovo typing system which allows for an alternative 
            approach to parameterized generics that can be used at runtime. So,
            for example, singledispatch cannot match MutableSequence[str] to a
            function even though type annotations often prefer the flexibility
            of generics. However, dispatcher compares the passed argument with
            the types (and Kinds) stored in 'denovo.framework.Kind.registry'.
    
    Attributes:
        wrapped (Wrappable): wrapped class or function.
        registry (dict[str, Operation]): registry for different functions that 
            may be called based on the first parameter's type. Defaults to an 
            empty dict.
        
    """
    wrapped: Wrappable
    registry: dict[str, Operation] = dataclasses.field(
        default_factory = dict)
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Allows class to be called as a function decorator."""
        # Updates 'wrapped' for proper introspection and traceback.
        functools.update_wrapper(self, self.wrapped)
        # Copies key attributes and functions to wrapped Operation.
        self.wrapped.register = self.register
        self.wrapped.dispatch = self.dispatch
        self.wrapped.registry = self.registry
        
    def __call__(self, *args: Any, **kwargs: Any) -> Operation:
        """Returns wrapped object with args and kwargs"""
        return self.dispatch(*args, **kwargs)

    """ Properties """
    
    @property
    def kinds(self) -> MutableMapping[str, Type[Any]]:
        """Returns the virtual registry of types in the module."""
        return globals()['__getattr__'](__module__, 'registry') # type: ignore
    
    """ Public Methods """
    
    def categorize(self, item: Any) -> str:
        """Determines the kind of 'item' and returns its str name."""
        if not inspect.isclass(item):
            item = item.__class__
        for name, kind in self.kinds.items():
            if issubclass(item, kind):
                return name
        raise KeyError(f'item does not match any recognized type')
           
    def dispatch(self, *args: Any, **kwargs: Any) -> Operation:
        """[summary]

        Args:
            source (Any): [description]

        Returns:
            Operation: [description]
            
        """
        item = self._get_first_argument(*args, **kwargs)
        key = self.categorize(item = item)
        return self.registry[key](item, *args, **kwargs)
    
    def register(self, wrapped: Operation) -> None:
        """[summary]

        Args:
            wrapped (Operation): [description]

        Returns:
            Operation: [description]
            
        """
        _, kind = next(iter(get_type_hints(wrapped).items()))
        self.registry[kind.__name__] = wrapped
        return
    
    """ Private Methods """
    
    def _get_first_argument(*args: Any, **kwargs: Any) -> Any:
        """Returns first argument in args and kwargs."""
        if args:
            return args[0]
        else:
            return list(kwargs.keys())[0]
           
def identify(item: Any) -> str:
    """Determines the kind/type of 'item' and returns its str name."""
    if inspect.isclass(item):
        checker = issubclass
    else:
        checker = isinstance
    for kind, name in Kind.matcher.items(): # type: ignore
        if checker(item, kind):
            return name # type: ignore
    raise KeyError(f'item {str(item)} does not match any recognized type')

def kindify(name: str, 
            item: Type[Any], 
            exclude_private: bool = True,
            include_signatures: bool = True) -> Type[Kind]:
    """Creates Kind named 'name' from passed 'item'."""
    kind = dataclasses.make_dataclass(
        name,
        list(Kind.__annotations__.keys()), 
        bases = tuple([Kind, abc.ABC]))
    kind.attributes = denovo.unit.name_attributes(  # type: ignore
        item = item,
        exclude_private = exclude_private)
    kind.methods = denovo.unit.name_methods( # type: ignore
        item = item, 
        exclude_private = exclude_private)
    kind.properties = denovo.unit.name_properties( # type: ignore
        item = item,
        exclude_private = exclude_private)
    if include_signatures:
        kind.signatures = denovo.unit.get_signatures( # type: ignore
            item = item,
            exclude_private = exclude_private)
    return kind


""" Abstract Base Class Types """

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
        return denovo.modify.snakify(self.__class__.__name__) # type: ignore
    
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
              

@dataclasses.dataclass # type: ignore
class Bunch(Collection, abc.ABC): # type: ignore
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
        contents (Collection): stored iterable. Defaults to None.
              
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
    def subset(
        self, 
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
                or denovo.unit.has_methods(
                    item = subclass,
                    methods = [
                        'add', 'subset', '__add__', '__iadd__', '__iter__', 
                        '__len__'])) 
          
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
        super().__init_subclass__(*args, **kwargs) # type: ignore
        cls.__hash__ = Node.__hash__ # type: ignore
        cls.__eq__ = Node.__eq__ # type: ignore
        cls.__ne__ = Node.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or denovo.modify.snakify(self.__class__.__name__)
                
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
                or denovo.unit.has_methods(
                    item = subclass,
                    methods = ['__hash__', '__eq__', '__ne__']))
        
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

    """ Required Properties """

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
    def add(
        self, 
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
    def subset(
        self, 
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
    def walk(
        self, 
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
        return (
            subclass in cls.__subclasses__() 
            or (denovo.unit.has_methods(
                item = subclass,
                methods = ['add', 'delete', 'merge', 'subset', 'walk', 
                           '__add__'])
                and denovo.unit.has_properties(
                    item = subclass, 
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
        return (
            subclass in cls.__subclasses__() 
            or (super().__subclasshook__(subclass = subclass) 
                and denovo.unit.has_methods(
                    item = subclass,
                    attributes = ['add', 'delete', 'merge', 'walk', 'subset'])
                    and denovo.unit.has_properties(
                        item = subclass,
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
        return (
            subclass in cls.__subclasses__() 
            or (super().__subclasshook__(subclass = subclass) 
                and denovo.unit.has_methods(
                    item = subclass,
                    methods = ['add', 'delete', 'merge', 'subset', 'walk'])
                and denovo.unit.has_properties(
                    item = subclass,
                    attributes = ['endpoints', 'paths', 'roots'])))

""" Type Variables """

Adjacency = TypeVar(
    'Adjacency', 
    bound = MutableMapping[Node, Union[set[Node], Sequence[Node]]])
Connections = TypeVar(
    'Connections', 
    bound = Collection[Node])
Dyad = TypeVar(
    'Dyad', 
    bound = tuple[Sequence[Any], Sequence[Any]])
Edge = TypeVar(
    'Edge', 
    bound = tuple[Node, Node])
Edges = TypeVar(
    'Edges', 
    bound = Collection[tuple[Node, Node]])
Matrix = TypeVar(
    'Matrix', 
    bound = tuple[Sequence[Sequence[int]], Sequence[Node]])
Nodes = TypeVar(
    'Nodes', 
    bound = Union[Node, Collection[Node]])
Pipeline = TypeVar(
    'Pipeline', 
    bound = Sequence[Node])
Pipelines = TypeVar(
    'Pipelines', 
    bound = Collection[Sequence[Node]])
