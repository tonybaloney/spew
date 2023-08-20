import spew.generate
import ast
from rich.console import Console
from rich.syntax import Syntax

console = Console()


m = spew.generate.generate_module()
code = ast.unparse(m)
syntax = Syntax(code, "python")
console.print(syntax)
ast.parse(code, "test.py")
