# Code style
PEP guide: https://peps.python.org/pep-0008/
## Import
```python
import os
import json

from datetime import datetime
from typing import List

from src.something import MyClazz
```
## Classe
```python
@something
class MyClazz(object):
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
```
## Fonction
```python
@something
def func_foo(args: List[str]) -> None:
    """he make something

    :param args: beautiful args
    
    :return None: nothing
    :raise:
        Exception: incredible 
    """
    pass
```