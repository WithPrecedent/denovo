"""
framework:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    Library (object):
    Quirk (ABC): abstract base class for all denovo quirks, which are pseudo-
        mixins that sometimes do more than add functionality to subclasses. 
    Keystone (Quirk, ABC):
    build_keystone (FunctionType):
    Validator (Quirk):
    Converter (ABC):

ToDo:
    Validator support for complex types like List[List[str]]
    Add deannotation ability to Validator to automatically determine needed
        converters
    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)
# from typing import get_args, get_origin

import more_itertools

import denovo


quirks: denovo.Catalog[str, denovo.Quirk] = denovo.Catalog()
keystones: denovo.Library = denovo.quirks.Keystone.library

meta_sources = {}


def build_keystone(name: str,
                   keystone: Union[str, denovo.quirks.Keystone] = None, 
                   quirks: Union[str, 
                                 denovo.Quirk, 
                                 Sequence[Union[str, denovo.Quirk]]] = None,
                   **kwargs) -> denovo.quirks.Keystone:
    """[summary]

    Args:
        name (str): [description]
        keystone (Union[str, denovo.quirks.Keystone], optional): [description]. 
            Defaults to None.
        quirks (Union[str, denovo.Quirk, Sequence[Union[str, denovo.Quirk]]], 
            optional): [description]. Defaults to None.

    Raises:
        TypeError: if all 'quirks' are not str or Quirk type or if 'keystone' is
            not a str or Keystone type.

    Returns:
        denovo.quirks.Keystone: dataclass of Keystone subclass with 'quirks'
            added.
        
    """
    bases = []
    for quirk in more_itertools.always_iterable(quirks):
        if isinstance(quirk, str):
            bases.append(quirks[quirk])
        elif isinstance(quirk, denovo.Quirk):
            bases.append(quirk)
        else:
            raise TypeError('All quirks must be str or Quirk type')
    if isinstance(keystone, str):
        bases.append(keystones.classes[keystone])
    elif isinstance(keystone, denovo.quirks.Keystone):
        bases.append(keystone)
    else:
        raise TypeError('keystone must be a str or Keystone type')
    return dataclasses.dataclass(type(name, tuple(bases), **kwargs))

@dataclasses.dataclass
class Origin(object):
    
    annotation: Type
    sources: Mapping[Union[Type, Tuple[Type], str]]

@dataclasses.dataclass
class Workshop(object):
    
    sources: Mapping[Union[Type, Tuple[Type], str]]
    
    def convert(self, source: Any, output: Type) -> Any:
    
    
# @dataclasses.dataclass
# class Validator(denovo.Quirk):
#     """Mixin for calling validation methods

#     Args:
#         validations (List[str]): a list of attributes that need validating.
#             Each item in 'validations' should have a corresponding method named 
#             f'_validate_{name}' or match a key in 'converters'. Defaults to an 
#             empty list. 
#         converters (denovo.Catalog):
               
#     """
#     validations: ClassVar[Sequence[str]] = []
#     converters: ClassVar[denovo.Catalog] = denovo.Catalog()

#     """ Public Methods """

#     def validate(self, validations: Sequence[str] = None) -> None:
#         """Validates or converts stored attributes.
        
#         Args:
#             validations (List[str]): a list of attributes that need validating.
#                 Each item in 'validations' should have a corresponding method 
#                 named f'_validate_{name}' or match a key in 'converters'. If not 
#                 passed, the 'validations' attribute will be used instead. 
#                 Defaults to None. 
        
#         """
#         if validations is None:
#             validations = self.validations
#         # Calls validation methods based on names listed in 'validations'.
#         for name in validations:
#             if hasattr(self, f'_validate_{name}'):
#                 kwargs = {name: getattr(self, name)}
#                 validated = getattr(self, f'_validate_{name}')(**kwargs)
#             else:
#                 converter = self._initialize_converter(name = name)
#                 try:
#                     validated = converter.validate(
#                         item = getattr(self, name),
#                         instance = self)
#                 except AttributeError:
#                     validated = getattr(self, name)
#             setattr(self, name, validated)
#         return self     

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
#             converter = self.converters[name]
#         except KeyError:
#             raise KeyError(
#                 f'No local or stored type validator exists for {name}')
#         return converter()             


# @dataclasses.dataclass
# class Converter(abc.ABC):
#     """Keystone class for type converters and validators.

#     Args:
#         base (str): 
#         parameters (Dict[str, Any]):
#         alternatives (tuple[Type])
        
#     """
#     base: str = None
#     parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
#     alterantives: tuple[Type] = dataclasses.field(default_factory = tuple)
#     default: Type = None

#     """ Initialization Methods """
    
#     def __init_subclass__(cls, **kwargs):
#         """Adds 'cls' to 'Validator.converters' if it is a concrete class."""
#         super().__init_subclass__(**kwargs)
#         if not abc.ABC in cls.__bases__:
#             key = denovo.tools.snakify(cls.__name__)
#             # Removes '_converter' from class name so that the key is consistent
#             # with the key name for the class being constructed.
#             try:
#                 key = key.replace('_converter', '')
#             except ValueError:
#                 pass
#             Validator.converters[key] = cls
                       
#     """ Public Methods """

#     def validate(self, item: Any, instance: object, **kwargs) -> object:
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
#                     validated = base(**kwargs)
#                 elif isinstance(item, base):
#                     validated = item
#                     for key, value in kwargs.items():
#                         setattr(validated, key, value)
#                 elif inspect.isclass(item) and issubclass(item, base):
#                     validated = item(**kwargs)
#                 elif (isinstance(item, str) 
#                         or isinstance(item, List)
#                         or isinstance(item, Tuple)):
#                     validated = base.library.select(names = item)(**kwargs)
#                 elif isinstance(item, self.alternatives) and self.alternatives:
#                     validated = base(item, **kwargs)
#                 else:
#                     raise TypeError(
#                         f'{item} could not be validated or converted')
#             except AttributeError:
#                 validated = self.default(**kwargs)
#         else:
#             try:
#                 validated = self.default(**kwargs)
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
