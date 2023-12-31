# spew

A tool for generating random, syntactically-correct Python code. Designed for fuzzing and testing of tools that parse Python code.

Designed for Python 3.10 and above, this is for testing the latest syntax. 

Supports:

- Functions
- For, If, While
- Async With, For, FunctionDef
- All constant expressions
- Match statements
- Many expression types
- Decorators
- Classes

## Usage

You can use at the command line:

```console
> python -m spew --depth=4
```

Caution, depths higher than 5 creating a huge recursive computing load. (A depth of 6 creates a file ~40,000 lines of code.)

Also, you can generate specific nodes, like modules or functions:

```python
import spew.generate as g

context = g.Context()
func = g.generate_function(context) # returns an ast.FunctionDef object
```

To generate AST objects back into Python code you can use the `ast.unparse()` function.

The full list of command-line options:

```default
python -m spew --help
usage: __main__.py [-h] [--depth DEPTH] [--width WIDTH] [--log-level LOG_LEVEL] [--output OUTPUT] [--check]

options:
  -h, --help            show this help message and exit
  --depth DEPTH         Maximum depth (nesting) of the module
  --width WIDTH
  --log-level LOG_LEVEL
  --output OUTPUT       Output file. If not specified, the output will be printed to the console.
  --check               Check if the code is valid Python
```
