import ast
from contextlib import contextmanager
import random as _random
import typing
from spew.names import generate as make_name

MAX_DEPTH = 3
DEFAULT_WIDTH = 20

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


class Context:
    depth: int
    in_loop: bool
    names: list[str]
    max_depth: int = MAX_DEPTH
    width: int = DEFAULT_WIDTH

    def __init__(self):
        self.depth = 0
        self.width = DEFAULT_WIDTH
        self.in_loop = False
        self.names = []

    @contextmanager
    def nested(self):
        self.depth += 1
        yield
        self.depth -= 1

    @contextmanager
    def inloop(self):
        self.in_loop = True
        yield
        self.in_loop = False


def randbool(ctx: Context) -> bool:
    # TODO: Use context for reproducible results
    return _random.randint(0, 1) == 1


T = typing.TypeVar("T")


def randchoice(ctx: Context, choices: typing.Sequence[T]) -> T:
    # TODO: Use context for reproducible results
    return _random.choice(choices)


def randint(ctx: Context, a: int, b: int) -> int:
    # TODO: Use context for reproducible results
    return _random.randint(a, b)


def generate_arg(ctx: Context) -> ast.arg:
    arg = ast.arg()
    arg.arg = make_name(ctx, new=True)
    # arg.annotation = None # TODO: Randomly assign annotations
    # TODO: Set defaults?
    return arg


def generate_function(ctx: Context) -> ast.FunctionDef:
    f = ast.FunctionDef()
    f.args = ast.arguments()
    f.args.args = [generate_arg(ctx) for _ in range(randint(ctx, 0, 10))]
    f.args.posonlyargs = []
    f.args.kwonlyargs = []
    f.args.defaults = []
    f.name = make_name(ctx, new=True)
    with ctx.nested():
        f.body = generate_stmts(ctx)
    f.decorator_list = []
    f.lineno = 1
    return f


def generate_asyncfunction(ctx: Context) -> ast.AsyncFunctionDef:
    f = ast.AsyncFunctionDef()
    f.args = ast.arguments()
    f.args.args = [generate_arg(ctx) for _ in range(randint(ctx, 0, 10))]
    f.args.posonlyargs = []
    f.args.kwonlyargs = []
    f.args.defaults = []
    f.name = make_name(ctx, new=True)
    with ctx.nested():
        f.body = generate_stmts(ctx)
    f.decorator_list = []  # TODO: Add decorators
    f.lineno = 1
    return f


def generate_class(ctx: Context) -> ast.ClassDef:
    c = ast.ClassDef()
    c.name = make_name(ctx, new=True)
    c.bases = []  # TODO: Add bases
    c.keywords = []
    with ctx.nested():
        c.body = generate_stmts(ctx)
    c.decorator_list = []  # TODO : Add decorators
    c.lineno = 1
    return c


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
    asgn.targets = [
        generate_name(ctx, new=True)
    ]  # TODO: vary number of assignment targets
    asgn.value = generate_expr(ctx)
    return asgn


def generate_augassign(ctx: Context) -> ast.AugAssign:
    asgn = ast.AugAssign()
    asgn.lineno = 1
    asgn.target = generate_name(ctx, new=True)
    asgn.value = generate_expr(ctx)
    asgn.op = randchoice(ctx, OPERATORS)()
    return asgn


def generate_annassign(ctx: Context) -> ast.AnnAssign:
    asgn = ast.AnnAssign()
    asgn.lineno = 1
    asgn.target = generate_name(ctx, new=True)
    asgn.value = generate_expr(ctx)
    asgn.simple = 1  # TODO : Work out what this is
    asgn.annotation = generate_expr(ctx)
    return asgn


def generate_import(ctx: Context) -> ast.Import:
    im = ast.Import()
    im.names = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        alias = ast.alias()
        alias.name = make_name(ctx)
        if randbool(ctx):
            alias.asname = make_name(ctx, new=True)

        im.names.append(alias)
    return im


def generate_importfrom(ctx: Context) -> ast.ImportFrom:
    im = ast.ImportFrom()
    im.module = make_name(ctx)
    im.names = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        alias = ast.alias()
        alias.name = make_name(ctx)
        if randbool(ctx):
            alias.asname = make_name(ctx, new=True)

        im.names.append(alias)
    return im


def generate_name(ctx: Context, new: bool = False) -> ast.Name:
    name = ast.Name()
    name.id = make_name(ctx, new=new)
    # TODO: Add type info
    return name


def generate_constant(ctx: Context, values_only=False) -> ast.Constant:
    c = ast.Constant()
    values = [None, str(), bytes(), bool(), int(), float(), complex()]
    if not values_only:
        values.append(Ellipsis)
    c.value = randchoice(ctx, values)
    return c


def generate_return(ctx: Context) -> ast.Return:
    r = ast.Return()
    if randbool(ctx):
        r.value = generate_expr(ctx)
    return r


def generate_delete(ctx: Context) -> ast.Delete:
    d = ast.Delete()
    # TODO : Is expr, but jst doing name
    d.targets = [generate_name(ctx)]  # TODO: Vary targets
    return d


def generate_raise(ctx: Context) -> ast.Raise:
    r = ast.Raise()
    r.exc = generate_expr(ctx)
    return r


def generate_global(ctx: Context) -> ast.Global:
    g = ast.Global()
    g.names = [make_name(ctx)]  # TODO: Vary length
    return g


def generate_nonlocal(ctx: Context) -> ast.Nonlocal:
    n = ast.Nonlocal()
    n.names = [make_name(ctx)]  # TODO: Vary length
    return n


def generate_for(ctx: Context) -> ast.For:
    f = ast.For()
    f.target = generate_name(ctx, new=True)  # Can be expr, but just doing name
    f.iter = generate_expr(ctx)
    f.lineno = 1
    with ctx.nested():
        f.body = generate_stmts(ctx)
    if randbool(ctx):
        with ctx.nested():
            f.orelse = generate_stmts(ctx)
    else:
        f.orelse = []  # TODO: Raise bug report about this?
    return f


def generate_asyncfor(ctx: Context) -> ast.AsyncFor:
    f = ast.AsyncFor()
    f.target = generate_name(ctx, new=True)
    f.iter = generate_expr(ctx)
    f.lineno = 1
    with ctx.nested():
        f.body = generate_stmts(ctx)
    if randbool(ctx):
        with ctx.nested():
            f.orelse = generate_stmts(ctx)
    else:
        f.orelse = []
    return f


def generate_while(ctx: Context) -> ast.While:
    w = ast.While()
    w.test = generate_expr(ctx)
    w.lineno = 1
    with ctx.nested():
        w.body = generate_stmts(ctx)
    if randbool(ctx):
        with ctx.nested():
            w.orelse = generate_stmts(ctx)
    else:
        w.orelse = []
    return w


def generate_if(ctx: Context) -> ast.If:
    i = ast.If()
    i.test = generate_expr(ctx)
    i.lineno = 1
    with ctx.nested():
        i.body = generate_stmts(ctx)
    if randbool(ctx):
        with ctx.nested():
            i.orelse = generate_stmts(ctx)
    else:
        i.orelse = []
    return i


def generate_with(ctx: Context) -> ast.With:
    w = ast.With()
    w.lineno = 1
    w.items = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        withitem = ast.withitem()
        withitem.context_expr = generate_expr(ctx)
        if randbool(ctx):
            withitem.optional_vars = generate_name(
                ctx, new=True
            )  # TODO : Can be expr, but just doing name
        w.items.append(withitem)
    with ctx.nested():
        w.body = generate_stmts(ctx)
    return w


def generate_asyncwith(ctx: Context) -> ast.AsyncWith:
    w = ast.AsyncWith()
    w.lineno = 1
    w.items = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        withitem = ast.withitem()
        withitem.context_expr = generate_expr(ctx)
        if randbool(ctx):
            withitem.optional_vars = generate_name(
                ctx, new=True
            )  # TODO : Can be expr, but just doing name
        w.items.append(withitem)
    with ctx.nested():
        w.body = generate_stmts(ctx)
    return w


def generate_assert(ctx: Context) -> ast.Assert:
    a = ast.Assert()
    a.test = generate_expr(ctx)
    if randbool(ctx):
        a.msg = generate_expr(ctx)
    return a


def generate_expression(ctx: Context) -> ast.Expr:
    e = ast.Expr()
    e.value = generate_expr(ctx)
    return e


def generate_try(ctx: Context) -> ast.Try:
    t = ast.Try()
    t.lineno = 1
    with ctx.nested():
        t.body = generate_stmts(ctx)
    t.handlers = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        handler = ast.ExceptHandler()
        handler.lineno = 1
        handler.type = generate_expr(ctx)
        if randbool(ctx):
            handler.name = make_name(ctx, new=True)
        with ctx.nested():
            handler.body = generate_stmts(ctx)
        t.handlers.append(handler)
    if randbool(ctx):
        with ctx.nested():
            t.orelse = generate_stmts(ctx)
    else:
        t.orelse = []
    if randbool(ctx):
        with ctx.nested():
            t.finalbody = generate_stmts(ctx)
    else:
        t.finalbody = []
    return t


def generate_literal_pattern(ctx: Context) -> ast.Constant:
    return generate_constant(ctx, values_only=True)


def generate_capture_pattern(ctx: Context) -> ast.Name:
    name = generate_name(ctx, new=True)  # Must not start with _ but doesnt anyway
    return name


def generate_wildcard_pattern(ctx: Context) -> ast.Name:
    name = ast.Name()
    name.id = "_"
    return name


def generate_value_pattern(ctx: Context) -> ast.Name:
    name = ast.Name()
    name1 = make_name(ctx, new=True)
    name2 = make_name(ctx, new=True)
    name.id = f"{name1}.{name2}"  # TODO : Vary length and depth
    return name


CLOSED_PATTERNS = [
    generate_literal_pattern,
    generate_capture_pattern,
    generate_wildcard_pattern,
    generate_value_pattern,
    # TODO...
    # group_pattern
    # sequence_pattern
    # mapping_pattern
    # class_pattern
]


def generate_closed_pattern(ctx: Context) -> typing.Union[ast.pattern, ast.Constant]:
    return randchoice(ctx, CLOSED_PATTERNS)(ctx)


def generate_matchvalue(ctx: Context) -> ast.MatchValue:
    m = ast.MatchValue()
    m.value = generate_constant(ctx, values_only=True)
    return m


def generate_matchsingleton(ctx: Context) -> ast.MatchSingleton:
    m = ast.MatchSingleton()
    m.value = randchoice(ctx, [None, True, False])
    return m


def generate_matchstar(ctx: Context) -> ast.MatchStar:
    m = ast.MatchStar()
    if randbool(ctx):
        m.name = make_name(ctx)
    return m


MATCH_CONST_GENERATORS = [
    generate_matchvalue,
    generate_matchsingleton,
]


def generate_matchsequence(ctx: Context) -> ast.MatchSequence:
    m = ast.MatchSequence()
    m.patterns = [
        randchoice(ctx, MATCH_CONST_GENERATORS)(ctx)
        for _ in range(randint(ctx, 1, 3))  # TODO: Vary length
    ]
    if randbool(ctx):
        m.patterns.append(generate_matchstar(ctx))
    return m


def generate_matchmapping(ctx: Context) -> ast.MatchMapping:
    m = ast.MatchMapping()
    m.keys = []
    m.patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        with ctx.nested():
            m.keys.append(
                generate_constant(ctx, values_only=True)
            )  # TODO: Handle value_pattern tokens
            m.patterns.append(
                randchoice(
                    ctx,
                    [
                        generate_matchvalue,
                        generate_matchsingleton,
                    ],
                )(ctx)
            )
    if randbool(ctx):
        m.rest = make_name(ctx)
    return m


def generate_matchclass(ctx: Context) -> ast.MatchClass:
    m = ast.MatchClass()
    m.cls = generate_name(ctx)  # TODO: Can be expr in ASDL but not in reality
    m.patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        with ctx.nested():
            m.patterns.append(randchoice(ctx, MATCH_CONST_GENERATORS)(ctx))
    m.kwd_attrs = []
    m.kwd_patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        with ctx.nested():
            m.kwd_attrs.append(make_name(ctx))
            m.kwd_patterns.append(randchoice(ctx, MATCH_CONST_GENERATORS)(ctx))
    return m


def generate_matchas(ctx: Context) -> ast.MatchAs:
    m = ast.MatchAs()
    if randbool(ctx):
        m.pattern = randchoice(ctx, CLOSED_PATTERNS)(ctx)
    if randbool(ctx):
        m.name = make_name(ctx, new=True)
    return m


def generate_matchor(ctx: Context) -> ast.MatchOr:
    m = ast.MatchOr()
    m.patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        m.patterns.append(randchoice(ctx, CLOSED_PATTERNS)(ctx))
    return m


MATCH_GENERATORS = [
    generate_matchvalue,
    generate_matchsingleton,
    generate_matchsequence,
    generate_matchmapping,
    generate_matchclass,
    # generate_matchstar,
    generate_matchas,
    generate_matchor,
]


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
    return randchoice(ctx, MATCH_GENERATORS)(ctx)


def generate_match(ctx: Context) -> ast.Match:
    m = ast.Match()
    m.subject = generate_expr(ctx)
    m.cases = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        case = ast.match_case()
        case.pattern = generate_matchpattern(ctx)
        if randbool(ctx):
            case.guard = generate_expr(ctx)
        with ctx.nested():
            case.body = generate_stmts(ctx)
        m.cases.append(case)
    return m


STMT_GENERATORS = (
    generate_function,
    generate_asyncfunction,
    generate_class,
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
    generate_match,
    generate_raise,
    generate_try,
    # generate_trystar, # TODO
    generate_assert,
    generate_import,
    generate_importfrom,
    generate_global,
    generate_nonlocal,
    generate_expression,
    generate_pass,
    generate_break,
    generate_continue,
    # generate_ellipsis, # This causes chaos
)


def generate_list(ctx: Context) -> ast.List:
    l = ast.List()
    with ctx.nested():
        l.elts = generate_exprs(ctx)
    if randbool(ctx):
        l.ctx = randchoice(ctx, [ast.Load, ast.Store, ast.Del])()
    return l


def generate_tuple(ctx: Context) -> ast.Tuple:
    t = ast.Tuple()
    with ctx.nested():
        t.elts = generate_exprs(ctx)
    return t


def generate_boolop(ctx: Context) -> ast.BoolOp:
    b = ast.BoolOp()
    b.values = [generate_expr(ctx)]  # TODO Vary length
    b.op = randchoice(ctx, [ast.And, ast.Or])()
    return b


def generate_binop(ctx: Context) -> ast.BinOp:
    b = ast.BinOp()
    b.left = generate_expr(ctx)
    b.right = generate_expr(ctx)
    b.op = randchoice(ctx, OPERATORS)()
    return b


def generate_unaryop(ctx: Context) -> ast.UnaryOp:
    u = ast.UnaryOp()
    u.operand = generate_expr(ctx)
    u.op = randchoice(ctx, [ast.Invert, ast.Not, ast.UAdd, ast.USub])()
    return u


def generate_lambda(ctx: Context) -> ast.Lambda:
    l = ast.Lambda()
    l.args = ast.arguments()
    l.args.args = [generate_arg(ctx) for _ in range(randint(ctx, 0, 10))]
    l.args.posonlyargs = []
    l.args.kwonlyargs = []
    l.args.defaults = []
    with ctx.nested():
        l.body = generate_expr(ctx)
    return l


def generate_ifexp(ctx: Context) -> ast.IfExp:
    i = ast.IfExp()
    i.test = generate_expr(ctx)
    i.body = generate_expr(ctx)
    i.orelse = generate_expr(ctx)
    return i


def generate_dict(ctx: Context) -> ast.Dict:
    d = ast.Dict()
    with ctx.nested():
        d.keys = generate_exprs(ctx)
        d.values = generate_exprs(ctx)
    return d


def generate_set(ctx: Context) -> ast.Set:
    s = ast.Set()
    with ctx.nested():
        s.elts = generate_exprs(ctx)
    return s


EXPR_GENERATORS = (
    generate_boolop,
    # generate_namedexpr,
    generate_binop,
    generate_unaryop,
    generate_lambda,
    generate_ifexp,
    generate_dict,
    generate_set,
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
    generate_list,
    generate_tuple,
    # generate_slice,
)


def generate_stmts(ctx: Context) -> list[ast.stmt]:
    if ctx.depth >= ctx.max_depth:
        return [generate_pass(ctx)]

    return [randchoice(ctx, STMT_GENERATORS)(ctx) for _ in range(ctx.width)]


def generate_expr(ctx: Context) -> ast.expr:
    return randchoice(ctx, EXPR_GENERATORS)(ctx)


def generate_exprs(ctx: Context) -> list[ast.expr]:
    if ctx.depth >= ctx.max_depth:
        return []
    return [generate_expr(ctx) for _ in range(randint(ctx, 1, ctx.width))]


def generate_module(depth: int, width: int) -> ast.Module:
    ctx = Context()
    ctx.max_depth = depth
    ctx.width = width
    mod = ast.Module()
    mod.type_ignores = []
    with ctx.nested():
        mod.body = generate_stmts(ctx)
    return mod
