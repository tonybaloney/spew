import ast
from contextlib import contextmanager
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
        self.depth = 0
        self.width = DEFAULT_WIDTH
    
    @contextmanager
    def nested(self):
        self.depth += 1
        yield
        self.depth -= 1

def generate_arg() -> ast.arg:
    arg = ast.arg()
    arg.arg = make_name()
    arg.annotation = None
    return arg

def generate_function(ctx: Context) -> ast.FunctionDef:
    f = ast.FunctionDef()
    f.args = ast.arguments()
    f.args.args = [generate_arg() for _ in range(random.randint(0, 10))]
    f.args.posonlyargs = []
    f.args.kwonlyargs = []
    f.args.defaults = []
    f.name = make_name()
    with ctx.nested():
        f.body = generate_stmts(ctx)
    f.decorator_list = []
    f.lineno = 1
    return f

def generate_asyncfunction(ctx: Context) -> ast.AsyncFunctionDef:
    f = ast.AsyncFunctionDef()
    f.args = ast.arguments()
    f.args.args = [generate_arg() for _ in range(random.randint(0, 10))]
    f.args.posonlyargs = []
    f.args.kwonlyargs = []
    f.args.defaults = []
    f.name = make_name()
    with ctx.nested():
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
    for _ in range(random.randint(1, 3)): # TODO: Vary length
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
    # TODO : Is expr, but jst doing name 
    d.targets = [generate_name()] # TODO: Vary targets
    return d

def generate_raise(ctx: Context) -> ast.Raise:
    r = ast.Raise()
    r.exc = generate_expr()
    return r

def generate_global(ctx: Context) -> ast.Global:
    g = ast.Global()
    g.names = [make_name()] # TODO: Vary length
    return g

def generate_nonlocal(ctx: Context) -> ast.Nonlocal:
    n = ast.Nonlocal()
    n.names = [make_name()] # TODO: Vary length
    return n

def generate_for(ctx: Context) -> ast.For:
    f = ast.For()
    f.target = generate_name() # Can be expr, but just doing name
    f.iter = generate_expr()
    f.lineno = 1
    with ctx.nested():
        f.body = generate_stmts(ctx)
    if randbool():
        with ctx.nested():
            f.orelse = generate_stmts(ctx)
    else:
        f.orelse = [] # TODO: Raise bug report about this?
    return f

def generate_asyncfor(ctx: Context) -> ast.AsyncFor:
    f = ast.AsyncFor()
    f.target = generate_name()
    f.iter = generate_expr()
    f.lineno = 1
    with ctx.nested():
        f.body = generate_stmts(ctx)
    if randbool():
        with ctx.nested():
            f.orelse = generate_stmts(ctx)
    else:
        f.orelse = []
    return f

def generate_while(ctx: Context) -> ast.While:
    w = ast.While()
    w.test = generate_expr()
    w.lineno = 1
    with ctx.nested():
        w.body = generate_stmts(ctx)
    if randbool():
        with ctx.nested():
            w.orelse = generate_stmts(ctx)
    else:
        w.orelse = []
    return w

def generate_if(ctx: Context) -> ast.If:
    i = ast.If()
    i.test = generate_expr()
    i.lineno = 1
    with ctx.nested():
        i.body = generate_stmts(ctx)
    if randbool():
        with ctx.nested():
            i.orelse = generate_stmts(ctx)
    else:
        i.orelse = []
    return i

def generate_with(ctx: Context) -> ast.With:
    w = ast.With()
    w.lineno = 1
    w.items = []
    for _ in range(random.randint(1, 3)): # TODO: Vary length
        withitem = ast.withitem()
        withitem.context_expr = generate_expr()
        if randbool():
            withitem.optional_vars = generate_name() # TODO : Can be expr, but just doing name
        w.items.append(withitem)
    with ctx.nested():
        w.body = generate_stmts(ctx)
    return w

def generate_asyncwith(ctx: Context) -> ast.AsyncWith:
    w = ast.AsyncWith()
    w.lineno = 1
    w.items = []
    for _ in range(random.randint(1, 3)): # TODO: Vary length
        withitem = ast.withitem()
        withitem.context_expr = generate_expr()
        if randbool():
            withitem.optional_vars = generate_name() # TODO : Can be expr, but just doing name
        w.items.append(withitem)
    with ctx.nested():
        w.body = generate_stmts(ctx)
    return w

def generate_assert(ctx: Context) -> ast.Assert:
    a = ast.Assert()
    a.test = generate_expr()
    if randbool():
        a.msg = generate_expr()
    return a

def generate_expression(ctx: Context) -> ast.Expr:
    e = ast.Expr()
    e.value = generate_expr()
    return e

def generate_try(ctx: Context) -> ast.Try:
    t = ast.Try()
    t.lineno = 1
    with ctx.nested():
        t.body = generate_stmts(ctx)
    t.handlers = []
    for _ in range(random.randint(1, 3)): # TODO: Vary length
        handler = ast.ExceptHandler()
        handler.lineno = 1
        handler.type = generate_expr()
        if randbool():
            handler.name = make_name()
        with ctx.nested():
            handler.body = generate_stmts(ctx)
        t.handlers.append(handler)
    if randbool():
        with ctx.nested():
            t.orelse = generate_stmts(ctx)
    else:
        t.orelse = []
    if randbool():
        with ctx.nested():
            t.finalbody = generate_stmts(ctx)
    else:
        t.finalbody = []
    return t

def generate_matchvalue(ctx: Context) -> ast.MatchValue:
    m = ast.MatchValue()
    m.value = generate_expr()
    return m

def generate_matchsingleton(ctx: Context) -> ast.MatchSingleton:
    m = ast.MatchSingleton()
    m.value = generate_constant()
    return m


def generate_matchpattern(ctx: Context) -> ast.pattern:
    """
    MatchValue(expr value)
    | MatchSingleton(constant value)
    | MatchSequence(pattern* patterns)
    | MatchMapping(expr* keys, pattern* patterns, identifier? rest)
    | MatchClass(expr cls, pattern* patterns, identifier* kwd_attrs, pattern* kwd_patterns)

    | MatchStar(identifier? name)
    -- The optional "rest" MatchMapping parameter handles capturing extra mapping keys

    | MatchAs(pattern? pattern, identifier? name)
    | MatchOr(pattern* patterns)
    """

def generate_match(ctx: Context) -> ast.Match:
    m = ast.Match()
    m.subject = generate_expr()
    m.cases = []
    for _ in range(random.randint(1, 3)): # TODO: Vary length
        case = ast.match_case()
        case.pattern = generate_matchpattern(ctx)
        if randbool():
            case.guard = generate_expr()
        with ctx.nested():
            case.body = generate_stmts(ctx)
        m.cases.append(case)
    return m

STMT_GENERATORS = (
    generate_function,
    # generate_asyncfunction,
    # generate_class,
    generate_return,
    generate_delete,
    generate_assign,
    generate_augassign,
    generate_annassign,
    generate_for,
    generate_asyncfor,
    generate_while,
    generate_if,
    generate_with,
    generate_asyncwith,
    # generate_match,
    generate_raise,
    generate_try,
    # generate_trystar,
    generate_assert,
    generate_import,
    generate_importfrom,
    generate_global,
    generate_nonlocal,
    generate_expression,
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
        return [generate_pass(ctx)]
    
    return [random.choice(STMT_GENERATORS)(ctx) for _ in range(ctx.width)]

def generate_expr() -> ast.expr:
    return random.choice(EXPR_GENERATORS)()


def generate_module(depth: int, width: int) -> ast.Module:
    ctx = Context()
    MAX_DEPTH = depth
    ctx.width = width
    mod = ast.Module()
    mod.type_ignores = []
    with ctx.nested():
        mod.body = generate_stmts(ctx)
    return mod
