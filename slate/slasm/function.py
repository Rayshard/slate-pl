from typing import Dict, Iterator, List, Optional, Set, Tuple

from slate.slasm.instruction import Instruction, OpCode

class BasicBlock:
    __TERMINATING_INSTRUCTIONS = set([
        OpCode.JUMP,
        OpCode.COND_JUMP,
        OpCode.RET
    ])

    def __init__(self) -> None:
        self.__instructions : List[Instruction] = []

    def append_instr(self, instr: Instruction) -> None:
        if self.is_terminated():
            raise Exception("Cannot append an instruction to a terminated block!")

        self.__instructions.append(instr)

    def is_terminated(self) -> bool:
        return len(self.__instructions) != 0 and self.__instructions[-1].opcode in BasicBlock.__TERMINATING_INSTRUCTIONS

    def __iter__(self) -> Iterator[Instruction]:
        return self.__instructions.__iter__()

    def __getitem__(self, idx: int) -> Instruction:
        return self.__instructions[idx]

class Function:
    def __init__(self, name: str, params: Set[str], locals: Set[str], returns_value: bool) -> None:
        self.__name = name
        self.__params = set(params)
        self.__locals = set(locals)
        self.__returns_value = returns_value
        self.__basic_blocks : Dict[str, BasicBlock] = {}
        self.__entry : Optional[str] = None

    def add_basic_block(self, name: str, basic_block: BasicBlock) -> None:
        if name in self.__basic_blocks:
            raise Exception(f"Basic block with name {name} already exists!")

        self.__basic_blocks[name] = basic_block

    def contains_nonterminated_basic_block(self) -> bool:
        return not all([bb.is_terminated() for bb in self.__basic_blocks.values()])

    @property
    def name(self) -> str:
        return self.__name

    @property
    def num_params(self) -> int:
        return len(self.__params)

    @property
    def num_locals(self) -> int:
        return len(self.__locals)

    @property
    def returns_value(self) -> bool:
        return self.__returns_value

    @property
    def entry(self) -> str:
        if self.__entry is None:
            raise Exception("Function's entry has not been set!")

        return self.__entry

    @entry.setter
    def entry(self, basic_block_name: str) -> None:
        if basic_block_name not in self.__basic_blocks:
            raise Exception(f"Basic block with name {basic_block_name} does not exist!")

        self.__entry = basic_block_name

    @property
    def basic_blocks(self) -> List[Tuple[str, BasicBlock]]:
        return list(self.__basic_blocks.items())

    @property
    def params(self) -> Set[str]:
        return set(self.__params)

    @property
    def locals(self) -> Set[str]:
        return set(self.__locals)
