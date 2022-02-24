use crate::slasm::prelude::DataType;

#[derive(Debug)]
pub enum Instruction {
    Noop,
    Push {
        data: Vec<u8>,
    },
    Pop {
        amt: u64,
    },
    Allocate {
        amt: u64,
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
    LoadLocalAddr {
        name: String,
    },
    LoadParamAddr {
        name: String,
    },
    LoadGlobalAddr {
        name: String,
    },
    LoadFuncAddr {
        name: String,
    },
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
        from: DataType,
        to: DataType,
    },
    Jump {
        target: String,
    },
    CondJump {
        true_target: String,
        false_target: String,
    },
    Call {
        target: String,
    },
    IndirectCall {
        param_buffer_size: u64,
        ret_buffer_size: u64,
    },
    Ret,
}
