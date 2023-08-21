import spew.generate
import ast
from rich.console import Console
from rich.syntax import Syntax
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--depth", type=int, default=4)
parser.add_argument("--width", type=int, default=10)

args = parser.parse_args()

console = Console()


m = spew.generate.generate_module(args.depth, args.width)
code = ast.unparse(m)
syntax = Syntax(code, "python")
console.print(syntax)
ast.parse(code, "test.py")
