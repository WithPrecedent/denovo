"""
quirks: denovo mixins
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Quirk (ABC): base class for quirks.
    Element (Quirk): quirk that automatically assigns a 'name' attribute if 
        none is passed. The default 'name' will be the snakecase name of the 
        class.
    Factory (Quirk): quirk that determines the appropriate constructor when a 
        universal 'create' classmethod is called. The appropriate construction 
        method should have the following form: "from_{str value matching key
        Type in 'sources' class variable}"
    Importer (Quirk): quirk that supports lazy importation of modules and items 
        stored within them.

ToDo:
    Fix quirks which are currently commented out.

"""
from __future__ import annotations
import abc
from collections import defaultdict
import dataclasses
import importlib
import inspect
import logging
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import more_itertools

import denovo


@dataclasses.dataclass
class Quirk(abc.ABC):
    """Base class for denovo quirks (mixin-approximations).

    denovo quirks are not technically mixins because some have required 
    attributes. Traditionally, mixins do not have any attributes and only add 
    functionality. quirks are designed for multiple inheritance and easy 
    addition to other classes like mixins but do not meet the formal definition. 
    Despite that face, quirks are sometimes internally referred to as "mixins" 
    because their design and goals are otherwise similar to mixins.

    Args:
        quirks (ClassVar[Catalog]): a catalog of Quirk subclasses.
        
    Namespaces: __init_subclass__
    
    """
    quirks: ClassVar[denovo.Catalog] = denovo.Catalog()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'quirks' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Adds concrete quirks to 'quirks' using 'key'.
        if not abc.ABC in cls.__bases__:
            # Creates a snakecase key of the class name.
            key = denovo.tools.snakify(cls.__name__)
            # Removes "_quirk" from class name if you choose to use 'Quirk' as
            # a suffix to Quirk subclasses. denovo doesn't follow this practice 
            # but includes this adjustment for users that which to use that 
            # naming convention and don't want to type "_quirk" at the end of
            # a key when accessing 'quirks'.
            try:
                key = key.replace('_quirk', '')
            except ValueError:
                pass
            # Stores 'cls' in 'quirks'.
            cls.quirks[key] = cls

    
@dataclasses.dataclass
class Element(Quirk):
    """Mixin for classes that need a 'name' attribute.
    
    Automatically provides a 'name' attribute to a subclass, if it isn't 
    otherwise passed. This quirk is used for nodes stored in denovo's composite
    structures.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout denovo. For example, if a denovo 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. 
            Defaults to None. 

    Namespaces: name, __post_init__, and _get_name

    """
    name: str = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
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
        return denovo.tools.snakify(self.__class__.__name__)


@dataclasses.dataclass
class Factory(Quirk):
    """Supports internal creation and automatic external parameterization.
    
    Args:
        sources (ClassVar[Mapping[Type, str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'sources' to correspond to an internal factory classmethod named
            f'from_{first item in sources}'. Defaults to an empty list.
    
    Namespaces: 'create' and 'sources'        
    
    """
    sources: ClassVar[Mapping[Type, str]] = {}
    
    """ Class Methods """

    @classmethod
    def create(cls, source: Any, **kwargs) -> Factory:
        """Calls corresponding creation class method to instance a subclass.
        
        For create to work properly, there should be a corresponding classmethod
        named f'from_{value in sources}'.

        Raises:
            AttributeError: If an appropriate method does not exist for the
                data type of 'source.'
            ValueError: If the type of 'source' does not match a key in 
                'sources'.

        Returns:
            Factory: instance of a Factory subclass.
            
        """
        for kind, suffix in cls.sources.items():
            if isinstance(source, kind):
                method_name = f'from_{suffix}'
                try:
                    method = getattr(cls, method_name)
                except AttributeError:
                    raise AttributeError(f'{method_name} does not exist')
                kwargs[suffix] = source
                return method(**kwargs)
        raise ValueError(f'source does not match any recognized types in '
                         'sources')  


@dataclasses.dataclass
class Importer(Quirk):
    """Faciliates lazy importing from modules.

    Subclasses with attributes storing strings containing import paths 
    (indicated by having a '.' in their text) will automatically have those
    attribute values turned into the corresponding stored classes.

    The 'importify' method also allows this process to be performed manually.

    Subclasses should not have custom '__getattribute__' methods or properties
    to avoid errors. If a subclass absolutely must include a custom 
    '__getattribute__' method, it should incorporate the code from this class.

    Namespaces: 'importify', '__getattribute__'
    
    """
     
    """ Public Methods """

    def importify(self, path: str) -> Any:
        """Returns object named by 'key'.

        Args:
            path (str): import path of class, function, or variable.
            
        Returns:
            Any: item from a python module.

        """
        item = path.split('.')[-1]
        module = path[:-len(item) - 1]
        try:
            imported = getattr(importlib.import_module(module), item)
        except (ImportError, AttributeError):
            raise ImportError(f'failed to load {item} in {module}')
        return imported

    """ Dunder Methods """

    def __getattribute__(self, name: str) -> Any:
        """Converts stored import paths into the corresponding objects.

        If an import path is stored, that attribute is permanently converted
        from a str to the imported object or class.
        
        Args:
            name (str): name of attribute sought.

        Returns:
            Any: the stored value or, if the value is an import path, the
                class or object stored at the designated import path.
            
        """
        value = super().__getattribute__(name)
        if (isinstance(value, str) and '.' in value):
            try:
                value = self.importify(path = value)
                super().__setattr__(name, value)
            except ImportError:
                pass
        return value
   
    
# @dataclasses.dataclass
# class Coordinator(Quirk):
#     """Supports internal creation and automatic external parameterization.
    
#     Args:
#         sources (ClassVar[Mapping[Type, str]]): attributes needed from 
#             another instance for some method within a subclass. The first item
#             in 'sources' to correspond to an internal factory classmethod named
#             f'from_{first item in sources}'. Defaults to an empty list.
    
#     Namespaces: 'create' and 'parameterize'        
#     """
#     sources: ClassVar[Mapping[Type, str]] = {}
    
#     """ Class Methods """

#     @classmethod
#     def create(cls, source: Any, **kwargs) -> Factory:
#         """Calls corresponding creation class method to instance a subclass.
        
#         For create to work properly, there should be a corresponding classmethod
#         named f'from_{item in sources}'.

#         Raises:
#             ValueError: If there is no corresponding method.

#         Returns:
#             Factory: instance of a Factory subclass.
            
#         """
#         sources = list(more_itertools.always_iterable(cls.sources))
#         if sources[0] in ['self']:
#             suffix = tuple(kwargs.keys())[0]
#         else:
#             suffix = sources[0]
#         method = getattr(cls, f'from_{suffix}')
#         for need in sources:
#             if need not in kwargs and need not in ['self']:
#                 raise ValueError(f'The create method must include a {need} '
#                                  f'argument')
#         return method(**kwargs)      
    
#     @classmethod
#     def parameterize(cls, instance: object) -> Mapping[str, Any]:
#         """Populates keywords from 'instance' based on 'sources'.

#         Args:
#             instance (object): instance with attributes or items in its 
#                 'contents' attribute with data to compose arguments to be
#                 passed to the 'create' classmethod.

#         Raises:
#             KeyError: if data could not be found for an argument.

#         Returns:
#             Mapping[str, Any]: keyword parameters and arguments to pass to the
#                 'create' classmethod.
            
#         """
#         kwargs = {}
#         for need in more_itertools.always_iterable(cls.sources):
#             if need in ['self']:
#                 key = denovo.tools.snakify(instance.__class__.__name__)
#                 kwargs[key] = instance
#             else:
#                 try:
#                     kwargs[need] = getattr(instance, need)
#                 except AttributeError:
#                     try:
#                         kwargs[need] = instance.contents[need]
#                     except (AttributeError, KeyError):
#                         raise KeyError(
#                             f'{need} could not be found in order to call a '
#                             f'method of {cls.__name__}')
#         return kwargs


# @dataclasses.dataclass
# class Logger(Quirk):
    
#     @property
#     def logger(self):
#         name = f'{self.__module__}.{self.__class__.__name__}'
#         return logging.getLogger(name)

# @dataclasses.dataclass
# class Proxified(object):
#     """ which creates a proxy name for a Element subclass attribute.

#     The 'proxify' method dynamically creates a property to access the stored
#     attribute. This allows class instances to customize names of stored
#     attributes while still maintaining the interface of the base denovo
#     classes.

#     Only one proxy should be created per class. Otherwise, the created proxy
#     properties will all point to the same attribute.

#     Namespaces: 'proxify', '_proxy_getter', '_proxy_setter', 
#         '_proxy_deleter', '_proxify_attribute', '_proxify_method', the name of
#         the proxy property set by the user with the 'proxify' method.
       
#     To Do:
#         Add property to class instead of instance to prevent return of property
#             object.
#         Implement '__set_name__' in a secondary class to denovo the code and
#             namespace usage.
        
#     """

#     """ Public Methods """

#     def proxify(self,
#             proxy: str,
#             attribute: str,
#             default_value: Any = None,
#             proxify_methods: bool = True) -> None:
#         """Adds a proxy property to refer to class attribute.

#         Args:
#             proxy (str): name of proxy property to create.
#             attribute (str): name of attribute to link the proxy property to.
#             default_value (Any): default value to use when deleting 'attribute' 
#                 with '__delitem__'. Defaults to None.
#             proxify_methods (bool): whether to create proxy methods replacing 
#                 'attribute' in the original method name with the string passed 
#                 in 'proxy'. So, for example, 'add_chapter' would become 
#                 'add_recipe' if 'proxy' was 'recipe' and 'attribute' was
#                 'chapter'. The original method remains as well as the proxy.
#                 This does not change the rest of the signature of the method so
#                 parameter names remain the same. Defaults to True.

#         """
#         self._proxied_attribute = attribute
#         self._default_proxy_value = default_value
#         self._proxify_attribute(proxy = proxy)
#         if proxify_methods:
#             self._proxify_methods(proxy = proxy)
#         return self

#     """ Proxy Property Methods """

#     def _proxy_getter(self) -> Any:
#         """Proxy getter for '_proxied_attribute'.

#         Returns:
#             Any: value stored at '_proxied_attribute'.

#         """
#         return getattr(self, self._proxied_attribute)

#     def _proxy_setter(self, value: Any) -> None:
#         """Proxy setter for '_proxied_attribute'.

#         Args:
#             value (Any): value to set attribute to.

#         """
#         setattr(self, self._proxied_attribute, value)
#         return self

#     def _proxy_deleter(self) -> None:
#         """Proxy deleter for '_proxied_attribute'."""
#         setattr(self, self._proxied_attribute, self._default_proxy_value)
#         return self

#     """ Other Private Methods """

#     def _proxify_attribute(self, proxy: str) -> None:
#         """Creates proxy property for '_proxied_attribute'.

#         Args:
#             proxy (str): name of proxy property to create.

#         """
#         setattr(self, proxy, property(
#             fget = self._proxy_getter,
#             fset = self._proxy_setter,
#             fdel = self._proxy_deleter))
#         return self

#     def _proxify_methods(self, proxy: str) -> None:
#         """Creates proxy method with an alternate name.

#         Args:
#             proxy (str): name of proxy to repalce in method names.

#         """
#         for item in dir(self):
#             if (self._proxied_attribute in item
#                     and not item.startswith('__')
#                     and callable(item)):
#                 self.__dict__[item.replace(self._proxied_attribute, proxy)] = (
#                     getattr(self, item))
#         return self
 
      