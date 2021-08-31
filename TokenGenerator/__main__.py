import click
import sys
import twisted.python.filepath as fp
from .TokenGenerator import GenerateTokens
    

@click.command(name="TokenGenerator")
@click.argument("input-path")
@click.argument("output-path")
def makeTokens(input_path, output_path):
    inp = fp.FilePath(input_path)
    outp = fp.FilePath(output_path)
    assert inp.exists() and inp.isdir()
    if not outp.exists():
        outp.makedirs()
    assert outp.isdir()
    return GenerateTokens(inp, outp)


makeTokens(sys.argv[1:], "python -m TokenGenerator")
