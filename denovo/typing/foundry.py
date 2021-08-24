"""
foundry: classes for converting and validating types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:


ToDo:

    
"""
from __future__ import annotations
import ast
import collections
import dataclasses
import inspect
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Generic, Hashable, Iterable, 
                    list, Literal, Mapping, MutableMapping, MutableSequence, 
                    Optional, Sequence, set, tuple, Type, TypeVar, Union)

import denovo
from denovo.typing.types import (Adjacency, Chain, Composite, Connections, 
                                 dict, Dyad, Edge, 
                                 Edges, Group, Index, Integer, Kind, listing, 
                                 Matrix, Nodes, Path, Pipeline, Pipelines, Real, 
                                 String)


@dataclasses.dataclass
class Workshop(object):
    """Controls type conversion, class
    
    
    """
    kinds: dict[str, Kind] = dataclasses.field(
        default_factory = lambda: denovo.types.catalog)
    
    """ Properties """
    
    @property
    def matchers(self) -> dict[tuple[Type, ...], str]:
        return {denovo.converters.to_tuple(item = k.sources): k.name 
                for k in self.kinds.values()}
    
    @property
    def names(self) -> dict[Kind, str]:
        labels = {}
        for key, value in self.kinds.items():
            for item in denovo.converters.to_tuple(item = value.comparison):
                labels[item] = key
        return labels
        
    @property
    def types(self) -> dict[str, Type]:
        return {k.name: denovo.converters.to_tuple(item = k.comparison) 
                for k in self.kinds.values()}
    
    """Public Methods"""
    
    def categorize(self, item: Any) -> str:
        """[summary]

        Args:
            item (Any): [description]

        Raises:
            KeyError: [description]

        Returns:
            str: [description]
            
        """
        if inspect.isclass(item):
            method = issubclass
        else:
            method = isinstance
        for key, value in self.kinds.items():
            if method(item, key):
                return value
        raise KeyError(f'item does not match any recognized type')
       
    def convert(self, item: Any, output: Union[Kind, String], **kwargs: Any) -> Any:
        """[summary]

        Args:
            item (Any): [description]
            output (str): [description]

        Returns:
            Any: [description]
            
        """
        start = self.categorize(item = item)
        if not isinstance(output, String):
            stop = output
        else:
            stop = self.names[output]
        try:
            strict_key = denovo.typing.types.STRICT(start, stop)
            method = self.converters[strict_key]
        except KeyError:
            flexible_key = denovo.typing.types.FLEXIBLE(stop)
            method = self.converters[flexible_key]
        return method(item = item, **kwargs: Any)


# @dataclasses.dataclass
# class Validator(denovo.Quirk):
#     """Mixin for calling validation methods

#     Args:
#         validations (list[str]): a list of attributes that need validating.
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
#             validations (list[str]): a list of attributes that need validating.
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
    
#     def _initialize_converter(self, name: ClassVar[str]) -> Converter:
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
#         parameters (dict[str, Any]):
#         alternatives (tuple[Type])
        
#     """
#     base: str = None
#     parameters: dict[str, Any] = dataclasses.field(default_factory = dict)
#     alterantives: tuple[Type] = dataclasses.field(default_factory = tuple)
#     default: Type = None

#     """ Initialization Methods """
    
#     def __init_subclass__(cls, **kwargs: Any):
#         """Adds 'cls' to 'Validator.converters' if it is a concrete class."""
#         super().__init_subclass__(**kwargs: Any)
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
