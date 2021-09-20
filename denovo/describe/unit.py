"""
unit: tools for examing classes, instances, and other python objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Class and Object Introspection Tools:
        check_attributes
        get_attributes
        get_methods
        get_name
        get_parameters
        get_properties
        get_signatures
        has_attributes
        has_methods
        has_properties
        has_signatures
        name_attributes
        name_methods
        name_properties
        is_container
        is_iterable
        is_nested
        is_sequence
    Attribute Introspection Tools:
        is_attribute
        is_class_attribute
        is_method
        is_property
    Container Introspection Tools:
        contains
        dict_contains
        list_contains
        tuple_contains
        
ToDo:


"""
from __future__ import annotations
from collections.abc import (
    Container, Iterable, Mapping, MutableMapping, MutableSequence, Sequence)
import inspect
import types
from typing import Any, Hashable, MutableMapping, Optional, Type, Union

import more_itertools

import denovo

""" Class and Object Introspection Tools """

def check_attributes(
    item: Union[object, Type[Any]], 
    attributes: MutableMapping[str, Type[Any]]) -> bool:
    """Returns whether 'attributes' exist in 'item' and are the right type.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        attributes (MutableMapping[str, Type[Any]]): dict where keys are the
            attribute names and values are the expected types of whose named
            attributes.
            
    Returns
        bool: whether all of the 'attributes' exist in 'item' and are of the
            proper type.
            
    """
    matched = True
    if inspect.isclass:
        for attribute, value in attributes.items():
            if value is not None:
                try:
                    testing = getattr(item, attribute)
                    testing = item.__annotations__[testing]
                except AttributeError:
                    return False
                try:
                    if not issubclass(testing, value):
                        return False
                except TypeError:
                    pass
    else:
        for attribute, value in attributes.items():
            if value is not None:
                try:
                    testing = getattr(item, attribute)
                except AttributeError:
                    return False
                try:
                    if not isinstance(testing, value):
                        return False
                except TypeError:
                    pass
    return matched

def get_attributes(
    item: Union[object, Type[Any]], 
    exclude_private: bool = True) -> Union[MutableMapping[str, Any],
                                           MutableSequence[str]]:
    """Returns dict of attributes of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        exclude_private (bool): whether to exclude (True) attributes that have 
            names beginning with '_' or not (False).
                        
    Returns
        Union[MutableMapping[str, Any], MutableSequence[str]]: dict of 
            attributes in 'item' if an instance is passed or a list of attribute
            names if a class is passed.
            
    """
    attributes = name_attributes(item = item, exclude_private = exclude_private)
    if inspect.isclass(item):
        return attributes
    else:
        values = [getattr(item, m) for m in attributes]
        return dict(zip(attributes, values))

def get_methods(
    item: Union[object, Type[Any]], 
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

def get_properties(
    item: Union[object, Type[Any]], 
    exclude_private: bool = True) -> list[Any]:
    """Returns properties of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    properties = name_properties(item = item, exclude_private = exclude_private)
    return [getattr(item, p) for p in properties]

def get_signatures(
    item: Union[object, Type[Any]], 
    exclude_private: bool = True) -> dict[str, inspect.Signature]:
    """Returns method signatures of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    methods = name_methods(item = item, exclude_private = exclude_private)
    signatures = [inspect.signature(getattr(item, m)) for m in methods]
    return dict(zip(methods, signatures))

def has_attributes(
    item: Union[object, Type[Any]], 
    attributes: Union[list[str], MutableMapping[str, Type[Any]]]) -> bool:
    """Returns whether 'attributes' exist in 'item'.
    
    If passed 'attributes' are a dict, this method will automatically call
    'check_attributes" instead.
    
    """
    if isinstance(attributes, MutableMapping):
        return check_attributes(item = item, attributes = attributes)
    else:
        return all(hasattr(item, a) for a in attributes)

def has_methods(
    item: Union[object, Type[Any]], 
    methods: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'methods' which are methods."""
    methods = list(more_itertools.always_iterable(methods))
    return all(is_method(item = item, attribute = m) for m in methods)

def has_properties(
    item: Union[object, Type[Any]], 
    properties: Union[str, list[str]]) -> bool:
    """Returns whether 'item' has 'properties' which are properties."""
    properties = list(more_itertools.always_iterable(properties))
    return all(is_property(item = item, attribute = p) for p in properties)

def has_signatures(
    item: Union[object, Type[Any]], 
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
    
def has_traits(
    item: Union[object, Type[Any]],
    attributes: Optional[list[str]] = None,
    methods: Optional[list[str]] = None,
    properties: Optional[list[str]] = None,
    signatures: Optional[MutableMapping[str, inspect.Signature]] = None) -> bool:
    """Returns if 'item' has 'attributes', 'methods' and 'properties'."""
    if not inspect.isclass(item):
        item = item.__class__ 
    attributes = attributes or []
    methods = methods or []
    properties = properties or []
    signatures = signatures or {}
    if not methods and signatures:
        methods = list(signatures.keys())
    return (
        all(hasattr(item, a) for a in attributes)
        and has_methods(item = item, methods = methods)
        and has_properties(item = item, properties = properties)
        and has_signatures(item = item, signatures = signatures))

def name_attributes(
    item: Union[object, Type[Any]], 
    exclude_private: bool = True) -> list[str]:
    """Returns simple data attribute names of 'item'."""
    attributes = [a for a in dir(item)
                  if is_attribute(item = item, attribute = a)]
    if exclude_private:
        attributes = [m for m in attributes if not m.startswith('_')]
    return attributes

def name_methods(
    item: Union[object, Type[Any]], 
    exclude_private: bool = True) -> list[str]:
    """Returns method names of 'item'."""
    methods = [a for a in dir(item)
               if is_method(item = item, attribute = a)]
    if exclude_private:
        methods = [m for m in methods if not m.startswith('_')]
    return methods

def name_properties(
    item: Union[object, Type[Any]], 
    exclude_private: bool = True) -> list[str]:
    """Returns method names of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    properties = [a for a in dir(item)
                  if is_property(item = item, attribute = a)]
    if exclude_private:
        properties = [p for p in properties if not p.startswith('_')]
    return properties

def is_container(item: Union[object, Type[Any]]) -> bool:
    """Return if 'item' is a container."""  
    if not inspect.isclass(item):
        item = item.__class__ 
    return issubclass(item, Container) # type: ignore
        
def is_iterable(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is iterable and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__ 
    return (
        issubclass(item, Iterable)  # type: ignore  
        and not issubclass(item, str)) # type: ignore  
    
def is_nested(item: Mapping[Any, Any]) -> bool:
    """Returns if 'item' is nested at least one-level."""
    return any(isinstance(v, Mapping) 
               for v in item.values())
 
def is_sequence(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is a sequence and is NOT a str type."""
    if not inspect.isclass(item):
        item = item.__class__ 
    return (
        issubclass(item, Sequence)  # type: ignore  
        and not issubclass(item, str)) # type: ignore  

""" Attribute Introspection Tools """

def is_attribute(
    item: Union[object, Type[Any]], 
    attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a simple data attribute of 'item'."""
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return (
        not is_method(item = item, attribute = attribute)
        and not is_property(item = item, attribute = attribute))

def is_class_attribute(
    item: Union[object, Type[Any]], 
    attribute: str) -> bool:
    """Returns if 'attribute' is a class attribute of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    return (
        hasattr(item, attribute)
        and not is_method(item = item, attribute = attribute)
        and not is_property(item = item, attribute = attribute))

def is_method(
    item: Union[object, Type[Any]], 
    attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a method of 'item'."""
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return inspect.ismethod(attribute)

def is_property(
    item: Union[object, Type[Any]], 
    attribute: Union[str, types.FunctionType]) -> bool:
    """Returns if 'attribute' is a property of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    if isinstance(attribute, str):
        attribute = getattr(item, attribute)
    return isinstance(attribute, property)

""" Container Introspection Tools """

@denovo.dynamic.dispatcher # type: ignore  
def contains(item: Any, contents: Any) -> bool:
    """Returns whether 'item' contains the data type(s) in 'contents'."""
    raise TypeError(f'item is not a supported type for {__name__}')

@contains.register # type: ignore  
def dict_contains(
    item: MutableMapping[Hashable, Any], 
    contents: tuple[Union[Type[Any], tuple[Type[Any], ...]],
                    Union[Type[Any], tuple[Type[Any], ...]]]) -> bool:
    """Returns whether dict 'item' contains the data type(s) in 'contents'.

    Args:
        item (MutableMapping[Hashable, Any]): [description]
        contents (tuple[Union[Type[Any], tuple[Type[Any], ...]], 
            Union[Type[Any], tuple[Type[Any], ...]]]): [description]

    Returns:
        bool: [description]
    """
    return ( # type: ignore
        list_contains(item = item.keys(), contents = contents[0])
        and list_contains(item = item.values(), contents = contents[1]))

@contains.register # type: ignore     
def list_contains(
    item: MutableSequence[Any],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether list 'item' contains the data type(s) in 'contents'.

    Args:
        item (MutableSequence[Any]): [description]
        contents (Union[Type[Any], tuple[Type[Any], ...]]): [description]

    Returns:
        bool: [description]
    """
    return all(isinstance(i, contents) for i in item)

@contains.register # type: ignore     
def set_contains(
    item: set[Any],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether list 'item' contains the data type(s) in 'contents'.

    Args:
        item (set[Any]): [description]
        contents (Union[Type[Any], tuple[Type[Any], ...]]): [description]

    Returns:
        bool: [description]
    """
    return list_contains(item = item, contents = contents) # type: ignore

@contains.register # type: ignore  
def tuple_contains(
    item: tuple[Any, ...],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether tuple 'item' contains the data type(s) in 'contents'.

    Args:
        item (tuple[Any, ...]): [description]
        contents (Union[Type[Any], tuple[Type[Any], ...]]): [description]

    Returns:
        bool: [description]
    """
    if isinstance(contents, tuple) and len(item) == len(contents):
        return all(isinstance(item[i], contents[i]) for i in enumerate(item)) # type: ignore
    else:
        return all(isinstance(item[i], contents) for i in item)
    