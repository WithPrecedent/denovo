"""
test_denovo: executes all denovo tests
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import logging
import pathlib
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


def test_version() -> None:
    assert denovo.__version__ == '0.1.0'
    return
    
def test_all(folder: Union[str, pathlib.Path] = None) -> None:
    test_version()
    current_folder = folder or pathlib.Path('.')
    testers = list(current_folder.glob('*/*.py'))
    testers = [f for f in testers if f.name.startswith('test_')]
    testers = [f for f in testers if f.name != f'test_{denovo.__package__}.py']
    for tester in testers:
        name = tester.stem
        module_to_test = denovo.tools.drop_prefix(item = name, prefix = 'test_')
        module_to_test = getattr(denovo, module_to_test)
        imported = denovo.lazy.from_path(name = name, file_path = tester)
        denovo.testing.testify(module_to_test = module_to_test,
                               testing_module = imported)
    return

if __name__ == '__main__':
    test_all()