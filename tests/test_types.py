"""
test_types: tests denovo typing system
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import dataclasses
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo
from denovo.core.types import *


@dataclasses.dataclass
class NewString(denovo.types.String):
    pass
    

def test_kind():
    assert 'default_dictionary' in kinds
    a_string = 'blah'
    assert isinstance(a_string, String)
    a_dict = {a_string: 'something'}
    assert isinstance(a_dict, Dictionary)
    
    
    new_string = NewString()
    return

if __name__ == '__main__':
    testables = denovo.testing.get_testables(module = denovo.types)
    denovo.testing.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   