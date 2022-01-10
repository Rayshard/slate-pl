import click
from . import slate_parser

@click.group()
def cli():
    pass

@cli.command(help="Outputs the ast of the speficied file.")
@click.option('-o', '--output', type=click.Path(dir_okay=False), required=True, nargs=1)
@click.argument('file_path', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def ast(output: str, file_path: str):
    import json

    try:
        module = slate_parser.parse_file(file_path)

        with open(output, 'w') as output_file:
            json.dump(module.serialize(), output_file, indent=4)

    except Exception as e:
        print(e)
