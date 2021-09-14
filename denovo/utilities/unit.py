"""
kind: tools for classes, instances, and other python objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:   

   
ToDo:


"""
from __future__ import annotations
import collections.abc
import dataclasses
import inspect
import types
from typing import Any, Optional, Type, Union

import denovo


""" Type Aliases """

Signatures = dict[str, inspect.Signature]

""" Introspection Tools """

def get_attributes(item: Union[object, Type[Any]], 
                   exclude_private: bool = True) -> list[types.FunctionType]:
    """Returns methods of 'item'."""
    attributes = name_attributes(item = item, exclude_private = exclude_private)
    return [getattr(item, m) for m in attributes]

def get_methods(item: Union[object, Type[Any]], 
                exclude_private: bool = True) -> list[types.FunctionType]:
    """Returns methods of 'item'."""
    methods = name_methods(item = item, exclude_private = exclude_private)
    return [getattr(item, m) for m in methods]

def get_name(item: Any, default: Optional[str] = None) -> Optional[str]:
    """Returns str name representation of 'item'.
    
    Args:
        item (Any): item to determine a str name.

    Returns:
        str: a name representation of 'item.'
        
    """        
    if isinstance(item, str):
        return item
    else:
        if hasattr(item, 'name') and isinstance(item.name, str):
            return item.name
        else:
            try:
                return denovo.modify.snakify(item.__name__) # type: ignore
            except AttributeError:
                if item.__class__.__name__ is not None:
                    return denovo.modify.snakify( # type: ignore
                        item.__class__.__name__) 
                else:
                    return default

def get_parameters(item: Type[Any]) -> list[str]:
    """Returns list of parameters based on annotations of 'item'."""        
    return list(item.__annotations__.keys())

def get_properties(item: Union[object, Type[Any]], 
                   exclude_private: bool = True) -> list[Any]:
    """Returns properties of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    properties = name_properties(item = item, exclude_private = exclude_private)
    return [getattr(item, p) for p in properties]

def get_signatures(item: Union[object, Type[Any]], 
                   exclude_private: bool = True) -> dict[str, inspect.Signature]:
    """Returns method signatures of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    methods = name_methods(item = item, exclude_private = exclude_private)
    signatures = [inspect.signature(getattr(item, m)) for m in methods]
    return dict(zip(methods, signatures))
 
def has_methods(item: Union[object, Type[Any]], 
                methods: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'methods' which are methods."""
    methods = denovo.typing.convert.listify(item = methods)
    return all(denovo.tools.is_method(item = item, attribute = m) 
               for m in methods)

def has_properties(item: Union[object, Type[Any]], 
                   properties: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'properties' which are properties."""
    properties = denovo.typing.convert.listify(item = properties)
    return all(denovo.tools.is_property(item = item, attribute = p) 
               for p in properties)

def has_signatures(item: Union[object, Type[Any]], 
                   signatures: dict[str, inspect.Signature]) -> bool:
    """Returns whether 'item' has 'signatures' of its methods."""
    names = name_methods(item = item)
    methods = get_methods(item = item)
    item_signatures = dict(zip(names, [inspect.signature(m) for m in methods]))
    pass_test = True
    for name, parameters in signatures.items():
        if (not hasattr(item, name) 
                or not item_signatures[name] != parameters):
            pass_test = False
    return pass_test
    
def has_traits(item: Union[object, Type[Any]],
               attributes: Optional[list[str]] = None,
               methods: Optional[list[str]] = None,
               properties: Optional[list[str]] = None,
               signatures: Optional[Signatures] = None) -> bool:
    """Returns if 'item' has 'attributes', 'methods' and 'properties'."""
    if not inspect.isclass(item):
        item = item.__class__ 
    attributes = attributes or []
    methods = methods or []
    properties = properties or []
    signatures = signatures or {}
    if not methods and signatures:
        methods = list(signatures.keys())
    return (all(hasattr(item, a) for a in attributes)
            and has_methods(item = item, methods = methods)
            and has_properties(item = item, properties = properties)
            and has_signatures(item = item, signatures = signatures))

def name_attributes(item: Union[object, Type[Any]], 
                    exclude_private: bool = True) -> list[str]:
    """Returns simple data attribute names of 'item'."""
    attributes = [a for a in dir(item)
                  if is_attribute(item = item, attribute = a)]
    if exclude_private:
        attributes = [m for m in attributes if not m.startswith('_')]
    return attributes

def name_methods(item: Union[object, Type[Any]], 
                 exclude_private: bool = True) -> list[str]:
    """Returns method names of 'item'."""
    methods = [a for a in dir(item)
               if is_method(item = item, attribute = a)]
    if exclude_private:
        methods = [m for m in methods if not m.startswith('_')]
    return methods

def name_properties(item: Union[object, Type[Any]], 
                    exclude_private: bool = True) -> list[str]:
    """Returns method names of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    properties = [a for a in dir(item)
                  if is_property(item = item, attribute = a)]
    if exclude_private:
        properties = [p for p in properties if not p.startswith('_')]
    return properties
    
def is_iterable(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is iterable and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__ 
    return (issubclass(item, collections.abc.Iterable)  # type: ignore  
            and not issubclass(item, str)) # type: ignore  
    
def is_kind(item: Union[Type[Any], object], 
            kind: Type[denovo.typing.Kind]) -> bool:
     """Returns whether 'item' is an instance of subclass of 'kind'."""   
     return has_traits(item = item,
                       attributes = kind.attributes,
                       methods = kind.methods, 
                       properties = kind.properties,
                       signatures = kind.signatures)
    
def is_nested(item: collections.abc.Mapping[Any, Any]) -> bool:
    """Returns if 'item' is nested at least one-level."""
    return any(isinstance(v, collections.abc.Mapping) 
               for v in item.values())
 
def is_sequence(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is a sequence and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__ 
    return (issubclass(item, collections.abc.Sequence)  # type: ignore  
            and not issubclass(item, str)) # type: ignore  

""" Attribute Introspection Tools """

def is_attribute(item: Union[object, Type[Any]], 
                 attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a simple data attribute of 'item'."""
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return (not is_method(item = item, attribute = attribute)
            and not is_property(item = item, attribute = attribute))

def is_classvar(item: Union[object, Type[Any]], 
                attribute: str) -> bool:
    """Returns if 'attribute' is a class attribute of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    return (hasattr(item, attribute)
            and not is_method(item = item, attribute = attribute)
            and not is_property(item = item, attribute = attribute))

def is_method(item: Union[object, Type[Any]], 
              attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a method of 'item'."""
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return inspect.ismethod(attribute)

def is_property(item: Union[object, Type[Any]], 
                attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a property of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return isinstance(attribute, property)
