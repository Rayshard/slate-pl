from typing import Dict, List, Optional

from slasm.function import Function

class Program:
    def __init__(self, target: str) -> None:
        self.__target = target
        self.__functions : Dict[str, Function] = {}
        self.__entry : Optional[str] = None

    def add_function(self, function: Function) -> None:
        if function.name in self.__functions:
            raise Exception(f"Function with name {function.name} already exists!")

        self.__functions[function.name] = function

    def contains_nonterminated_basic_block(self) -> bool:
        return any([func.contains_nonterminated_basic_block() for func in self.__functions.values()])

    @property
    def target(self) -> str:
        return self.__target

    @property
    def functions(self) -> List[Function]:
        return list(self.__functions.values())

    @property
    def entry(self) -> str:
        if self.__entry is None:
            raise Exception("Program's entry has not been set!")

        return self.__entry

    @entry.setter
    def entry(self, func_name: str) -> None:
        if func_name not in self.__functions:
            raise Exception(f"Function with name {func_name} does not exist!")

        self.__entry = func_name