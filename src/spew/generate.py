import ast
import random
from spew.names import generate as make_name

MAX_DEPTH = 3
DEFAULT_WIDTH = 20

def randbool() -> bool:
    return random.randint(0, 1) == 1

class Context:
    depth: int
    width: int = DEFAULT_WIDTH

    def __init__(self):
        self.depth = 1
        self.width = DEFAULT_WIDTH

def generate_arg() -> ast.arg:
    arg = ast.arg()
    arg.arg = make_name()
    arg.annotation = None
    return arg

def generate_function(ctx: Context) -> ast.FunctionDef:
    f = ast.FunctionDef()
    f.args = ast.arguments()
    f.args.args = [generate_arg(), generate_arg()]
    f.args.posonlyargs = []
    f.args.kwonlyargs = []
    f.args.defaults = []
    f.name = make_name()
    f.body = generate_stmts(ctx)
    f.decorator_list = []
    f.lineno = 1
    return f

def generate_ellipsis(ctx: Context) -> ast.Ellipsis:
    return ast.Ellipsis()

def generate_pass(ctx: Context) -> ast.Pass:
    return ast.Pass()

def generate_break(ctx: Context) -> ast.Break:
    return ast.Break()

def generate_continue(ctx: Context) -> ast.Continue:
    return ast.Continue()

def generate_assign(ctx: Context) -> ast.Assign:
    asgn = ast.Assign()
    asgn.lineno = 1
    asgn.targets = [generate_name()]  # TODO: vary number of assignment targets
    asgn.value = generate_expr()
    return asgn

OPERATORS = [
    ast.Add,
    ast.BitAnd,
    ast.BitOr,
    ast.BitXor,
    ast.Div,
    ast.FloorDiv,
    ast.LShift,
    ast.Mod,
    ast.Mult,
    ast.MatMult,
    ast.Pow,
    ast.RShift,
    ast.Sub,
]

def generate_augassign(ctx: Context) -> ast.AugAssign:
    asgn = ast.AugAssign()
    asgn.lineno = 1
    asgn.target = generate_name()
    asgn.value = generate_expr()
    asgn.op = random.choice(OPERATORS)()
    return asgn

def generate_annassign(ctx: Context) -> ast.AnnAssign:
    asgn = ast.AnnAssign()
    asgn.lineno = 1
    asgn.target = generate_name()
    asgn.value = generate_expr()
    asgn.simple = 1  # TODO : Work out waht this is
    asgn.annotation = generate_expr()
    return asgn

def generate_import(ctx: Context) -> ast.Import:
    im = ast.Import()
    im.names = []
    for i in range(random.randint(1, 3)): # TODO: Vary length
        alias = ast.alias()
        alias.name = make_name()
        if randbool():
            alias.asname = make_name()

        im.names.append(alias)
    return im

def generate_importfrom(ctx: Context) -> ast.ImportFrom:
    im = ast.ImportFrom()
    im.module = make_name()
    im.names = []
    for i in range(random.randint(1, 3)): # TODO: Vary length
        alias = ast.alias()
        alias.name = make_name()
        if randbool():
            alias.asname = make_name()

        im.names.append(alias)
    return im

def generate_name() -> ast.Name:
    name = ast.Name()
    name.id = make_name()
    # TODO: Add type info
    return name

def generate_constant() -> ast.Constant:
    c = ast.Constant()
    c.value = random.choice((None, str(), bytes(), bool(), int(), float(), complex(), Ellipsis))
    return c

def generate_return(ctx: Context) -> ast.Return:
    r = ast.Return()
    if randbool():
        r.value = generate_expr()
    return r

def generate_delete(ctx: Context) -> ast.Delete:
    d = ast.Delete()
    d.targets = [generate_name()] # TODO: Vary targets
    return d

def generate_raise(ctx: Context) -> ast.Raise:
    r = ast.Raise()
    r.exc = generate_expr()
    return r

def generate_assert(ctx: Context) -> ast.Assert:
    a = ast.Assert()
    a.test = generate_expr()
    if randbool():
        a.msg = generate_expr()
    return a

def generate_global(ctx: Context) -> ast.Global:
    g = ast.Global()
    g.names = [make_name()] # TODO: Vary length
    return g

def generate_nonlocal(ctx: Context) -> ast.Nonlocal:
    n = ast.Nonlocal()
    n.names = [make_name()] # TODO: Vary length
    return n

STMT_GENERATORS = (
    # generate_function,  #TODO: Fix indent issue
    # generate_asyncfunction,
    # generate_class,
    generate_return,
    generate_delete,
    generate_assign,
    generate_augassign,
    generate_annassign,
    # generate_for,
    # generate_asyncfor,
    # generate_while,
    # generate_if,
    # generate_with,
    # generate_asyncwith,
    # generate_match,
    generate_raise,
    # generate_try,
    # generate_trystar,
    # generate_assert,
    generate_import,
    generate_importfrom,
    generate_global,
    generate_nonlocal,
    # generate_expr,
    generate_pass,
    generate_break,
    generate_continue,
    # generate_ellipsis,
)

EXPR_GENERATORS = (
    # generate_boolop,
    # generate_namedexpr,
    # generate_binop,
    # generate_unaryop,
    # generate_lambda,
    # generate_ifexp,
    # generate_dict,
    # generate_set,
    # generate_listcomp,
    # generate_setcomp,
    # generate_dictcomp,
    # generate_generatorexp,
    # generate_await,
    # generate_yield,
    # generate_yieldfrom,
    # generate_compare,
    # generate_call,
    # generate_formattedvalue,
    # generate_joinedstr,
    generate_constant,
    # generate_attribute,
    # generate_subscript,
    # generate_starred,
    generate_name,
    # generate_list,
    # generate_tuple,
    # generate_slice,
)


def generate_stmts(ctx: Context) -> list[ast.stmt]:
    if ctx.depth >= MAX_DEPTH:
        return []
    ctx.depth += 1
    return [random.choice(STMT_GENERATORS)(ctx) for _ in range(ctx.width)]

def generate_expr() -> ast.expr:
    return random.choice(EXPR_GENERATORS)()


def generate_module() -> ast.Module:
    ctx = Context()
    mod = ast.Module()
    mod.type_ignores = []
    mod.body = []
    mod.body = generate_stmts(ctx)
    return mod
