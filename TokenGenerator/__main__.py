import click
import sys
import twisted.python.filepath as fp
from .TokenGenerator import GenerateTokens
    

@click.command(name="TokenGenerator")
@click.argument("input-path", nargs=-1)
@click.argument("output-path", is_eager=True)
def makeTokens(input_path, output_path):
    inps = []
    for ip in input_path:
        inp = fp.FilePath(ip)
        assert inp.exists() and inp.isdir()
        inps.append(inp)
    outp = fp.FilePath(output_path)
    if not outp.exists():
        outp.makedirs()
    assert outp.isdir()
    return GenerateTokens(inps, outp)


makeTokens(sys.argv[1:], "python -m TokenGenerator")
