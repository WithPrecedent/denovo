"""
test_tools: tests function in denovo.tools
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


def test_how_soon_is_now():
    print('testing how soon is now')
    current_datetime = denovo.tools.how_soon_is_now()
    assert isinstance(current_datetime, str)
    return

if __name__ == '__main__':
    testables = denovo.testing.get_testables(module = denovo.tools)
    denovo.testing.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   