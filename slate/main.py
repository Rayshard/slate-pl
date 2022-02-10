from dataclasses import dataclass
import subprocess
import time
from typing import Any, Dict, List, Optional, cast
from pathlib import Path
import click
import xml.etree.ElementTree as ET
import xml.dom.minidom

from slate.ast import ASTModule
from slate.slasm.visitors import xml_visitor as slasm_xml_visitor
from slate.slasm.visitors import nasm_visitor as slasm_nasm_visitor
from slate.visitors import slasm_emitter

from . import parser, interpreter
from .visitors import serializer, llvm_emitter, typechecker

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
@click.option('--emit-slasm', is_flag=True)
@click.option('-O', '--optimize', is_flag=True)
@click.argument('file_path', type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True, nargs=1)
@click.pass_context
def compile(ctx: click.Context, emit_slasm: bool, optimize: bool, file_path: Path):
    cli_context = cast(CLIContext, ctx.find_object(CLIContext))
    
    # Parse
    print(f"Parsing {file_path} ...")
    start_time = time.perf_counter()

    parsing_context = parser.Context()
    
    try:
        parser.parse_file(file_path, parsing_context)
    except parser.ParseError as e:
        print(e.get_message_with_trace())
        exit(-1)

    print(f"Parsing took {time.perf_counter() - start_time} seconds")

    # Type Check
    print(f"\nTypechecking...")
    start_time = time.perf_counter()

    modules : Dict[str, ASTModule] = {}

    for path, module in parsing_context.modules.items():
        try:
            modules[path] = typechecker.visit(module)
        except typechecker.TCError as e:
            print(e)
            exit(-1)

    print(f"Typechecking took {time.perf_counter() - start_time} seconds")

    # Emit AST
    if cli_context.emit_ast:
        import json

        with file_path.with_suffix(file_path.suffix + ".ast.xml").open("w") as output_file:
            serialization = ET.Element("AST")
            
            for m in modules.values():
                serialization.append(serializer.visit(m))

            output_file.write(xml.dom.minidom.parseString(ET.tostring(serialization, 'unicode')).toprettyxml(indent='    '))

    # Convert to slasm
    print(f"\nConverting to slasm...")
    start_time = time.perf_counter()

    slasm_program = slasm_emitter.visit(list(modules.values()), "slasm-interpreter")

    print(f"Slasm conversion took {time.perf_counter() - start_time} seconds")

    # Emit slasm
    if emit_slasm:
        with file_path.with_suffix(file_path.suffix + ".slasm.xml").open("w") as output_file:
            output_file.write(slasm_xml_visitor.to_string(slasm_xml_visitor.emit_Program(slasm_program)))

    # Run program
    print(f"\nCompiling...")
    start_time = time.perf_counter()

    with open('slate/slasm/nasm_template.asm', 'r') as template_file:
        template = template_file.read()

        native_funcs = {
            "LINUX_x86_64_SYSCALL1_WITH_RET": slasm_nasm_visitor.GlobalContext.FuncDef(2, True),
            "LINUX_x86_64_SYSCALL1_NO_RET": slasm_nasm_visitor.GlobalContext.FuncDef(2, False),
            "C_CALL_3_WITH_RET": slasm_nasm_visitor.GlobalContext.FuncDef(4, True),
            "C_CALL_3_NO_RET": slasm_nasm_visitor.GlobalContext.FuncDef(4, False),
            "DEBUG_PRINT_I64": slasm_nasm_visitor.GlobalContext.FuncDef(1, False),
        }

        asm_file_path = file_path.with_suffix(file_path.suffix + ".asm")
        object_file_path = file_path.with_suffix(file_path.suffix + ".o")
        executable_file_path = file_path.with_suffix(file_path.suffix + ".bin")

        with asm_file_path.open("w") as file:
            file.write(slasm_nasm_visitor.emit_Program(slasm_program, template, native_funcs))

        process = subprocess.run(f"nasm -f macho64 {asm_file_path} && gcc -arch x86_64 -o {executable_file_path} {object_file_path} && rm {object_file_path}", shell=True)
        
        if process.stdout:
            print(process.stdout)

        if process.stderr:
            print(process.stderr)

        print(f"Compilation took {time.perf_counter() - start_time} seconds")
