"""
test_tools: tests function in denovo.tools
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

ToDo:
    Add tests for the remaining functions in tools.
    
"""
import dataclasses
import inspect
import pathlib
import sys
import types
from typing import Any, ClassVar, Union

import denovo


@dataclasses.dataclass
class TestDataclass(object):
    
    a_dict: dict[Any, Any] = dataclasses.field(default_factory = dict)
    a_list: list[Any] = dataclasses.field(default_factory = list)
    a_classvar: ClassVar[Any] = None     

    @property
    def get_something(self) -> str:
        return 'something'
    
    def do_something(self) -> None:
        return
    
class TestClass(object):
    
    a_classvar: str = 'tree'
    
    def __init__(self) -> None:
        a_dict = {'tree': 'house'}

    @property
    def get_something(self) -> str:
        return 'something'
    
    def do_something(self) -> None:
        return
    
def test_all() -> None:
    a_class = TestClass()
    a_dataclass = TestDataclass()
    assert denovo.unit.is_classvar(item = a_class, attribute = 'a_classvar')
    assert denovo.unit.is_classvar(
        item = a_dataclass, 
        attribute = 'a_classvar')   
    assert not denovo.unit.is_classvar(item = a_class, attribute = 'a_dict')
    assert not denovo.unit.is_classvar(
        item = a_dataclass, 
        attribute = 'a_dict')    
    assert denovo.unit.is_method(item = a_class, attribute = 'do_something')
    assert denovo.unit.is_method(
        item = a_dataclass, 
        attribute = 'do_something')
    assert denovo.unit.is_property(
        item = a_class, 
        attribute = 'get_something')
    assert denovo.unit.is_property(
        item = a_dataclass, 
        attribute = 'get_something')
    properties = denovo.unit.get_properties(item = a_class)
    assert isinstance(properties[0], property)
    methods = denovo.unit.get_methods(item = a_dataclass) 
    assert isinstance(methods[0], types.MethodType)
    return

if __name__ == '__main__':
    denovo.test.testify(target_module = denovo.unit, testing_module = __name__)
   