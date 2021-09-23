"""
framework: denovo type protocols, aliases, and variables
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
        Signatures: dict of inspect.Signature types.
        Types: dict of Type[Any] types.
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
        identify (Callable): determines the matching Kind or builtin python 
            type.
        is_kind (Callable): returns whether the passed item is a particular
            Kind.
        kindify (Callable): convenience function for creating Kind subclasses
            from any existing class or instance.

ToDo:
    Convert Kind registry into a tree for a more complex typing match search.
       
"""
from __future__ import annotations
import abc
from collections.abc import (
    Callable, Collection, Container, Generator, Hashable, Iterable, Iterator, 
    Mapping, MutableMapping, MutableSequence, Sequence, Set)
import copy
import dataclasses
import datetime
import functools
import inspect
import re
from typing import (
    Any, ClassVar, Optional, Type, Union, get_origin, get_type_hints)

import denovo

""" Type Aliases """

# Simpler alias for generic callable.
Operation = Callable[..., Any]
# Abbreviated alias for a dict of inspect.Signature types.
Signatures = MutableMapping[str, inspect.Signature]
# Alias for dict of Type[Any] types.
Types = MutableMapping[str, Type[Any]]
# Shorter alias for things that can be wrapped.
Wrappable = Union[object, Type[Any], Operation]

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

GENERICS: list[Type[Any]] = [
    Callable, #type: ignore
    MutableMapping,
    Mapping,
    tuple,
    MutableSequence,
    Sequence,
    Set,
    Iterator,
    Iterable,
    Generator,
    Collection,
    Container,
    Hashable]

""" Module Attribute Accessor """

def __getattr__(attribute: str) -> Any:
    """Adds module level access to 'registry' and 'matcher'."""
    if attribute in ['registry']:
        return get_registry()
    else:
        raise AttributeError(
            f'{attribute} not found in {globals()["__module__"]}')    

def get_registry() -> Types:
    """
    """
    complete = copy.deepcopy(Kind._registry)
    complete.update(BUILTINS)
    return complete 

""" Private Methods """

def _snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): str to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()
    
""" Simplified Protocol System """

@dataclasses.dataclass
class Kind(abc.ABC):
    """Base class for easy protocol typing.
    
    The Kind system allows virtual subclassing based by matching various aspects
    of a class with those required. 
    
    Kind must be subclassed either directly or by using the helper function
    'kindify'. All of its attributes are stored as class-level variables and 
    subclasses are not designed to be instanced.
    
    Args:
        attributes (ClassVar[Union[list[str], Types]]): a list of the str names 
            of attributes that are neither methods nor properties or a dict of 
            str names of attributes that are neither methods nor properties 
            with values that are types of those attributes. Defaults to an empty 
            list.
        methods (ClassVar[Union[list[str], Signatures]]): a list of str names of 
            methods or a dict of str names of methods with values that are 
            inspect.Signature type for the named methods. Defaults to an empty 
            list.
        properties (ClassVar[list[str]]): a list of str names of properties. 
            Defaults to an empty list.
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of. Defaults to None.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
        _registry (ClassVar[Types]): dict which stores registered Kind 
            subclasses.
    
    """
    attributes: ClassVar[Union[list[str], Types]] = []
    methods: ClassVar[Union[list[str], Signatures]] = []
    properties: ClassVar[list[str]] = []
    generic: ClassVar[Optional[Type[Any]]] = None
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = None
    _registry: ClassVar[Types] = {}
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs: Any):
        """Adds 'cls' to '_registry'."""
        try:
            super().__init_subclass__(**kwargs) # type: ignore
        except AttributeError:
            pass
        key = _snakify(cls.__name__)
        cls._registry[key] = cls

    """ Properties """
    
    @property
    def registry(self) -> Types:
        """Returns internal registry with builtin types added."""
        return get_registry()

    """ Public Methods """
    
    @classmethod
    def create(
        cls,     
        attributes: Optional[Union[list[str], Types]] = None,
        methods: Optional[Union[list[str], Signatures]] = None,
        properties: Optional[list[str]] = None,
        generic: Optional[Type[Any]] = None,
        contains: Optional[Union[Any, tuple[Any, ...]]] = None) -> Type[Kind]:
        """[summary]

        Using 'create' will not allow the constructed Kinds to be usable by 
        mypy because the creation does not occur until runtime.
        
        Args:
            attributes (Optional[Union[list[str], Types]]): [description]. 
                Defaults to None.
            methods (Optional[Union[list[str], Signatures]]): [description]. 
                Defaults to None.
            properties (Optional[list[str]]): [description]. Defaults to None.
            generic (Optional[Optional[Type[Any]]]): [description]. 
                Defaults to None.

        Returns:
            Kind: [description]
            
        """
        new_kind = copy.deepcopy(cls)
        for trait in [
            'attributes', 'methods', 'properties', 'generic', 'contains']:
            if locals()[trait]:
                setattr(new_kind, trait, locals()[trait])
            # Adds required trait data from this class to 'new_kind'.
            if getattr(cls, trait):
                if (isinstance(getattr(cls, trait), MutableMapping)
                    and isinstance(getattr(new_kind, trait), MutableMapping)):
                    getattr(new_kind, trait).update(getattr(cls, trait))
                elif (isinstance(getattr(cls, trait), MutableSequence)
                    and isinstance(getattr(new_kind, trait), MutableSequence)):
                    getattr(new_kind, trait).extend(getattr(cls, trait))
                elif (isinstance(getattr(cls, trait), tuple)
                    and isinstance(getattr(new_kind, trait), tuple)):
                    value = getattr(new_kind, trait) + getattr(cls, trait)
                    setattr(new_kind, trait, value)
        return new_kind
    
    @classmethod
    def register(cls, item: Type[Any], name: Optional[str] = None) -> None:
        """
        """
        key = name or _snakify(item.__name__)
        cls._registry[key] = item
        return
        
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Tests whether 'subclass' has the relevant characteristics."""
        return is_kind(item = subclass, kind = cls) # type: ignore


def identify(item: Any) -> str:
    """Determines the kind/type of 'item' and returns its str name."""
    if not inspect.isclass(item):
        item = item.__class__
    for name, kind in get_registry().items():
        try:
            if issubclass(item, kind):
                return name
        except TypeError:
            if issubclass(get_origin(item), kind): # type: ignore
                return name
    raise KeyError(f'item {str(item)} does not match any recognized type')

def is_generic(
    item: Union[Type[Any], object], 
    generic: Optional[Type[Any]],
    contains: Optional[Union[Any, tuple[Any, ...]]] = None) -> bool:
    """Tests whether 'item' is a subclass or instance of 'generic'.
    
    Returns True if 'item' is a subclass/instance of 'generic' or 'generic' is 
    None.
    
    """
    if not inspect.isclass(item):
        item = item.__class__
    return generic is None or issubclass(item, generic) # type: ignore
   
def is_kind(item: Union[Type[Any], object], kind: Kind) -> bool:
     """Returns whether 'item' is an instance of subclass of 'kind'."""   
     return (
         denovo.unit.has_traits(
            item = item,
            attributes = kind.attributes,
            methods = kind.methods, 
            properties = kind.properties)
         and is_generic(
             item = item, 
             generic = kind.generic,
             contains = kind.contains))
     
def kindify(name: str, 
            item: Type[Any], 
            exclude_private: bool = True) -> Type[Kind]:
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
    for generic in GENERICS:
        if issubclass(item, generic):
            kind.generic = generic # type: ignore
            break
    return kind

""" Base denovo Kinds """

@dataclasses.dataclass
class Dictionary(Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = MutableMapping
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        Hashable, Any)


@dataclasses.dataclass
class Dyad(Kind):
    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        Sequence, Sequence)
  

@dataclasses.dataclass
class Group(Kind):
    
    methods: ClassVar[Union[list[str], Signatures]] = ['add', 'subset']
    generic: ClassVar[Optional[Type[Any]]] = Collection
  

@dataclasses.dataclass
class Named(Kind):
    
    attributes: ClassVar[Union[list[str], Types]] = {'name': str}


# @dataclasses.dataclass
# class TypeNode(denovo.structures.Tree):
#     pass



# keystones: denovo.Library = denovo.core.quirks.Keystone.library
# kinds: denovo.Catalog[str, Kind] = denovo.Catalog()
# quirks: denovo.Catalog[str, denovo.Quirk] = denovo.Catalog()


# def build_keystone(name: str,
#                    keystone: Union[str, denovo.core.quirks.Keystone] = None, 
#                    quirks: Union[str, 
#                                  denovo.Quirk, 
#                                  Sequence[Union[str, denovo.Quirk]]] = None,
#                    **kwargs: Any) -> denovo.core.quirks.Keystone:
#     """[summary]

#     Args:
#         name (str): [description]
#         keystone (Union[str, denovo.core.quirks.Keystone], optional): [description]. 
#             Defaults to None.
#         quirks (Union[str, denovo.Quirk, Sequence[Union[str, denovo.Quirk]]], 
#             optional): [description]. Defaults to None.

#     Raises:
#         TypeError: if all 'quirks' are not str or Quirk type or if 'keystone' is
#             not a str or Keystone type.

#     Returns:
#         denovo.core.quirks.Keystone: dataclass of Keystone subclass with 'quirks'
#             added.
        
#     """
#     bases = []
#     for quirk in more_itertools.always_iterable(quirks):
#         if isinstance(quirk, str):
#             bases.append(quirks[quirk])
#         elif isinstance(quirk, denovo.Quirk):
#             bases.append(quirk)
#         else:
#             raise TypeError('All quirks must be str or Quirk type')
#     if isinstance(keystone, str):
#         bases.append(keystones.classes[keystone])
#     elif isinstance(keystone, denovo.core.quirks.Keystone):
#         bases.append(keystone)
#     else:
#         raise TypeError('keystone must be a str or Keystone type')
#     return dataclasses.dataclass(type(name, tuple(bases), **kwargs))


# @dataclasses.dataclass
# class Validator(denovo.Quirk):
#     """Mixin for calling validation methods

#     Args:
#         validations (list[str]): a list of attributes that need validating.
#             Each item in 'validations' should have a corresponding method named 
#             f'_validate_{name}' or match a key in 'tools'. Defaults to an 
#             empty list. 
#         tools (denovo.Catalog):
               
#     """
#     validations: ClassVar[Sequence[str]] = []
#     tools: ClassVar[denovo.Catalog] = denovo.Catalog()

#     """ Public Methods """

#     def validate(self, validations: Sequence[str] = None) -> None:
#         """Validates or converts stored attributes.
        
#         Args:
#             validations (list[str]): a list of attributes that need validating.
#                 Each item in 'validations' should have a corresponding method 
#                 named f'_validate_{name}' or match a key in 'tools'. If not 
#                 passed, the 'validations' attribute will be used instead. 
#                 Defaults to None. 
        
#         """
#         if validations is None:
#             validations = self.validations
#         # Calls validation methods based on names listed in 'validations'.
#         for name in validations:
#             if hasattr(self, f'_validate_{name}'):
#                 kwargs = {name: getattr(self, name)}
#                 validated = getattr(self, f'_validate_{name}')(**kwargs: Any)
#             else:
#                 converter = self._initialize_converter(name = name)
#                 try:
#                     validated = converter.validate(
#                         item = getattr(self, name),
#                         instance = self)
#                 except AttributeError:
#                     validated = getattr(self, name)
#             setattr(self, name, validated)
#         return     

# #     def deannotate(self, annotation: Any) -> tuple[Any]:
# #         """Returns type annotations as a tuple.
        
# #         This allows even complicated annotations with Union to be converted to a
# #         form that fits with an isinstance call.

# #         Args:
# #             annotation (Any): type annotation.

# #         Returns:
# #             tuple[Any]: base level of stored type in an annotation
        
# #         """
# #         origin = get_origin(annotation)
# #         args = get_args(annotation)
# #         if origin is Union:
# #             accepts = tuple(self.deannotate(a)[0] for a in args)
# #         else:
# #             self.stores = origin
# #             accepts = get_args(annotation)
# #         return accepts

#     """ Private Methods """
    
#     def _initialize_converter(self, name: str) -> Converter:
#         """[summary]

#         Args:
#             converter (Union[Converter, Type[Converter]]): [description]

#         Returns:
#             Converter: [description]
#         """
#         try:
#             converter = self.tools[name]
#         except KeyError:
#             raise KeyError(
#                 f'No local or stored type validator exists for {name}')
#         return converter()             


# @dataclasses.dataclass
# class Converter(abc.ABC):
#     """Keystone class for type tools and validators.

#     Args:
#         base (str): 
#         parameters (dict[str, Any]):
#         alternatives (tuple[Type])
        
#     """
#     base: str = None
#     parameters: dict[str, Any] = dataclasses.field(default_factory = dict)
#     alterantives: tuple[Type] = dataclasses.field(default_factory = tuple)
#     default: Type = None

#     """ Initialization Methods """
    
#     def __init_subclass__(cls, **kwargs: Any):
#         """Adds 'cls' to 'Validator.tools' if it is a concrete class."""
#         super().__init_subclass__(**kwargs: Any)
#         if not abc.ABC in cls.__bases__:
#             key = denovo.modify.snakify(cls.__name__)
#             # Removes '_converter' from class name so that the key is consistent
#             # with the key name for the class being constructed.
#             try:
#                 key = key.replace('_converter', '')
#             except ValueError:
#                 pass
#             Validator.tools[key] = cls
                       
#     """ Public Methods """

#     def validate(self, item: Any, instance: object, **kwargs: Any) -> object:
#         """[summary]

#         Args:
#             item (Any): [description]
#             instance (object): [description]

#         Raises:
#             TypeError: [description]
#             AttributeError: [description]

#         Returns:
#             object: [description]
            
#         """ 
#         if hasattr(instance, 'library') and instance.library is not None:
#             kwargs = {
#                 k: self._kwargify(v, instance, item) 
#                 for k, v in self.parameters.items()}
#             try:
#                 base = getattr(instance.library, self.base)
#                 if item is None:
#                     validated = base(**kwargs: Any)
#                 elif isinstance(item, base):
#                     validated = item
#                     for key, value in kwargs.items():
#                         setattr(validated, key, value)
#                 elif inspect.isclass(item) and issubclass(item, base):
#                     validated = item(**kwargs: Any)
#                 elif (isinstance(item, str) 
#                         or isinstance(item, list)
#                         or isinstance(item, tuple)):
#                     validated = base.library.select(names = item)(**kwargs: Any)
#                 elif isinstance(item, self.alternatives) and self.alternatives:
#                     validated = base(item, **kwargs: Any)
#                 else:
#                     raise TypeError(
#                         f'{item} could not be validated or converted')
#             except AttributeError:
#                 validated = self.default(**kwargs: Any)
#         else:
#             try:
#                 validated = self.default(**kwargs: Any)
#             except (TypeError, ValueError):
#                 raise AttributeError(
#                     f'Cannot validate or convert {item} without library')
#         return validated

#     """ Private Methods """
    
#     def _kwargify(self, attribute: str, instance: object, item: Any) -> Any:
#         """[summary]

#         Args:
#             attribute (str): [description]
#             instance (object): [description]
#             item (Any): [description]

#         Returns:
#             Any: [description]
            
#         """
#         if attribute in ['self']:
#             return instance
#         elif attribute in ['str']:
#             return item
#         else:
#             return getattr(instance, attribute)
