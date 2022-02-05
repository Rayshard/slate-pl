from typing import Dict, List, Optional

from slasm.function import Function

class Program:
    def __init__(self, target: str) -> None:
        self.__target = target
        self.__functions : Dict[str, Function] = {}
        self.__entry : Optional[str] = None

    @property
    def target(self) -> str:
        return self.__target

    @property
    def functions(self) -> List[Function]:
        return list(self.__functions.values())

    @property
    def entry(self) -> str:
        assert self.__entry is not None
        return self.__entry

    @entry.setter
    def entry(self, func_name: str) -> None:
        assert self.__entry is None and func_name in self.__functions
        self.__entry = func_name

    def add_function(self, function: Function, is_entry: bool = False) -> None:
        assert function.name not in self.__functions
        self.__functions[function.name] = function