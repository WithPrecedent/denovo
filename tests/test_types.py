"""
test_types: tests denovo typing system
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import collections.abc
import dataclasses
import pathlib
import sys

import denovo
from denovo.typing.types import *


@dataclasses.dataclass
class NewString(denovo.types.String):
    pass
    

def test_kind():
    assert 'dictionary' in denovo.types.catalog
    a_string = 'blah'
    assert isinstance(a_string, String)
    a_dict = {a_string: 'something'}
    assert isinstance(a_dict, Dictionary)
    a_dyad = [['a', 'b', 'c'], ['d', 'e', 'f']]
    assert isinstance(a_dyad, Dyad)
    an_int = 4
    assert isinstance(an_int, Integer)
    assert not isinstance(an_int, Real)
    a_real = 3.14
    assert isinstance(a_real, Real)
    # a_default = collections.defaultdict(None, {'tree': 'house'})
    # assert isinstance(a_default, DefaultDictionary)
    a_listing = ['abc', '123']
    assert isinstance(a_listing, Listing)
    a_disk = pathlib.Path('.')
    assert isinstance(a_disk, Path)
    an_index = tuple(['for', 'four'])
    assert isinstance(an_index, Index)
    new_string = NewString()
    assert new_string.comparison == str
    an_adjacency = {'a_node': {'another_node', 'ya_node'},
                    'another_node': set(),
                    'ya_node': set()}
    assert isinstance(an_adjacency, Adjacency)
    return

if __name__ == '__main__':
    testables = denovo.testing.get_testables(module = denovo.types)
    denovo.testing.run_tests(testables = testables, 
                             module = sys.modules[__name__])
   