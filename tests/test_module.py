import spew.module
import ast


def test_basic_module():
    m = spew.module.generate()
    assert m
    assert isinstance(ast.unparse(m), str) 