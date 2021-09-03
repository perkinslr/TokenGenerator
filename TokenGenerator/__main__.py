import click
import sys
import twisted.python.filepath as fp
from .TokenGenerator import GenerateTokens
import os
    

@click.command(name="TokenGenerator")
@click.option("--generate-zip")
@click.argument("input-path", nargs=-1)
@click.argument("output-path", is_eager=True)
def makeTokens(generate_zip, input_path, output_path):
    inps = []
    for ip in input_path:
        inp = fp.FilePath(ip)
        assert inp.exists() and inp.isdir()
        inps.append(inp)
    outp = fp.FilePath(output_path)
    if not outp.exists():
        outp.makedirs()
    assert outp.isdir()
    GenerateTokens(inps, outp)
    if generate_zip:
        cwd = os.getcwd()
        for dir in outp.children():
            os.chdir(dir.path)
            os.system(f"zip -r {dir.siblingExtension('.rptok').path} ./*")


makeTokens(sys.argv[1:], "python -m TokenGenerator")
