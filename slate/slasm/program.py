from typing import Dict, List, Optional, Set, Tuple

from slate.slasm.function import Function
from slate.slasm.slasm import Word

class Program:
    def __init__(self, target: str, globals: Set[str]) -> None:
        self.__target = target
        self.__data : Dict[str, bytes] = {}
        self.__globals = set(globals)
        self.__functions : Dict[str, Function] = {}
        self.__entry : Optional[str] = None

    def add_function(self, function: Function) -> None:
        if function.name in self.__functions:
            raise Exception(f"Function with name {function.name} already exists!")

        self.__functions[function.name] = function

    def add_data(self, label: str, data: bytes) -> None:
        if label in self.__data:
            raise Exception(f"Data with label {label} already exists!")

        size = len(data)
        padding = (Word.SIZE() - size % Word.SIZE()) % Word.SIZE()

        self.__data[label] = data + bytes([0] * padding)

    def contains_nonterminated_basic_block(self) -> bool:
        return any([func.contains_nonterminated_basic_block() for func in self.__functions.values()])

    @property
    def target(self) -> str:
        return self.__target

    @property
    def num_globals(self) -> int:
        return len(self.__globals)

    @property
    def functions(self) -> List[Function]:
        return list(self.__functions.values())

    @property
    def globals(self) -> Set[str]:
        return set(self.__globals)

    @property
    def data(self) -> List[Tuple[str, bytes]]:
        return list(self.__data.items())

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