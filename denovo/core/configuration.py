"""
configuration: easy, flexible tool for user configuraton settings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings (Lexicon): stores configuration settings after either loading 
        them from disk or by the passed arguments.    
         
"""
from __future__ import annotations
import configparser
import dataclasses
import importlib
import importlib.util
import json
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import denovo


TwoLevel: Type = MutableMapping[Hashable, MutableMapping[Hashable, Any]]


@dataclasses.dataclass
class Settings(denovo.Lexicon):
    """Loads and stores configuration settings.

    To create Settings instance, a user can pass a:
        1) file path to a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, Settings creates a dict and can 
    convert the dict values to appropriate datatypes. Currently, supported file 
    types are: ini, json, toml, and python.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported). Type conversion is automatically disabled
    if the source file is a python module (assuming the user has properly set
    the types of the stored python dict).

    Because Settings uses ConfigParser for .ini files, by default it stores 
    a 2-level dict. The desire for accessibility and simplicity denovoted this 
    limitation. A greater number of levels can be achieved by having separate
    sections with names corresponding to the strings in the values of items in 
    other sections. This is implemented in the 'project' subpackage.

    Args:
        contents (TwoLevel): a two-level nested dict for
            storing configuration options. Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        standard (Mapping[str, Mapping[str]]): any standard options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.

    """
    contents: TwoLevel = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = dict)
    standard: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Infers types for values in 'contents', if the 'infer_types' option is 
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._add_standard(contents = self.contents)

    """ Class Methods """

    @classmethod
    def create(cls, **kwargs) -> Settings:
        """Calls corresponding creation class method to instance a subclass.

        Raises:
            TypeError: If there is no corresponding method.

        Returns:
            Needy: instance of a Needy subclass.
            
        """
        if 'file_path' in kwargs:
            return cls.from_file_path(**kwargs)
        elif 'dictionary' in kwargs:
            if (isinstance(kwargs['dictionary'], Mapping) 
                    and all(isinstance(v, Mapping) 
                            for v in kwargs['dictionary'].values())):
                return cls.from_dictionary(**kwargs)
            else:
                raise TypeError(f'dictionary must be nested dict type')
        else:
            raise TypeError(
                f'create method requires a str, pathlib.Path, or dict type')   

    @classmethod
    def from_dictionary(cls, 
        dictionary: Mapping[str, Mapping[str, Any]], 
        **kwargs) -> Settings:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            Settings: [description]
            
        """        
        return cls(contents = dictionary, **kwargs)
    
    @classmethod
    def from_file_path(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Settings:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            Settings: [description]
            
        """        
        extension = str(pathlib.Path(file_path).suffix)[1:]
        load_method = getattr(cls, f'from_{extension}')
        return load_method(file_path = file_path, **kwargs)
    
    @classmethod
    def from_ini(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Settings:
        """Returns settings dictionary from an .ini file.

        Args:
            file_path (str): path to configparser-compatible .ini file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(str(file_path))
            return cls(contents = dict(contents._sections), **kwargs)
        except (KeyError, FileNotFoundError):
            raise FileNotFoundError(f'settings file {file_path} not found')

    @classmethod
    def from_json(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Settings:
        """Returns settings dictionary from an .json file.

        Args:
            file_path (str): path to configparser-compatible .json file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            with open(pathlib.Path(file_path)) as settings_file:
                contents = json.load(settings_file)
            return cls(contents = contents, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    @classmethod
    def from_py(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Settings:
        """Returns a settings dictionary from a .py file.

        Args:
            file_path (str): path to python module with '__dict__' dict
                defined.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a
                file.

        """
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = False
        try:
            file_path = pathlib.Path(file_path)
            import_path = importlib.util.spec_from_file_location(
                file_path.name,
                file_path)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            return cls(contents = import_module.configuration, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    @classmethod
    def from_toml(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Settings:
        """Returns settings dictionary from a .toml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        import toml
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            return cls(contents = toml.load(file_path), **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')
   
    @classmethod
    def from_yaml(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Settings:
        """Returns settings dictionary from a .yaml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        import yaml
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = False
        try:
            with open(file_path, 'r') as config:
                return cls(contents = yaml.safe_load(config, **kwargs))
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')
        
    """ Public Methods """

    def add(self, section: str, contents: Mapping[str, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Mapping[str, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(contents)
        except KeyError:
            self[section] = contents
        return self

    def inject(self, 
               instance: object,
               additional: Union[Sequence[str], str] = None, 
               overwrite: bool = False) -> object:
        """Injects appropriate items into 'instance' from 'contents'.

        Args:
            instance (object): denovo class instance to be modified.
            additional (Union[Sequence[str], str]]): other section(s) in 
                'contents' to inject into 'instance'. Defaults to None.
            overwrite (bool]): whether to overwrite a local attribute in 
                'instance' if there are values stored in that attribute. 
                Defaults to False.

        Returns:
            instance (object): denovo class instance with modifications made.

        """
        sections = ['general']
        try:
            sections.append(instance.name)
        except AttributeError:
            pass
        if additional:
            sections.extend(more_itertools.always_iterable(additional))
        for section in sections:
            try:
                for key, value in self.contents[section].items():
                    if (not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
            except KeyError:
                pass
        return instance

    """ Private Methods """

    def _infer_types(self,
        contents: Mapping[str, Mapping[str, Any]]) -> Mapping[
            str, Mapping[str, Any]]:
        """Converts stored values to appropriate datatypes.

        Args:
            contents (Mapping[str, Mapping[str, Any]]): a nested contents dict
                to review.

        Returns:
            Mapping[str, Mapping[str, Any]]: with the nested values converted to 
                the appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: denovo.tools.typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = denovo.tools.typify(value)
        return new_contents

    def _add_standard(self, 
        contents: Mapping[str, Mapping[str, Any]]) -> (
            Mapping[str, Mapping[str, Any]]):
        """Creates a backup set of mappings for denovo settings lookup.


        Args:
            contents (MutableMapping[Any, Mapping[Any, Any]]): a nested contents 
                dict to add standard to.

        Returns:
            Mapping[Any, Mapping[Any, Any]]: with stored standard added.

        """
        new_contents = self.standard
        new_contents.update(contents)
        return new_contents

    """ Dunder Methods """

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (Mapping[str, Any]): the dictionary to be placed in that 
                section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return self
