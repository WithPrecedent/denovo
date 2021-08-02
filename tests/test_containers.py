"""
test_containers: tests classes in denovo.containers
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

ToDo:
    test_catalog: complete tests
    test_proxy
    test_library
    
"""
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, Mapping, 
                    MutableMapping, MutableSequence, Optional, Sequence, Type, 
                    Union)

import denovo


@dataclasses.dataclass
class TestClass(object):
    
    name: str = 'something'

def test_manifest():
    manifest = denovo.Manifest(contents = ['a', 'b', 'c'])
    assert manifest[1] == 'b'
    manifest.add(item = 'd')
    assert manifest[3] == 'd'
    manifest.insert(2, 'zebra')
    assert manifest[2] == 'zebra'
    manifest.append('e')
    assert manifest[5] == 'e'
    manifest.extend(['f', 'g'])
    assert manifest[7] == 'g'
    sub_manifest = manifest.subset(include = ['a', 'b', 'c', 'd', 'zebra'],
                                   exclude = 'd')
    assert sub_manifest.contents == ['a', 'b', 'zebra', 'c']
    sub_manifest.remove('c')
    assert sub_manifest.contents == ['a', 'b', 'zebra']
    manifest.clear()
    return

def test_hybrid():
    hybrid = denovo.Hybrid(contents = ['a', 'b', 'c'], default_factory = 'No')
    assert hybrid[1] == 'b'
    hybrid.add(item = 'd')
    assert hybrid[3] == 'd'
    hybrid.insert(2, 'zebra')
    assert hybrid[2] == 'zebra'
    sub_hybrid = hybrid.subset(include = ['a', 'b', 'c', 'd', 'zebra'],
                               exclude = 'd')
    assert sub_hybrid.contents == ['a', 'b', 'zebra', 'c']
    sub_hybrid.remove('c')
    assert sub_hybrid.contents == ['a', 'b', 'zebra']
    assert hybrid[0] == 'a'
    assert hybrid['zebra'] == 2
    assert hybrid.get('tree') == 'No'
    hybrid.append('b')
    assert hybrid['b'] == [1, 5]
    assert hybrid.values() == tuple(['a', 'b', 'zebra', 'c', 'd', 'b'])
    assert hybrid.keys() == tuple(['a', 'b', 'zebra', 'c', 'd', 'b'])
    hybrid.remove('b')
    assert hybrid.contents == ['a', 'zebra', 'c', 'd', 'b']
    hybrid.clear()
    test_class = TestClass()
    hybrid.add(test_class)
    assert hybrid.keys() == tuple(['something'])
    assert hybrid.values() == tuple([test_class])
    return

def test_lexicon():
    alt_created = denovo.Lexicon.fromkeys(keys = ['a', 'b', 'c'], 
                                          value = 'tree')
    assert alt_created['a'] == 'tree'
    lexicon = denovo.Lexicon(contents = {'a': 'b', 'c': 'd'}, 
                             default_factory = 'Nada')
    assert lexicon.get('f') == 'Nada'
    assert lexicon['a'] == 'b'
    lexicon.add({'e': 'f'})
    assert lexicon['e'] == 'f'
    subset = lexicon.subset(include = ['a', 'e'])
    assert subset.keys() == tuple(['a', 'e'])
    assert subset.values() == tuple(['b', 'f'])
    return

def test_catalog():
    catalog = denovo.Catalog()
    return
 
if __name__ == '__main__':
    denovo.testing.testify(target_module = denovo.containers, 
                           testing_module = __name__)
   