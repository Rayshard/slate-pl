from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional, Type
from enum import Enum

from slate.utilities import Location, Position

_WORD_SIZE = 8

class SlateType(ABC):
    def __init__(self, byte_size: int) -> None:
        super().__init__()

        self.__byte_size = byte_size

    def get_byte_size(self) -> int:
        return self.__byte_size

    @abstractmethod
    def same_as(self, other: 'SlateType') -> bool:
        pass

class _UnitType(SlateType):
    def __init__(self) -> None:
        super().__init__(0)

    def __str__(self) -> str:
        return "unit"

    def same_as(self, other: 'SlateType') -> bool:
        return isinstance(other, _UnitType)

class _IntType(SlateType):
    def __init__(self, byte_size: int, signed: bool) -> None:
        super().__init__(byte_size)

        self.__signed = signed

    def is_signed(self) -> bool:
        return self.__signed

    def __str__(self) -> str:
        return f"{'u' if self.__signed else ''}i{self.get_byte_size()}"

    def same_as(self, other: 'SlateType') -> bool:
        return isinstance(other, _IntType) and other.get_byte_size() == self.get_byte_size() and other.__signed == self.__signed

class SlateFunction(SlateType):
    def __init__(self, params: List[SlateType], ret: SlateType) -> None:
        super().__init__(_WORD_SIZE)

        self.__params = params
        self.__ret = ret

    def get_params(self) -> List[SlateType]:
        return self.__params

    def get_ret(self) -> SlateType:
        return self.__ret

    def __str__(self) -> str:
        return f"({str.join(',', [str(param) for param in self.__params])}) -> {self.__ret}"

    def same_params(self, other_params: List[SlateType]) -> bool:
        return len(other_params) == len(self.__params) and all([param.same_as(self.__params[i]) for i, param in enumerate(other_params)])

    def same_as(self, other: 'SlateType') -> bool:
        return isinstance(other, SlateFunction) and other.same_params(self.__params) and other.__ret.same_as(self.__ret)

_UNIT = _UnitType()
_I64 = _IntType(8, True)
_UI64 = _IntType(8, False)

def Unit() -> _UnitType:
    return _UNIT

def I64() -> _IntType:
    return _I64

def UI64() -> _IntType:
    return _UI64

@dataclass(frozen=True)
class EnvironmentDefinition:
    name: str
    location: Location
    slate_type: SlateType

class EnvironmentError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

    @staticmethod
    def Redefinition(org_def: EnvironmentDefinition) -> 'EnvironmentError':
        return EnvironmentError(f"'{org_def.name}' was already defined at {org_def.location}")

    @staticmethod
    def UnknownDefinition(name: str) -> 'EnvironmentError':
        return EnvironmentError(f"'{name}' is not defined")

class _Environment:
    def __init__(self, parent: Optional['_Environment'] = None) -> None:
        self.__parent = parent
        self.__definitions : Dict[str, EnvironmentDefinition] = {}

    def define(self, definition: EnvironmentDefinition) -> None:
        if definition.name in self.__definitions:
            raise EnvironmentError.Redefinition(definition)

        self.__definitions[definition.name] = definition

    def undefine(self, name: str) -> None:
        if name not in self.__definitions:
            raise EnvironmentError.UnknownDefinition(name)

        del self.__definitions[name]

    def get_definition(self, name: str, check_parent: bool = False) -> EnvironmentDefinition:
        if name in self.__definitions:
            return self.__definitions[name]
        elif not check_parent or self.__parent is None:
            raise EnvironmentError.UnknownDefinition(name)
        else:
            return self.__parent.get_definition(name, True)

    def is_defined(self, name: str, check_parent: bool = False) -> bool:
        return name in self.__definitions or (self.__parent is not None and check_parent and self.__parent.is_defined(name, True))

    def get_parent(self) -> Optional['_Environment']:
        return self.__parent

def _GenerateDefaultModuleEnv(module_path: str) -> _Environment:
    env = _Environment()
    env.define(EnvironmentDefinition("operator+", Location(module_path), SlateFunction([I64(), I64()], I64())))
    env.define(EnvironmentDefinition("operator-", Location(module_path), SlateFunction([I64(), I64()], I64())))
    env.define(EnvironmentDefinition("operator*", Location(module_path), SlateFunction([I64(), I64()], I64())))
    env.define(EnvironmentDefinition("operator/", Location(module_path), SlateFunction([I64(), I64()], I64())))

    return env

class ModuleContext:
    def __init__(self, module_path: str) -> None:
        self.__module_path = module_path
        self.__env_chain = [_GenerateDefaultModuleEnv(module_path)]
        self.__exports : Dict[str, EnvironmentDefinition] = {}

    def push_env(self) -> _Environment:
        self.__env_chain.append(_Environment(self.__env_chain[-1]))
        return self.__env_chain[-1]

    def pop_env(self) -> _Environment:
        assert len(self.__env_chain) > 1, "ModuleContext must has at least one _Environment in its enviornment chain"
        return self.__env_chain.pop()

    def get_cur_env(self) -> _Environment:
        assert len(self.__env_chain) != 0
        return self.__env_chain[-1]

    def add_export(self, name: str, definintion: EnvironmentDefinition) -> None:
        assert name not in self.__exports
        self.__exports[name] = definintion

    def get_module_path(self) -> str:
        return self.__module_path

    def get_exports(self) -> Dict[str, EnvironmentDefinition]:
        return self.__exports
