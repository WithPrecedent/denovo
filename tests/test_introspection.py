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
    a_folder = pathlib.Path('.') / 'tests' / 'test_folder'
    a_file = pathlib.Path(a_folder) / 'dummy_module.py'
    assert denovo.check.is_folder(folder = a_folder)
    assert denovo.check.is_file(file_path = a_file)
    assert denovo.check.name_modules(folder = a_folder) == ['dummy_module']
    all_modules = denovo.check.get_modules(folder = a_folder)
    a_module = all_modules[0]
    assert type(a_module) == types.ModuleType
    assert a_module.__name__ == 'dummy_module'
    class_names = denovo.check.name_classes(module = a_module)
    assert class_names == ['TestClass', 'TestDataclass']
    function_names = denovo.check.name_functions(module = a_module)
    assert function_names == ['a_function']
    classes = denovo.check.get_classes(module = a_module)
    assert inspect.isclass(classes[0])
    functions = denovo.check.get_functions(module = a_module)
    assert type(functions[0]) == types.FunctionType
    a_class = TestClass()
    a_dataclass = TestDataclass()
    assert denovo.check.is_classvar(item = a_class, attribute = 'a_classvar')
    assert denovo.check.is_classvar(item = a_dataclass, 
                                     attribute = 'a_classvar')   
    assert not denovo.check.is_classvar(item = a_class, attribute = 'a_dict')
    assert not denovo.check.is_classvar(item = a_dataclass, 
                                         attribute = 'a_dict')    
    assert denovo.check.is_method(item = a_class, attribute = 'do_something')
    assert denovo.check.is_method(item = a_dataclass, 
                                   attribute = 'do_something')
    assert denovo.check.is_property(item = a_class, 
                                     attribute = 'get_something')
    assert denovo.check.is_property(item = a_dataclass, 
                                     attribute = 'get_something')
    properties = denovo.check.get_properties(item = a_class)
    assert isinstance(properties[0], property)
    methods = denovo.check.get_methods(item = a_dataclass) 
    assert isinstance(methods[0], types.MethodType)
    return

if __name__ == '__main__':
    testables = denovo.test.get_testables(module = denovo.tools)
    denovo.test.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   