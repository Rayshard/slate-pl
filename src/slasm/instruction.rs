use crate::slasm::prelude::DataType;
use crate::slasm::prelude::Word;

#[derive(Debug)]
pub enum Instruction {
    Noop,
    LoadConst {
        value: Word,
    },
    LoadLocal {
        name: String,
    },
    StoreLocal {
        name: String,
    },
    LoadParam {
        name: String,
    },
    StoreParam {
        name: String,
    },
    LoadGlobal {
        name: String,
    },
    StoreGlobal {
        name: String,
    },
    LoadMem {
        offset: i64,
    },
    StoreMem {
        offset: i64,
    },
    LoadFuncAddr {
        name: String,
    },
    Pop,
    Add {
        data_type: DataType,
    },
    Sub {
        data_type: DataType,
    },
    Mul {
        data_type: DataType,
    },
    Div {
        data_type: DataType,
    },
    Mod {
        data_type: DataType,
    },
    Inc {
        data_type: DataType,
    },
    Dec {
        data_type: DataType,
    },
    Eq {
        data_type: DataType,
    },
    Neq {
        data_type: DataType,
    },
    Gt {
        data_type: DataType,
    },
    Lt {
        data_type: DataType,
    },
    GtEq {
        data_type: DataType,
    },
    LtEq {
        data_type: DataType,
    },
    Neg {
        data_type: DataType,
    },
    Or,
    And,
    Xor,
    Not,
    Shl,
    Shr,
    Convert {
        dt_from: DataType,
        dt_to: DataType,
    },
    Jump {
        target: String,
    },
    CondJump {
        target: String,
    },
    Call {
        target: String,
    },
    IndirectCall {
        num_params: u64,
        num_returns: u64,
    },
    Ret,
}
