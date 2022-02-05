from typing import List, Set, Union

from slasm.instruction import Instruction, Label


class Function:
    def __init__(self, name: str, num_params: int, num_locals: int) -> None:
        self.__name = name
        self.__num_params = num_params
        self.__num_locals = num_locals
        self.__code : List[Union[Instruction, Label]] = []
        self.__labels : Set[Label] = set()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def code(self) -> List[Union[Instruction, Label]]:
        return self.__code

    @property
    def num_params(self) -> int:
        return self.__num_params

    @property
    def num_locals(self) -> int:
        return self.__num_locals

    def insert_instr(self, instr: Instruction) -> None:
        self.__code.append(instr)

    def insert_label(self, label: Label) -> None:
        assert label not in self.__labels

        self.__labels.add(label)
        self.__code.append(label)
