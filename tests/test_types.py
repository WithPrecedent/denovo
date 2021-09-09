"""
test_types: tests denovo typing system
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import sys

import denovo
from denovo.typing.types import *

    

def test_composite():
    return

if __name__ == '__main__':
    testables = denovo.test.get_testables(module = denovo.types)
    denovo.test.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   