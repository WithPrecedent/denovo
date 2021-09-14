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
        denovo.alias.Operation: generic, flexible Callable type alias.
        denovo.alias.Signatures: dict of denovo.alias.Signatures type.
        denovo.alias.Wrappable: type for an item that can be wrapped by a decorator.
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

ToDo:
    Convert Kind registry into a tree for a more complex typing match search.
       
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Iterator, Mapping, MutableMapping, MutableSequence, 
    Sequence, Set)
import copy
import dataclasses
import datetime
import inspect
from typing import (
    Any, Callable, ClassVar, Optional, Type, TypeVar, Union, get_origin, get_type_hints)

import denovo

""" Module Level Variables """

BUILTINS: dict[str, Type[Any]] = {
    'bool': bool,
    'str': str,
    'dict': Mapping,
    'list': MutableSequence,
    'float': float,
    'int': int,
    'set': Set,
    'tuple': Sequence,
    'complex': complex,
    'bytes': bytes,
    'datetime': datetime.datetime}

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
        signatures: ClassVar[denovo.alias.Signatures]  = a dict with keys as 
            str names of methods and values as inspect.Signature classes. 
            Defaults to an empty dict.
    
    """
    attributes: ClassVar[list[str]] = []
    methods: ClassVar[list[str]] = []
    properties: ClassVar[list[str]] = []
    signatures: ClassVar[denovo.alias.Signatures] = {}
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
    def registry(self) -> dict[str, Union[Type[Any], Kind]]:
        """Returns internal registry with builtin types added."""
        return _get_registry() # type: ignore
    
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Tests whether 'subclass' has the relevant characteristics."""
        return is_kind(item = subclass, kind = cls) # type: ignore

def identify(item: Any) -> str:
    """Determines the kind/type of 'item' and returns its str name."""
    if not inspect.isclass(item):
        item = item.__class__
    for name, kind in _get_registry().items():
        try:
            if issubclass(item, kind):
                return name
        except TypeError:
            if issubclass(get_origin(item), kind):
                return name
    raise KeyError(f'item {str(item)} does not match any recognized type')
    
def is_kind(item: Union[Type[Any], object], 
            kind: Type[denovo.typing.Kind]) -> bool:
     """Returns whether 'item' is an instance of subclass of 'kind'."""   
     return denovo.unit.has_traits(
         item = item,
         attributes = kind.attributes,
         methods = kind.methods, 
         properties = kind.properties,
         signatures = kind.signatures)
     
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
