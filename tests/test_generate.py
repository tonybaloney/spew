import spew.generate as g
import ast
import pytest
import compileall
import tempfile


@pytest.fixture
def ctx():
    context = g.Context()
    context.max_depth = 1
    return context


def compiles(code: str):
    ast.parse(code)
    with tempfile.NamedTemporaryFile("w", suffix=".py") as f:
        f.write(code)
        result = compileall.compile_file(f.name)
    return result


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_nested_generate_module(depth):
    module = g.generate_module(depth=depth, width=3)
    assert module
    code = ast.unparse(module)
    assert compiles(code)


def test_generate_arg(ctx):
    arg = g.generate_arg(ctx)
    assert arg
    code = ast.unparse(arg)
    assert compiles(code)


def test_generate_function(ctx):
    ctx.max_depth = 1
    func = g.generate_function(ctx)
    assert func
    code = ast.unparse(func)
    assert compiles(code)


def test_generate_asyncfunction(ctx):
    ctx.max_depth = 1
    func = g.generate_asyncfunction(ctx)
    assert func
    code = ast.unparse(func)
    assert compiles(code)


def test_generate_class(ctx):
    ctx.max_depth = 1
    class_ = g.generate_class(ctx)
    assert class_
    code = ast.unparse(class_)
    assert compiles(code)


def test_generate_ellipsis(ctx):
    ellipsis = g.generate_ellipsis(ctx)
    assert ellipsis
    code = ast.unparse(ellipsis)
    assert compiles(code)


def test_generate_pass(ctx):
    pass_ = g.generate_pass(ctx)
    assert pass_
    code = ast.unparse(pass_)
    assert compiles(code)


def test_generate_break(ctx):
    break_ = g.generate_break(ctx)
    assert break_
    code = ast.unparse(break_)
    assert compiles(code)


def test_generate_continue(ctx):
    continue_ = g.generate_continue(ctx)
    assert continue_
    code = ast.unparse(continue_)
    assert compiles(code)


def test_generate_assign(ctx):
    assign = g.generate_assign(ctx)
    assert assign
    code = ast.unparse(assign)
    assert compiles(code)


def test_generate_augassign(ctx):
    augassign = g.generate_augassign(ctx)
    assert augassign
    code = ast.unparse(augassign)
    assert compiles(code)


def test_generate_annassign(ctx):
    annassign = g.generate_annassign(ctx)
    assert annassign
    code = ast.unparse(annassign)
    assert compiles(code)


def test_generate_import(ctx):
    import_ = g.generate_import(ctx)
    assert import_
    code = ast.unparse(import_)
    assert compiles(code)


def test_generate_importfrom(ctx):
    importfrom = g.generate_importfrom(ctx)
    assert importfrom
    code = ast.unparse(importfrom)
    assert compiles(code)


def test_generate_name(ctx):
    name = g.generate_name(ctx)
    assert name
    code = ast.unparse(name)
    assert compiles(code)


def test_generate_constant(ctx):
    constant = g.generate_constant(ctx)
    assert constant
    code = ast.unparse(constant)
    assert compiles(code)


def test_generate_delete(ctx):
    delete = g.generate_delete(ctx)
    assert delete
    code = ast.unparse(delete)
    assert compiles(code)


def test_generate_raise(ctx):
    raise_ = g.generate_raise(ctx)
    assert raise_
    code = ast.unparse(raise_)
    assert compiles(code)


def test_generate_global(ctx):
    global_ = g.generate_global(ctx)
    assert global_
    code = ast.unparse(global_)
    assert compiles(code)


def test_generate_nonlocal(ctx):
    nonlocal_ = g.generate_nonlocal(ctx)
    assert nonlocal_
    code = ast.unparse(nonlocal_)
    assert compiles(code)


def test_generate_for(ctx):
    ctx.max_depth = 1
    for_ = g.generate_for(ctx)
    assert for_
    code = ast.unparse(for_)
    assert compiles(code)


def test_generate_asyncfor(ctx):
    ctx.max_depth = 1
    asyncfor = g.generate_asyncfor(ctx)
    assert asyncfor
    code = ast.unparse(asyncfor)
    assert compiles(code)


def test_generate_while(ctx):
    ctx.max_depth = 1
    while_ = g.generate_while(ctx)
    assert while_
    code = ast.unparse(while_)
    assert compiles(code)


def test_generate_if(ctx):
    ctx.max_depth = 1
    if_ = g.generate_if(ctx)
    assert if_
    code = ast.unparse(if_)
    assert compiles(code)


def test_generate_with(ctx):
    ctx.max_depth = 1
    with_ = g.generate_with(ctx)
    assert with_
    code = ast.unparse(with_)
    assert compiles(code)


def test_generate_asyncwith(ctx):
    ctx.max_depth = 1
    asyncwith = g.generate_asyncwith(ctx)
    assert asyncwith
    code = ast.unparse(asyncwith)
    assert compiles(code)


def test_generate_assert(ctx):
    assert_ = g.generate_assert(ctx)
    assert assert_
    code = ast.unparse(assert_)
    assert compiles(code)


def test_generate_expression(ctx):
    expression = g.generate_expression(ctx)
    assert expression
    code = ast.unparse(expression)
    assert compiles(code)


def test_generate_try(ctx):
    ctx.max_depth = 1
    try_ = g.generate_try(ctx)
    assert try_
    code = ast.unparse(try_)
    assert compiles(code)


def test_generate_trystar(ctx):
    ctx.max_depth = 1
    try_ = g.generate_trystar(ctx)
    assert try_
    code = ast.unparse(try_)
    assert compiles(code)


def test_generate_matchvalue(ctx):
    matchvalue = g.generate_matchvalue(ctx)
    assert matchvalue
    case = ast.unparse(matchvalue)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_matchsingleton(ctx):
    singleton = g.generate_matchsingleton(ctx)
    assert singleton
    case = ast.unparse(singleton)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_matchsequence(ctx):
    matchsequence = g.generate_matchsequence(ctx)
    assert matchsequence
    case = ast.unparse(matchsequence)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_matchmapping(ctx):
    matchmapping = g.generate_matchmapping(ctx)
    assert matchmapping
    case = ast.unparse(matchmapping)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_matchclass(ctx):
    matchclass = g.generate_matchclass(ctx)
    assert matchclass
    case = ast.unparse(matchclass)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_matchas(ctx):
    matchas = g.generate_matchas(ctx)
    assert matchas
    case = ast.unparse(matchas)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_matchor(ctx):
    matchor = g.generate_matchor(ctx)
    assert matchor
    case = ast.unparse(matchor)
    code = f"match x:\n case {case}: pass"
    assert compiles(code)


def test_generate_match(ctx):
    match = g.generate_match(ctx)
    assert match
    code = ast.unparse(match)
    assert compiles(code), match


def test_generate_list(ctx):
    list_ = g.generate_list(ctx)
    assert list_
    code = ast.unparse(list_)
    assert compiles(code)


def test_generate_tuple(ctx):
    tuple_ = g.generate_tuple(ctx)
    assert tuple_
    code = ast.unparse(tuple_)
    assert compiles(code)


def test_generate_boolop(ctx):
    boolop = g.generate_boolop(ctx)
    assert boolop
    code = ast.unparse(boolop)
    assert compiles(code)


def test_generate_binop(ctx):
    binop = g.generate_binop(ctx)
    assert binop
    code = ast.unparse(binop)
    assert compiles(code)


def test_generate_unaryop(ctx):
    unaryop = g.generate_unaryop(ctx)
    assert unaryop
    code = ast.unparse(unaryop)
    assert compiles(code)


def test_generate_lambda(ctx):
    lambda_ = g.generate_lambda(ctx)
    assert lambda_
    code = ast.unparse(lambda_)
    assert compiles(code)


def test_generate_ifexp(ctx):
    ifexp = g.generate_ifexp(ctx)
    assert ifexp
    code = ast.unparse(ifexp)
    assert compiles(code)


def test_generate_dict(ctx):
    dict_ = g.generate_dict(ctx)
    assert dict_
    code = ast.unparse(dict_)
    assert compiles(code)


def test_generate_set(ctx):
    set_ = g.generate_set(ctx)
    assert set_
    code = ast.unparse(set_)
    assert compiles(code)


def test_generate_listcomp(ctx):
    listcomp = g.generate_listcomp(ctx)
    assert listcomp
    code = ast.unparse(listcomp)
    assert compiles(code)


def test_generate_setcomp(ctx):
    setcomp = g.generate_setcomp(ctx)
    assert setcomp
    code = ast.unparse(setcomp)
    assert compiles(code)


def test_generate_dictcomp(ctx):
    dictcomp = g.generate_dictcomp(ctx)
    assert dictcomp
    code = ast.unparse(dictcomp)
    assert compiles(code)


def test_generate_generatorexp(ctx):
    generatorexp = g.generate_generatorexp(ctx)
    assert generatorexp
    code = ast.unparse(generatorexp)
    assert compiles(code)


def test_generate_await(ctx):
    await_ = g.generate_await(ctx)
    assert await_
    code = ast.unparse(await_)
    assert compiles(code)


def test_generate_yield(ctx):
    yield_ = g.generate_yield(ctx)
    assert yield_
    code = ast.unparse(yield_)
    assert compiles(code)


def test_generate_yieldfrom(ctx):
    yieldfrom = g.generate_yieldfrom(ctx)
    assert yieldfrom
    code = ast.unparse(yieldfrom)
    assert compiles(code)


def test_generate_compare(ctx):
    compare = g.generate_compare(ctx)
    assert compare
    code = ast.unparse(compare)
    assert compiles(code)


def test_generate_call(ctx):
    call = g.generate_call(ctx)
    assert call
    code = ast.unparse(call)
    assert compiles(code)


def test_generate_formattedvalue(ctx):
    formattedvalue = g.generate_formattedvalue(ctx)
    assert formattedvalue
    code = ast.unparse(formattedvalue)
    assert code  # isn't valid syntax


def test_generate_joinedstr(ctx):
    joinedstr = g.generate_joinedstr(ctx)
    assert joinedstr
    code = ast.unparse(joinedstr)
    assert compiles(code)


def test_generate_attribute(ctx):
    attribute = g.generate_attribute(ctx)
    assert attribute
    code = ast.unparse(attribute)
    assert compiles(code)


def test_generate_subscript(ctx):
    subscript = g.generate_subscript(ctx)
    assert subscript
    code = ast.unparse(subscript)
    assert compiles(code)
