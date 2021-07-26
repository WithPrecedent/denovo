"""
test_structures: unit tests for denovo structures
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""


import denovo


@attr.s
class Something(denovo.structures.Node):
    
    pass


@attr.s
class AnotherThing(denovo.structures.Node):
    
    pass


@attr.s
class EvenAnother(denovo.structures.Node):
    
    pass



if __name__ == '__main__':
    denovo.testing.testify(target_module = denovo.structures, 
                           testing_module = __name__)
    
