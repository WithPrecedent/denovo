"""
alias: denovo type aliases
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Operation: generic, flexible Callable type alias.
    Signatures: dict of Signatures type.
    Wrappable: type for an item that can be wrapped by a decorator.
    
"""
from __future__ import annotations
from collections.abc import MutableMapping

import inspect
from typing import Any, Callable, Type, Union


""" Type Aliases """

Operation = Callable[..., Any]
Signatures = MutableMapping[str, inspect.Signature]
Wrappable = Union[object, Type[Any], Operation]
