"""
test_quirks: tests function in denovo.quirks
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import dataclasses
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, Mapping, 
                    MutableMapping, MutableSequence, Optional, Sequence, Type, 
                    Union)

import denovo


@dataclasses.dataclass
class Bases(denovo.quirks.Importer):
    
    clerk: Union[str, Type] = denovo.filing.Clerk
    library: Union[str, Type] = 'denovo.containers.Library'
    settings: Union[str, Type] = 'denovo.configuration.settings'
    

def test_importer():
    bases = Bases()
    library = bases.library()
    assert isinstance(library, denovo.containers.Library)
    clerk = bases.clerk()
    assert isinstance(clerk, denovo.filing.Clerk)
    return

if __name__ == '__main__':
    testables = denovo.testing.get_testables(module = denovo.quirks)
    denovo.testing.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   