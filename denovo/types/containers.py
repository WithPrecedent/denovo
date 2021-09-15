"""
containers: denovo basic container classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

All denovo containers have a 'contents' attribute where an item or items are
internally stored. This is used instead of the normal 'data' attribute used in
base python classes to make it easier for users to know which object they are
accessing when using either 'contents' or 'data'.

Contents:
    Proxy (Container): basic wrapper for a stored python object. Dunder methods 
        attempt to intelligently apply access methods to either the wrapper or 
        the wrapped item.
    Bunch (Collection, ABC): base class for denovo collections that requires
        subclasses to have 'add' and 'subset' methods. 
    Manifest (Bunch, MutableSequence): denovo drop-in replacement for a python 
        list with additional functionality.
    Hybrid (Manifest): iterable with both dict and list interfaces.
    Lexicon (Bunch, MutableMapping): denovo's drop-in replacement for a python
        dict with some added functionality.
    Catalog (Lexicon): wildcard-accepting dict which is primarily intended for 
        storing different options and strategies. It also returns lists of 
        matches if a list of keys is provided.
    Library (object): registry for storing, accessing, and instancing classes
        and instances.
        
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Collection, Container, Hashable, Iterable, Mapping, MutableMapping, 
    MutableSequence, Sequence)
import copy
import dataclasses
import inspect
from typing import Any, Optional, Type, Union

import more_itertools

import denovo
 
""" (Mostly) Transparent Wrapper """

@dataclasses.dataclass
class Proxy(Container):
    """Basic wrapper class.
    
    A Proxy differs than an ordinary container in 2 significant ways:
        1) When an 'in' call is made, the '__contains__' method first looks to
            see if the item is stored in 'contents' (if 'contents' is a 
            collection). If that check gets a TypeError, the method then checks
            if the item is equivalent to 'contents'. This allows a Proxy to be
            agnostic as to the type of item(s) in 'contents' while returning the
            expected result from an 'in' call.
        2) Access methods for getting, setting, and deleting try to 
            intelligently direct the user's call to the proxy or stored object.
            So, for example, when a user tries to set an attribute on the proxy,
            the method will replace an attribute that exists in the proxy if
            one exists. But if there is no such attribute, the set method is
            applied to the object stored in 'contents'.

    Args:
        contents (Any): any stored item(s). Defaults to None.
        
    ToDo:
        Add more dunder methods to address less common and fringe cases for use
            of a Proxy class.
        
    """
    contents: Any = None

    """ Dunder Methods """
       
    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equal to 'contents'.

        Args:
            item (Any): item to check versus 'contents'
            
        Returns:
            bool: if 'item' is in or equal to 'contents' (True). Otherwise, it
                returns False.

        """
        try:
            return item in self.contents
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

""" Generic Collection with Kind Typing """

@dataclasses.dataclass # type: ignore
class Bunch(denovo.framework.Kind, Collection, abc.ABC): # type: ignore
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
                        
""" Generic list """

@dataclasses.dataclass # type: ignore
class Manifest(Bunch, MutableSequence): # type: ignore
    """Basic denovo list replacement.
    
    A Manifest differs from an ordinary python list only in ways required by
    inheriting from Bunch: 'add' and 'subset' methods, storing data in 
    'contents', and allowing the '+' operator to join Manifests with other lists 
    and Manifests).
    
    The 'add' method attempts to extend 'contents' with the item to be added.
    If this fails, it appends the item to 'contents'.
            
    Args:
        contents (MutableSequence[Any]): items to store in a list. Defaults to 
            an empty list.
        
    """
    contents: MutableSequence[Any] = dataclasses.field(default_factory = list)

    """ Public Methods """

    def add(self, item: Union[Any, Sequence[Any]]) -> None:
        """Tries to extend 'contents' with 'item'. Otherwise, appends.

        Args:
            item (Union[Any, Sequence[Any]]): item(s) to add to the 'contents' 
                attribute.
                
        """
        if isinstance(item, Sequence) and not isinstance(item, str):
            self.contents.extend(item)
        else:
            self.contents.append(item)
        return

    def insert(self, index: int, item: Any) -> None:
        """Inserts 'item' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'item' at.
            item (Any): object to be inserted.
            
        """
        self.contents.insert(index, item)
        return
               
    def subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None, 
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Manifest:
        """Returns a new instance with a subset of 'contents'.

        This method applies 'include' before 'exclude' if both are passed. If
        'include' is None, all existing keys will be added before 'exclude' is
        applied.
        
        Args:
            include (Union[Hashable, Sequence[Hashable]]): item(s) to include in 
                the new Manifest instance.
            exclude (Union[Hashable, Sequence[Hashable]]: item(s) to exclude in 
                the new Manifest instance.                
                
        Returns:
            Manifest: with only items from 'include' and no items in 'exclude'.

        """
        if include is None and exclude is None:
            raise ValueError('include or exclude must not be None')
        else:
            if include is None:
                contents = self.contents
            else:
                include = list(more_itertools.always_iterable(include))
                contents = [i for i in self.contents if i in include]
            if exclude is not None:
                exclude = list(more_itertools.always_iterable(exclude))
                contents = [i for i in contents if i not in exclude]
            new_manifest = copy.deepcopy(self)
            new_manifest.contents = contents
        return new_manifest
                       
    """ Dunder Methods """

    def __getitem__(self, index: Any) -> Any:
        """Returns value(s) for 'key' in 'contents'.

        Args:
            index (Any): index to search for in 'contents'.

        Returns:
            Any: item stored in 'contents' at key.

        """
        return self.contents[index]
            
    def __setitem__(self, index: Any, value: Any) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            index (Any): index to set 'value' to in 'contents'.
            value (Any): value to be set at 'key' in 'contents'.

        """
        self.contents[index] = value
        return

    def __delitem__(self, index: Any) -> None:
        """Deletes item at 'key' index in 'contents'.

        Args:
            index (Any): index in 'contents' to delete.

        """
        del self.contents[index]
        return

""" list with a dict Interface """

@dataclasses.dataclass # type: ignore
class Hybrid(Manifest):
    """Iterable that has both a dict and list interfaces.
    
    Hybrid combines the functionality and interfaces of python dicts and lists.
    It allows duplicate keys and list-like iteration while supporting the easier
    access methods of dictionaries. In order to support this hybrid approach to
    iterables, Hybrid can only store items that are hashable or have a 'name' 
    attribute or property that contains or returns a hashable value.

    A Hybrid inherits the differences between a Manifest and an ordinary python 
    list.
    
    A Hybrid differs from a Manifest in 3 significant ways:
        1) It only stores hashable items or objects with 'name' attributes or 
            properties that contain hashable items.
        2) Hybrid has an interface of both a dict and a list, but stores a list. 
            Hybrid does this by taking advantage of the 'name' attribute or
            hashability of stored items. A 'name' or hash acts as a key to 
            create the facade of a dict with the items in the stored list 
            serving as values. This allows for duplicate keys for storing items, 
            simpler iteration than a dict, and support for returning multiple 
            matching items. This design comes at the expense of lookup speed. As 
            a result, Hybrid should only be used if a high volume of access 
            calls is not anticipated. Ordinarily, the loss of lookup speed 
            should have negligible effect on overall performance.
        3) Hybrids should not store int types. This ensures that when, for 
            example, a 'hybrid[3]' is called, the item at that index is 
            returned. If int types are stored, that call would create 
            uncertainty as to whether an index or item should be returned. By
            design, int types are assumed to be calls to return the item at that
            index.

    Args:
        contents (MutableSequence[Any]): items to store in a list. Defaults to 
            an empty list.
        default_factory (Any): default value to return when the 'get' method is 
            used.
               
    """
    contents: MutableSequence[Any] = dataclasses.field(default_factory = list)
    default_factory: Any = None
        
    """ Public Methods """

    def get(self, key: Union[Any, int]) -> Union[Any, Sequence[Any]]:
        """Returns value in 'contents' or value in 'default_factory' attribute.
        
        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
                
        Returns:
            Union[Any, Sequence[Any]]: items in 'contents' or value in 
                'default_factory' attribute. 
        """
        try:
            return[key]
        except KeyError:
            return self.default_factory

    def items(self) -> tuple[tuple[Hashable, Any], ...]:
        """Emulates python dict 'items' method.
        
        Returns:
            tuple[tuple[Any, Any]: an iterable equivalent to dict.items(). A 
                Hybrid cannot actually create an ItemsView because that would 
                eliminate any duplicate keys, which are permitted by Hybrid.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> tuple[Hashable, ...]:
        """Emulates python dict 'keys' method.
        
        Returns:
            tuple[Any]: an iterable equivalent to dict.keys(). A Hybrid cannot
                actually create an KeysView because that would eliminate any
                duplicate keys, which are permitted by Hybrid.
            
        """
        return tuple([self._hashify(item = c) for c in self.contents])

    def setdefault(self, value: Any) -> None:
        """sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self.default_factory = value 
        return

    def update(self, items: Mapping[Any, Any]) -> None:
        """Mimics the dict 'update' method by extending 'contents' with 'items'.
        
        Args:
            items (Dict[Any, Any]): items to add to the 'contents' attribute. 
                The values of 'items' are added to 'contents' and the keys 
                become the 'name' attributes of those values. As a result, the 
                keys of 'items' are discarded. To mimic dict' update', the 
                passed 'items' values are added to 'contents' by the 'extend' 
                method which adds the values to the end of 'contents'.           
        
        """
        self.extend(list(items.values()))
        return

    def values(self) -> tuple[Any, ...]:
        """Emulates python dict 'values' method.
        
        Returns:
            tuple[Any]: an iterable equivalent to dict.values(). A Hybrid cannot
                actually create an ValuesView because that would eliminate any
                duplicate keys, which are permitted by Hybrid.
            
        """
        return tuple(self.contents)

    """ Dunder Methods """

    def __getitem__(self, key: Union[Hashable, int]) -> Any: # type: ignore
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored item at the
        corresponding index.
        
        If only one match is found, a single item is returned. If more are 
        found, a Hybrid or Hybrid subclass with the matching 'name' attributes 
        is returned.

        Args:
            key (Union[Hashable, int]): name of an item or index to search for 
                in 'contents'.

        Returns:
            Any: value(s) stored in 'contents' that correspond to 'key'. If 
                there is more than one match, the return is a Hybrid or Hybrid 
                subclass with that matching stored items.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [i for i, c in enumerate(self.contents)
                       if self._hashify(c) == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return matches
            
    def __setitem__(self, key: Union[Any, int], value: Any) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Any, int]): if key isn't an int, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.add(value)
        return

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[Any, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents 
                             if denovo.unit.get_name(c) != key]
        return

""" Generic dict """

@dataclasses.dataclass  # type: ignore
class Lexicon(Bunch, MutableMapping):  # type: ignore
    """Basic denovo dict replacement.
    
    A Lexicon differs from an ordinary python dict in ways inherited from Bunch 
    by requiring 'add' and 'subset' methods, storing data in 'contents', and 
    allowing the '+' operator to join Lexicons with other lists and Lexicons).
    In addition, it differs in 1 other significant way:
        1) When returning 'keys', 'values' and 'items', this class returns them
            as tuples instead of KeysView, ValuesView, and ItemsView.
    
    Args:
        contents (denovo.alias.Dictionary]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Any): default value to return when the 'get' method is 
            used. Defaults to None.
                          
    """
    contents: denovo.alias.Dictionary = dataclasses.field(
        default_factory = dict)
    default_factory: Any = None

    """ Class Methods """

    @classmethod
    def fromkeys(
        cls, 
        keys: Sequence[Hashable], 
        value: Any, 
        **kwargs: Any) -> Lexicon:
        """Emulates the 'fromkeys' class method from a python dict.

        Args:
            keys (Sequence[Hashable]): items to be keys in a new Lexicon.
            value (Any): the value to use for all values in a new Lexicon.

        Returns:
            Lexicon: formed from 'keys' and 'value'.
            
        """
        return cls(contents = dict.fromkeys(keys, value), **kwargs)
    
    """ Public Methods """
     
    def add(self, item: Mapping[Hashable, Any], **kwargs: Any) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Mapping[Hashable, Any]): items to add to 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.update(item, **kwargs)
        return

    def get(self, key: Hashable) -> Any: # type: ignore
        """Returns value in 'contents' or value in 'default_factory' attribute.
        
        Args:
            key (Hashable): key for value in 'contents'.
                
        Returns:
            Any: value matching key in 'contents' or 'default_factory' value. 
            
        """
        try:
            return[key]
        except (KeyError, TypeError):
            if self.default_factory is None:
                raise KeyError(f'{key} is not in {self.__class__}')
            else:
                try:
                    return self.default_factory()
                except TypeError:
                    return self.default_factory
                
    def items(self) -> tuple[tuple[Any, Any], ...]: # type: ignore
        """Emulates python dict 'items' method.
        
        Returns:
            tuple[tuple[Any, Any]: an iterable equivalent to dict.items(). A 
                Hybrid cannot actually create an ItemsView because that would 
                eliminate any duplicate keys, which are permitted by Hybrid.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> tuple(Any, ...): # type: ignore
        """Returns 'contents' keys as a tuple.
        
        Returns:
            tuple[Any]: an iterable equivalent to dict.keys(). A Hybrid cannot
                actually create an KeysView because that would eliminate any
                duplicate keys, which are permitted by Hybrid.
            
        """
        return tuple(self.contents.keys())

    def setdefault(self, value: Any) -> None: # type: ignore
        """sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self.default_factory = value 
        return
               
    def subset(
        self, 
        include: Union[Hashable, Sequence[Hashable]] = None, 
        exclude: Union[Hashable, Sequence[Hashable]] = None) -> Lexicon:
        """Returns a new instance with a subset of 'contents'.

        This method applies 'include' before 'exclude' if both are passed. If
        'include' is None, all existing keys will be added before 'exclude' is
        applied.
        
        Args:
            include (Union[Hashable, Sequence[Hashable]]): key(s) to include in 
                the new Lexicon instance.
            exclude (Union[Hashable, Sequence[Hashable]]): key(s) to exclude in 
                the new Lexicon instance.                
                
        Returns:
            Lexicon: with only keys from 'include' and no keys in 'exclude'.

        """
        if include is None and exclude is None:
            raise ValueError('include or exclude must not be None')
        else:
            if include is None:
                contents = self.contents
            else:
                include = list(more_itertools.always_iterable(include)) 
                contents = {k: self.contents[k] for k in include}
            if exclude is not None:
                exclude = list(more_itertools.always_iterable(exclude))
                contents = {k: v for k, v in contents.items() 
                            if k not in exclude}
            new_lexicon = copy.deepcopy(self)
            new_lexicon.contents = contents
        return new_lexicon
      
    def values(self) -> tuple[Any, ...]: # type: ignore
        """Returns 'contents' values as a tuple.
        
        Returns:
            tuple[Any]: an iterable equivalent to dict.values(). A Hybrid cannot
                actually create an ValuesView because that would eliminate any
                duplicate keys, which are permitted by Hybrid.
            
        """
        return tuple(self.contents.values())

    """ Dunder Methods """

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            key (Hashable): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return

    def __delitem__(self, key: Hashable) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return
    
""" dict that Accepts lists of Keys and Wildcards """

_ALL_KEYS: list[Any] = [
    'all', 'All', ['all'], ['All']]
_DEFAULT_KEYS: list[Any] = [
    'default', 'defaults', 'Default', 'Defaults', ['default'], ['defaults'], 
    ['Default'], ['Defaults']]
_NONE_KEYS: list[Any] = ['none', 'None', ['none'], ['None']]


@dataclasses.dataclass  # type: ignore
class Catalog(Lexicon):
    """Wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Lexicon and an ordinary python
    dict.

    A Catalog differs from a Lexicon in 5 significant ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'default' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'default' is not passed when the instance is initialized, the 
            initial value of 'default' is 'all'.
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching values 
            returned. For example, 'catalog[['first_key', 'second_key']]' will 
            return the values for those keys in a list ['first_value',
            'second_value'].
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single type will be returned.

    Args:
        contents (Mapping[Hashable, Any]]): stored dictionary. Defaults to an 
            empty dict.
        default_factory (Any): default value to return when the 'get' method is 
            used.
        default (Sequence[Any]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False.
                     
    """
    contents: denovo.alias.Dictionary = dataclasses.field(
        default_factory = dict)
    default_factory: Any = None
    default: Iterable[Any] = 'all'
    always_return_list: bool = False

    """ Dunder Methods """

    def __getitem__(
        self, 
        key: Union[Hashable, Sequence[Hashable]]) -> Union[Any, Sequence[Any]]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[Hashable, Sequence[Hashable]]): key(s) in 'contents'.

        Returns:
            Union[Any, Sequence[Any]]: value(s) stored in 'contents'.

        """
        # Returns a list of all values if the 'all' key is sought.
        if key in _ALL_KEYS:
            return list(self.contents.values())
        # Returns a list of values for keys listed in 'default' attribute.
        elif key in _DEFAULT_KEYS:
            try:
                return[self.default]
            except KeyError:
                matches = {k: self.contents[k] for k in self.default}
                return list(matches.values())
        # Returns an empty list if a null value is sought.
        elif key in _NONE_KEYS:
            return []
        # Returns list of matching values if 'key' is list-like.        
        elif isinstance(key, Sequence) and not isinstance(key, str):
            return [self.contents[k] for k in key if k in self.contents]
        # Returns matching value if key is not a non-str Sequence or wildcard.
        else:
            try:
                if self.always_return_list:
                    return [self.contents[key]]
                else:
                    return self.contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(
        self, 
        key: Union[Hashable, Sequence[Hashable]], 
        value: Union[Any, Iterable[Any]]) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Hashable, Sequence[Hashable]]): key(s) to set in 
                'contents'.
            value (Union[Any, Iterable[Any]]): value(s) to be paired with 'key' 
                in 'contents'.

        """
        if key in _DEFAULT_KEYS:
            self.default = more_itertools.always_iterable(value)
        else:
            try:
                self.contents[key] = value
            except TypeError:
                self.contents.update(dict(zip(key, value))) # type: ignore
        return

    def __delitem__(self, key: Union[Hashable, Sequence[Hashable]]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[Hashable, Sequence[Hashable]]): name(s) of key(s) in 
                'contents' to delete the key/value pair.

        """
        self.contents = {i: self.contents[i] for i in self.contents 
                         if i not in more_itertools.always_iterable(key)}
        return

""" Dual dict for Storing Subclasses and Instances """

@dataclasses.dataclass  # type: ignore
class Library(Lexicon):
    """Stores classes and class instances.
    
    When searching for matches, instances are prioritized over classes.
    
    Args:
        classes (Catalog): a catalog of stored classes. Defaults to any empty
            Catalog.
        instances (Catalog): a catalog of stored class instances. Defaults to an
            empty Catalog.
        kinds (MutableMapping[str, set[str]]): a defaultdict with keys
            that are the different kinds of stored items and values which are
            sets of names of items that are of that kind. Defaults to an empty
            defaultdict which autovivifies sets as values.
            
    """
    classes: Catalog = Catalog()
    instances: Catalog = Catalog()
    kinds: MutableMapping[str, set[str]] = dataclasses.field(
        default_factory = lambda: collections.defaultdict(set))

    """ Public Methods """
    
    def classify(self, item: Union[str, object, Type[Any]]) -> tuple[str, ...]:
        """Returns kind or kinds of 'item' based on 'kinds.'
        
        Args:
            item (Union[str, object, Type]): name of object or Type or an object
                or Type to be classified.
                
        Returns:
            tuple[str]: kinds of which 'item' is part of.
 
        """
        if not isinstance(item, str):
            item = denovo.unit.get_name(item = item)
        kinds = []  
        for kind, classes in self.kinds.items():  
            if item in classes:
                kinds.append(kind)
        return tuple(kinds)
       
    def deposit(
        self, 
        item: Union[Type[Any], object],
        kind: Optional[Union[str, Sequence[str]]] = None) -> None:
        """Adds 'item' to 'classes' and, possibly, 'instances'.

        If 'item' is a class, it is added to 'classes.' If it is an object, it
        is added to 'instances' and its class is added to 'classes'.
        
        Args:
            item (Union[Type, object]): class or instance to add to the Library
                instance.
            kind (Union[str, Sequence[str]]): kind(s) to add 'item'
                to. Defaults to None.
                
        """
        key = denovo.unit.get_name(item = item)
        base_key = None
        if inspect.isclass(item):
            self.classes[key] = item
        elif isinstance(item, object):
            self.instances[key] = item
            base = item.__class__
            base_key = denovo.unit.get_name(item = base)
            self.classes[base_key] = base
        else:
            raise TypeError(f'item must be a class or a class instance')
        if kind is not None:
            for classification in more_itertools.always_iterable(kind):
                self.kinds[classification].add(key)
                if base_key is not None:
                    self.kinds[classification].add(base_key)
        return
    
    def remove(self, name: str) -> None:
        """Removes an item from 'instances' or 'classes.'
        
        If 'name' is found in 'instances', it will not also be removed from 
        'classes'.

        Args:
            name (str): key name of item to remove.
            
        Raises:
            KeyError: if 'name' is neither found in 'instances' or 'classes'.

        """
        try:
            del self.instances[name]
        except KeyError:
            try:
                del self.classes[name]
            except KeyError:
                raise KeyError(f'{name} is not found in the library')
        return    

    def withdraw(
        self, 
        name: Union[str, Sequence[str]], 
        kwargs: Optional[denovo.alias.Dictionary] = None) -> (
            Union[Type[Any], object]):
        """Returns instance or class of first match of 'name' from catalogs.
        
        The method prioritizes the 'instances' catalog over 'classes' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): key name(s) of stored item(s) 
                sought.
            kwargs (Mapping[Hashable, Any]): keyword arguments to pass to a
                newly created instance or, if the stored item is already an
                instance to be manually added as attributes.
            
        Raises:
            KeyError: if 'name' does not match a key to a stored item in either
                'instances' or 'classes'.
            
        Returns:
            Union[Type, object]: returns a class is 'kwargs' are None. 
                Otherwise, and object is returned.
            
        """
        names = denovo.convert.listify(name)
        item = None
        for key in names:
            for catalog in ['instances', 'classes']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {name} was found')
        if kwargs is not None:
            if 'name' in item.__annotations__.keys() and 'name' not in kwargs:
                kwargs[name] = names[0]
            if inspect.isclass(item):
                item = item(**kwargs)
            else:
                for key, value in kwargs.items():
                    setattr(item, key, value)  
        return item # type: ignore
