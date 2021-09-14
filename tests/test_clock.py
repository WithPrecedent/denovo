"""
test_clock: tests functions and classes related to date and time
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

ToDo:
    
"""

import denovo

def test_how_soon_is_now() -> None:
    current_datetime = denovo.tools.how_soon_is_now()
    assert isinstance(current_datetime, str)
    return

if __name__ == '__main__':
    denovo.test.testify(target_module = denovo.clock, testing_module = __name__)
   