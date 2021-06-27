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
    test_filing
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

if __name__ == '__main__':
    test_version()
    folder = pathlib.Path('.')
    testimony = denovo.testing.Testimony(folder = folder)
    testimony.testify()
    