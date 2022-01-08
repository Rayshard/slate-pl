import click

@click.group()
def cli():
    pass

@cli.command(help="Simulate the execution of the specified file.")
@click.argument('file_path', type=click.Path(exists=True, resolve_path=True), required=True, nargs=1)
def run(file_path: str):
    print(file_path)

@cli.command(help="Compile the specified file into an executable.")
@click.argument('file_path', type=click.Path(exists=True, resolve_path=True), required=True, nargs=1)
def compile(file_path: str):
    print(file_path)
    raise NotImplementedError()

@cli.command(help="Outputs the ast of the speficied file.")
@click.argument('file_path', type=click.Path(exists=True, resolve_path=True), required=True, nargs=1)
def ast(file_path: str):
    print(file_path)
    raise NotImplementedError()

@cli.command(help="Outputs the bytecode of the speficied file.")
@click.argument('file_path', type=click.Path(exists=True, resolve_path=True), required=True, nargs=1)
def bytecode(file_path: str):
    print(file_path)
    raise NotImplementedError()
