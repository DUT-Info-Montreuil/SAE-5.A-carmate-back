# Code style
PEP guide: https://peps.python.org/pep-0008/
## Sommaire :
- [Import](#import)
- [Classe](#classe)
- [Fonction](#fonction)
- [Condition](#condition)

## Import
```python
import os
import json

from datetime import datetime
from typing import List

from src.something import MyClazz
from src.many_import import (
    a,
    b,
    c,
    d,
    e,
    f
)
from tests import A
from tests.b import B
```

## Classe
```python


@something
class MyClazz:
    """hello world"""
    var: str = "something"

    def __init__(self) -> None:
        pass

    def foo(self,
            too: str,
            much: int,
            args: int,
            here: List[float],
            sorry: str = None) -> float:
        """he make something

        :param too: beautiful args
        :param much: beautiful args
        :param args: beautiful args
        :param here: beautiful args
        :param sorry: beautiful args
        
        :return float: math.pi
        :raise:
            Exception: incredible 
        """
        pass


class MyClazzHeritance(object):
    """hello world"""
    var: str = "something"

    def __init__(self) -> None:
        super().__init__()


```

## Fonction
```python


@something
def func_foo(args1: List[str],
             args2: Tuple[int, int, int]) -> None:
    """he make something

    :param args: beautiful args
    :param args2: other beautiful args
    
    :return None: nothing
    :raise:
        Exception: incredible 
    """
    pass


def func_foo2() -> Tuple[int,
                         float,
                         int,
                         str,
                         Tuple[int, int, int], 
                         List[Tuple[int, int, int]]]:
    pass


```

## Condition
```python
if val == 'val' \
        and other_val == 'val' \
        or wrong_val == 'val':
    print('i d\'ont know')
```
