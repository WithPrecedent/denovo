"""
test_tools: tests function in denovo.tools
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

ToDo:
    Add tests for the remaining functions in tools.
    
"""
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, Mapping, 
                    MutableMapping, MutableSequence, Optional, Sequence, Type, 
                    Union)

import denovo


@dataclasses.dataclass
class TestClass(object):
    
    a_dict: Dict = dataclasses.field(default_factory = dict)
    a_list: Dict = dataclasses.field(default_factory = list)
    a_none: None = None     


def test_how_soon_is_now():
    current_datetime = denovo.tools.how_soon_is_now()
    assert isinstance(current_datetime, str)
    return

def test_instancify():
    an_instance = TestClass()
    result = denovo.tools.instancify(item = TestClass, a_list = ['a'])
    assert result.a_list == ['a']
    result = denovo.tools.instancify(item = an_instance, a_list = ['a'])
    assert result.a_list == ['a']
    return

def test_listify():
    some_list = ['a', 'b', 'c']
    another_list = ['d']
    a_string = 'tree'
    an_int = 4
    result = denovo.tools.listify(item = some_list)
    assert result == ['a', 'b', 'c']
    result = denovo.tools.listify(item = another_list)
    assert result == ['d']
    result = denovo.tools.listify(item = a_string)
    assert result == ['tree']
    result = denovo.tools.listify(item = an_int)
    assert result == [4]
    return

def test_namify():
    an_instance = TestClass()
    result = denovo.tools.namify(item = an_instance)
    assert result == 'test_class'
    an_instance.name = 'huh'
    result = denovo.tools.namify(item = an_instance)
    assert result == 'huh'
    return

def test_numify():
    a_string = '5'
    an_int = 4
    another_string = 'tree'
    result = denovo.tools.numify(item = a_string)
    assert result == 5
    result = denovo.tools.numify(item = an_int)
    assert result == 4
    result = denovo.tools.numify(item = another_string)
    assert result == 'tree'
    return

if __name__ == '__main__':
    testables = denovo.testing.get_testables(module = denovo.tools)
    denovo.testing.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   