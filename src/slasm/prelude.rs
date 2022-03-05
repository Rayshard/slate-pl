use std::fmt;

pub const VERSION: &str = "1.0.0";
pub const WORD_SIZE: usize = 8;

pub fn to_hex_string(bytes: &[u8]) -> String {
    format!(
        "0x{}",
        bytes
            .iter()
            .map(|byte| format!("{:02x}", byte).to_uppercase())
            .collect::<Vec<String>>()
            .join("")
    )
}

#[derive(Debug)]
pub struct Word {
    pub bytes: [u8; WORD_SIZE],
}

impl Word {
    pub fn new(bytes: [u8; WORD_SIZE]) -> Word {
        Word { bytes: bytes }
    }

    pub fn from_i64(value: i64) -> Word {
        Word {
            bytes: value.to_le_bytes(),
        }
    }

    pub fn from_ui64(value: u64) -> Word {
        Word {
            bytes: value.to_le_bytes(),
        }
    }

    pub fn as_hex(&self) -> String {
        format!(
            "0x{}",
            self.bytes
                .iter()
                .rev()
                .map(|x| format!("{:02x}", x).to_uppercase())
                .collect::<Vec<String>>()
                .join("")
        )
    }

    pub fn as_i64(&self) -> i64 {
        i64::from_le_bytes(self.bytes)
    }

    pub fn as_ui64(&self) -> u64 {
        u64::from_le_bytes(self.bytes)
    }
}

#[derive(Debug)]
pub enum DataType {
    I8,
    UI8,
    I16,
    UI16,
    I32,
    UI32,
    I64,
    UI64,
    F32,
    F64,
}

impl fmt::Display for DataType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{}",
            match self {
                DataType::I8 => "I8",
                DataType::UI8 => "UI8",
                DataType::I16 => "I16",
                DataType::UI16 => "UI16",
                DataType::I32 => "I32",
                DataType::UI32 => "UI32",
                DataType::I64 => "I64",
                DataType::UI64 => "UI64",
                DataType::F32 => "F32",
                DataType::F64 => "F64",
            }
        )
    }
}
