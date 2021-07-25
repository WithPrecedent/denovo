"""
test_converters: tests denovo typing system
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import collections.abc
import pathlib
import sys

import denovo
from denovo.typing.types import *


def test_to_adjacency():
    adjacency = {'node': {'another_node'},
                 'another_node': {'some_node'},
                 'some_node': set()}
    converted = denovo.converters.to_adjacency(adjacency)
    assert converted == {'node': {'another_node'},
                         'another_node': {'some_node'},
                         'some_node': set()}
    matrix = tuple([[[0, 1], [1,0]], ['tree', 'house']])
    print('test matrix', matrix)
    print('test registry', denovo.converters.to_adjacency.registry.keys())
    print('test string registry', denovo.converters.to_string.registry.keys())
    assert isinstance(matrix, denovo.types.Matrix)
    converted = denovo.converters.to_adjacency(matrix)
    return

def test_to_string():
    print('testing to_string')
    listing = ['stuff', 'more_stuff', 'even_more']
    converted = denovo.converters.to_string(listing)
    assert converted == 'stuff, more_stuff, even_more'
    return

if __name__ == '__main__':
    print('testing')
    testables = denovo.testing.get_testables(module = denovo.converters)
    print('testing testables', testables)
    denovo.testing.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   