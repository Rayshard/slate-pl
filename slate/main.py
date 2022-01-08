import pylpc, pylpc.parsers


def cli():
    print(pylpc.parsers.Chars().parse("hello world"))