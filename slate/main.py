from dataclasses import dataclass
from typing import Any, Dict, Optional, cast
from pathlib import Path
import click
from pylpc.pylpc import ParseError

from . import slate_parser, interpreter
from .visitors import serializer, llvm_emitter

@dataclass
class CLIContext:
    emit_ast : bool = False

@click.group()
@click.option('--emit-ast', is_flag=True)
@click.pass_context
def cli(ctx: click.Context, emit_ast: bool):
    ctx.ensure_object(CLIContext)
    cli_context = ctx.find_object(CLIContext)

    if cli_context is not None:
        cli_context.emit_ast = emit_ast

@cli.command(help="Runs the specified file.")
@click.option('--backend', type=click.Choice(['llvm', 'slate'], case_sensitive=False), required=False, default="llvm")
@click.option('--emit-ir', is_flag=True)
@click.argument('file_path', type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, nargs=1)
@click.pass_context
def run(ctx: click.Context, backend: str, emit_ir: bool, file_path: Path):
    cli_context = cast(CLIContext, ctx.find_object(CLIContext))
    parsing_context = slate_parser.Context()
    
    try:
        slate_parser.parse_file(file_path, parsing_context)
    except ParseError as e:
        print(e)

    if cli_context.emit_ast:
        import json

        with file_path.with_suffix(file_path.suffix + ".ast.json").open("w") as output_file:
            serialization = {
                "modules": [serializer.visit(m) for m in parsing_context.modules.values()]
            }

            json.dump(serialization, output_file, indent=4)

    # Interpret program
    exit_code : interpreter.ExitCode = 0

    if backend == "llvm":
        from llvmlite import ir # type: ignore
        from llvmlite.binding import linker # type: ignore

        ir_module = ir.Module("MODULE")

        for m in parsing_context.modules.values():
            llvm_emitter.visit(m, ir_module)

        if emit_ir:
            with file_path.with_suffix(file_path.suffix + ".ir.ll").open("w") as output_file:
                output_file.write(str(ir_module))

        exit_code = interpreter.run_llvm(ir_module, file_path.as_posix() + "#entry")
    else:
        raise NotImplementedError(f"backend={backend}")

    print(f"Exited with code {exit_code}.")

        
