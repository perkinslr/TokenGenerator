import click
import sys
import twisted.python.filepath as fp
import os
from .Deconstructor import RipTokens

@click.command(name="TokenGenerator.Deconstructor")
@click.argument("input-path", nargs=-1)
@click.argument("output-path", is_eager=True)
def makeTokens(input_path, output_path):
    inps = []
    for ip in input_path:
        inp = fp.FilePath(ip)
        assert inp.exists()
        inps.append(inp)
    outp = fp.FilePath(output_path)
    if not outp.exists():
        outp.makedirs()
    assert outp.isdir()
    RipTokens(inps, outp)


makeTokens(sys.argv[1:], "python -m TokenGenerator.Deconstructor")
