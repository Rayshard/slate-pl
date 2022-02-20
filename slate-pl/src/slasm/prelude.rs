const WORD_SIZE: usize = 8;

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
        let be_bytes : Vec<u8> = self.bytes.iter().copied().rev().collect();
        format!("0x{}", hex::encode_upper(be_bytes))
    }

    pub fn as_i64(&self) -> i64 {
        i64::from_le_bytes(self.bytes)
    }

    pub fn as_ui64(&self) -> u64 {
        u64::from_le_bytes(self.bytes)
    }
}

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
    F64
}
