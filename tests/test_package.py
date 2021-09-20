"""
test_tools: tests function in denovo.tools
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

ToDo:
    Add tests for the remaining functions in tools.
    
"""
import inspect
import pathlib
import sys
import types

import denovo

    
def test_all() -> None:
    a_folder = pathlib.Path('.') / 'tests' / 'test_folder'
    a_file = pathlib.Path(a_folder) / 'dummy_module.py'
    assert denovo.package.is_folder(item = a_folder)
    assert denovo.package.is_file(file_path = a_file)
    assert denovo.package.name_modules(item = a_folder) == ['dummy_module']
    all_modules = denovo.package.get_modules(item = a_folder)
    a_module = all_modules[0]
    assert type(a_module) == types.ModuleType
    assert a_module.__name__ == 'dummy_module'
    class_names = denovo.package.name_classes(item = a_module)
    assert class_names == ['TestClass', 'TestDataclass']
    function_names = denovo.package.name_functions(item = a_module)
    assert function_names == ['a_function']
    classes = denovo.package.get_classes(item = a_module)
    assert inspect.isclass(classes[0])
    functions = denovo.package.get_functions(item = a_module)
    assert type(functions[0]) == types.FunctionType
    return

if __name__ == '__main__':
    testables = denovo.test.get_testables(module = denovo.package)
    denovo.test.run_tests(testables = testables, module = sys.modules[__name__])
   