"""
test_denovo: executes all denovo tests
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

ToDo:
    Add testing logger
    test_quirks
    test_configuration
    test_framework (or eliminate framework module)
    test_storage
    test_decorators
    test_lazy (beyond testing built into denovo)
    test_memory
    
"""
import logging
import pathlib
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


# """ Sets Testing Logger """

# LOGGER = logging.getLogger(denovo.__package__)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.WARNING)
# LOGGER.addHandler(console_handler)
# file_handler = logging.FileHandler(f'{denovo.__package__}_testing.log')
# file_handler.setLevel(logging.DEBUG)
# LOGGER.addHandler(file_handler)
# LOGGER.info(f'{denovo.__package__} version is: {denovo.__version__}')

""" Testing Functions """

def test_version() -> None:
    assert denovo.__version__ == '0.1.0'
    return
    
def test_all(folder: Union[str, pathlib.Path] = None) -> None:
    test_version()
    folder = folder or pathlib.Path('.')
    python_modules = list(folder.glob('*/*.py'))
    testers = [f for f in python_modules if f.name.startswith('test_')]
    testers = [f for f in testers if f.name != f'test_{denovo.__package__}.py']
    for tester in testers:
        name = tester.stem
        module_name = denovo.tools.drop_prefix(item = name, prefix = 'test_')
        module_to_test = getattr(denovo, module_name)
        imported = denovo.lazy.from_path(name = name, file_path = tester)
        denovo.testing.testify(module_to_test = module_to_test,
                               testing_module = imported)
    return

if __name__ == '__main__':
    test_all()