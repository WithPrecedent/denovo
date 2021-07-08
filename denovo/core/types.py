"""
types:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:


ToDo:
    subclass check for Dyad
    add date types and appropriate conversion functions
    
"""
from __future__ import annotations
import abc
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Generic, Hashable, Iterable, 
                    List, Literal, Mapping, MutableMapping, MutableSequence, 
                    Optional, Sequence, Set, Tuple, Type, TypeVar, Union)

import denovo


KindType = TypeVar('KindType')

kinds: Dict[str, Kind] = {}


""" Base Type """

@dataclasses.dataclass
class Kind(Generic[KindType], abc.ABC):
    """Base class for generic types used by denovo.
    
    Args:
    
    
    """
    name: ClassVar[str]
    comparison: ClassVar[Union[Type, Tuple[Type]]]
    sources: ClassVar[Tuple[Kind]]
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'kinds' dict."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library'.
        kinds[cls.name] = cls

    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return isinstance(instance, denovo.tools.tuplify(self.comparison))
    
    @classmethod
    def __subclasscheck__(self, subclass: Type) -> bool:
        return issubclass(subclass, denovo.tools.tuplify(self.comparison))


""" Mapping Types """

@dataclasses.dataclass
class Dictionary(Kind):
    
    name: ClassVar[str] = 'dictionary'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableMapping
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Dyad, Unknown])    


@dataclasses.dataclass
class DefaultDictionary(Kind):
    
    name: ClassVar[str] = 'default_dictionary'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableMapping
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Dyad, Unknown])
    
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, denovo.tools.tuplify(self.comparison))
                and hasattr(instance, 'default_factory'))


""" Numerical Types """

@dataclasses.dataclass
class Integer(Kind):
    
    name: ClassVar[str] = 'integer'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = int
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Real, String, Unknown]) 


@dataclasses.dataclass
class Real(Kind):
    
    name: ClassVar[str] = 'real'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = float
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Integer, String, Unknown]) 


""" Sequence Types """

@dataclasses.dataclass
class Chain(Kind, abc.ABC):
    
    name: ClassVar[str] = 'chain'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableSequence
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([String, Unknown])    


@dataclasses.dataclass
class Dyad(Kind):
    
    name: ClassVar[str] = 'dyad'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Sequence 
  
    """ Dunder Methods """
    
    @classmethod
    def __instancecheck__(self, instance: Any) -> bool:
        return (isinstance(instance, denovo.tools.tuplify(self.comparison)) 
                and len(instance) == 2
                and isinstance(instance[0], self.comparison)
                and isinstance(instance[1], self.comparison))
        
        
@dataclasses.dataclass
class Listing(Chain):
    
    name: ClassVar[str] = 'listing'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = MutableSequence  
     
        
""" Other Types """
         
@dataclasses.dataclass
class String(Kind):
    
    name: ClassVar[str] = 'string'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = str
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Listing, Unknown])   

    
@dataclasses.dataclass
class Disk(Kind):
    
    name: ClassVar[str] = 'disk'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = pathlib.Path
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Unknown, String])  

    
@dataclasses.dataclass
class Group(Kind):
    
    name: ClassVar[str] = 'group'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = tuple([Set, Tuple, Chain])
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Unknown, Chain])  
    
             
@dataclasses.dataclass
class Index(Kind):
    
    name: ClassVar[str] = 'index'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Hashable
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([Unknown])  
    

@dataclasses.dataclass
class Unknown(Kind):
    
    name: ClassVar[str] = 'unknown'
    comparison: ClassVar[Union[Type, Tuple[Type]]] = Literal
    sources: ClassVar[Tuple[Kind]] = lambda: tuple([]) 
       
