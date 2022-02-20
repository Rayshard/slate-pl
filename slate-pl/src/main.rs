use crate::slasm::instruction::Instruction;
use crate::slasm::prelude::Word;

mod slasm;

fn main() {
    println!("{}", Word::from_ui64(123).as_hex());
}
