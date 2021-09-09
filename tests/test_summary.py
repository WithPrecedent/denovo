"""
test_recap: tests function in denovo.recap
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
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

def test_beautify():
    dummy = TestClass(a_dict = {'tree': 'house', 'window': 'pane'},
                      a_list = ['car', 'road', 'lawn'])
    recap = denovo.recap.beautify(item = dummy, package = 'denovo')
    return

if __name__ == '__main__':
    testables = denovo.test.get_testables(module = denovo.recap)
    denovo.test.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   