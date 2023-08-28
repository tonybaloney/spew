import spew.generate
import ast
from rich.console import Console
from rich.syntax import Syntax
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--depth", type=int, default=4, help="Maximum depth (nesting) of the module"
)
parser.add_argument("--width", type=int, default=10)
parser.add_argument("--log-level", type=str, default="INFO")
parser.add_argument(
    "--output",
    type=argparse.FileType("w", encoding="utf-8"),
    default=None,
    help="Output file. If not specified, the output will be printed to the console.",
)
parser.add_argument(
    "--check", action="store_true", help="Check if the code is valid Python"
)
args = parser.parse_args()

console = Console()
logger.setLevel(args.log_level)
logger.debug("Generating module with depth %s and width %s", args.depth, args.width)
m = spew.generate.generate_module(
    depth=args.depth, width=args.width, log_level=args.log_level
)
code = ast.unparse(m)


if args.output:
    args.output.write(code)
else:
    syntax = Syntax(code, "python")
    console.print(syntax)

if args.check:
    ast.parse(code, "test.py")
    logger.info("Code is valid Python")
