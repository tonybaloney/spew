import ast
import random as _random
import sys
from contextlib import contextmanager
import typing
from spew.names import generate as make_name
import logging
import enum
from spew.randomcycle import rcycle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_DEPTH = 3
DEFAULT_WIDTH = 20


class GeneratorConstraints(enum.Flag):
    ANY = enum.auto()
    ONLY_IN_LOOPS = enum.auto()
    ONLY_IN_FUNCTIONS = enum.auto()


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
CMPOPS = [
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Is,
    ast.IsNot,
    ast.In,
    ast.NotIn,
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
        self.in_function = False
        self.names = []

    @contextmanager
    def nested(self):
        if self.depth + 1 > self.max_depth:
            logger.debug("Max depth exceeded", stack_info=True)
        self.depth += 1
        yield
        self.depth -= 1

    @contextmanager
    def inloop(self):
        _prev_state = self.in_loop
        self.in_loop = True
        yield
        self.in_loop = _prev_state

    @contextmanager
    def infunction(self):
        _prev_state = self.in_function
        self.in_function = True
        yield
        self.in_function = _prev_state


def make_text(ctx: Context) -> str:
    return make_name(ctx, new=True)  # TODO : Do better


boolcycle = rcycle([True, False])


def randbool(ctx: Context) -> bool:
    return next(boolcycle)


T = typing.TypeVar("T")


def randchoice(ctx: Context, choices: typing.Sequence[T]) -> T:
    return _random.choice(choices)


def randint(ctx: Context, a: int, b: int) -> int:
    # TODO: Use context for reproducible results
    return _random.randint(a, b)


def generate_arg(ctx: Context, allow_annotations=False) -> ast.arg:
    arg = ast.arg()
    arg.arg = make_name(ctx, new=True)
    if randbool(ctx) and allow_annotations:
        arg.annotation = generate_name(ctx)
    return arg


TFunc = typing.TypeVar("TFunc", ast.FunctionDef, ast.AsyncFunctionDef)


def _generate_function(f: TFunc, ctx: Context) -> TFunc:
    f.args = ast.arguments()
    n_args = randint(ctx, 0, ctx.width)
    f.args.args = [generate_arg(ctx, True) for _ in range(n_args)]
    f.args.posonlyargs = []
    f.args.kwonlyargs = []
    if randbool(ctx):
        f.args.defaults = [
            generate_constant(ctx, values_only=True) for _ in range(n_args)
        ]
    else:
        f.args.defaults = []
    f.name = make_name(ctx, new=True)
    with ctx.infunction():
        f.body = generate_nested_stmts(ctx)
    if randbool(ctx):
        f.decorator_list = []
    else:
        f.decorator_list = [
            generate_expr(ctx) for _ in range(randint(ctx, 1, 3))
        ]  # TODO: vary length
    f.lineno = 1
    return f


def generate_function(ctx: Context) -> ast.FunctionDef:
    f = ast.FunctionDef()
    return _generate_function(f, ctx)


def generate_asyncfunction(ctx: Context) -> ast.AsyncFunctionDef:
    f = ast.AsyncFunctionDef()
    return _generate_function(f, ctx)


def generate_class(ctx: Context) -> ast.ClassDef:
    c = ast.ClassDef()
    c.name = make_name(ctx, new=True)
    if randbool(ctx):  # 50/50 chance of no bases
        c.bases = []
    else:
        c.bases = [generate_expr(ctx) for _ in range(randint(ctx, 0, 3))]
    c.keywords = []
    c.body = generate_nested_stmts(ctx)
    if randbool(ctx):  # 50/50 chance of no decorator list
        c.decorator_list = []
    else:
        c.decorator_list = [
            generate_expr(ctx) for _ in range(randint(ctx, 1, ctx.width))
        ]
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


gen_cycle = rcycle([ast.Load, ast.Store, ast.Del])


def generate_attribute(ctx: Context) -> ast.Attribute:
    a = ast.Attribute()
    a.value = generate_expr(ctx)
    a.attr = make_name(ctx)
    a.ctx = next(gen_cycle)()
    return a


generate_subscript_ctx = rcycle([ast.Load, ast.Store, ast.Del])


def generate_subscript(ctx: Context) -> ast.Subscript:
    s = ast.Subscript()
    s.value = generate_expr(ctx)
    if randbool(ctx):
        s.slice = generate_constant(ctx)  # TODO : Generate Tuple elts slice
    else:
        s.slice = generate_slice(ctx)
    s.ctx = next(generate_subscript_ctx)()
    return s


def generate_assign(ctx: Context) -> ast.Assign:
    asgn = ast.Assign()
    asgn.lineno = 1
    if randbool(ctx):
        asgn.targets = [generate_name(ctx, new=True)]
    else:
        asgn.targets = [
            generate_name(ctx, new=True) for _ in range(randint(ctx, 1, ctx.width))
        ]
    asgn.value = generate_expr(ctx)
    return asgn


operators_cycle = rcycle(OPERATORS)


def generate_augassign(ctx: Context) -> ast.AugAssign:
    asgn = ast.AugAssign()
    asgn.lineno = 1
    if randbool(ctx):
        asgn.target = generate_name(ctx, new=True)
    else:
        if randbool(ctx):
            asgn.target = generate_attribute(ctx)
        else:
            asgn.target = generate_subscript(ctx)
    asgn.value = generate_expr(ctx)
    asgn.op = next(operators_cycle)()
    return asgn


def generate_annassign(ctx: Context) -> ast.AnnAssign:
    asgn = ast.AnnAssign()
    asgn.lineno = 1
    if randbool(ctx):
        asgn.target = generate_name(ctx, new=True)
    else:
        if randbool(ctx):
            asgn.target = generate_attribute(ctx)
        else:
            asgn.target = generate_subscript(ctx)

    # simple is a boolean integer set to True for a Name node in target
    # that do not appear in between parenthesis and are hence pure names
    # and not expressions.
    if randbool(ctx):
        asgn.simple = 1
        asgn.value = generate_name(ctx)
    else:
        asgn.simple = 0
        # value is a single optional node
        asgn.value = generate_expr(ctx)
    asgn.annotation = generate_expr(ctx)
    return asgn


def generate_import(ctx: Context) -> ast.Import:
    im = ast.Import()
    im.names = []
    for _ in range(randint(ctx, 1, ctx.width)):
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
    for _ in range(randint(ctx, 1, ctx.width)):
        alias = ast.alias()
        alias.name = make_name(ctx)
        if randbool(ctx):
            alias.asname = make_name(ctx, new=True)

        im.names.append(alias)
    return im


def generate_name(ctx: Context, new: bool = False) -> ast.Name:
    name = ast.Name()
    name.id = make_name(ctx, new=new)
    return name


constant_values_cycle = rcycle(
    [None, str(), bytes(), bool(), int(), float(), complex()]
)
constant_values_with_ellipsis_cycle = rcycle(
    [None, str(), bytes(), bool(), int(), float(), complex(), Ellipsis]
)


def generate_constant(ctx: Context, values_only=False) -> ast.Constant:
    c = ast.Constant()
    c.value = next(constant_values_cycle)
    return c


def generate_str_constant(ctx: Context) -> ast.Constant:
    c = ast.Constant()
    c.value = str(make_text(ctx))
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


TFor = typing.TypeVar("TFor", ast.For, ast.AsyncFor)


def _generate_for(ctx: Context, f: TFor) -> TFor:
    # TODO : Set tuple or collection as target
    f.target = generate_name(ctx, new=True)  # Can be expr, but just doing name
    f.iter = generate_expr(ctx)
    f.lineno = 1
    with ctx.inloop():
        f.body = generate_nested_stmts(ctx)
    if randbool(ctx):
        f.orelse = generate_nested_stmts(ctx)
    else:
        f.orelse = []  # TODO: Raise bug report about this?
    return f


def generate_for(ctx: Context) -> ast.For:
    return _generate_for(ctx, ast.For())


def generate_asyncfor(ctx: Context) -> ast.AsyncFor:
    return _generate_for(ctx, ast.AsyncFor())


def generate_while(ctx: Context) -> ast.While:
    w = ast.While()
    w.test = generate_expr(ctx)
    w.lineno = 1
    with ctx.inloop():
        w.body = generate_nested_stmts(ctx)
    if randbool(ctx):
        w.orelse = generate_nested_stmts(ctx)
    else:
        w.orelse = []
    return w


def generate_if(ctx: Context) -> ast.If:
    i = ast.If()
    i.test = generate_expr(ctx)
    i.lineno = 1
    i.body = generate_nested_stmts(ctx)
    if randbool(ctx):
        i.orelse = generate_nested_stmts(ctx)
    else:
        i.orelse = []
    return i


TWith = typing.TypeVar("TWith", ast.With, ast.AsyncWith)


def _generate_with(ctx: Context, w: TWith) -> TWith:
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
    w.body = generate_nested_stmts(ctx)
    return w


def generate_with(ctx: Context) -> ast.With:
    return _generate_with(ctx, ast.With())


def generate_asyncwith(ctx: Context) -> ast.AsyncWith:
    return _generate_with(ctx, ast.AsyncWith())


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


if sys.version_info < (3, 11):
    TTry = typing.TypeVar("TTry")
else:
    TTry = typing.TypeVar("TTry", ast.Try, ast.TryStar)


def _generate_try(ctx: Context, t: TTry) -> TTry:
    t.lineno = 1
    t.body = generate_nested_stmts(ctx)
    t.handlers = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        handler = ast.ExceptHandler()
        handler.lineno = 1
        handler.type = generate_expr(ctx)
        if randbool(ctx):
            handler.name = make_name(ctx, new=True)
        handler.body = generate_nested_stmts(ctx)
        t.handlers.append(handler)
    if randbool(ctx):
        t.orelse = generate_nested_stmts(ctx)
    else:
        t.orelse = []
    if randbool(ctx):
        t.finalbody = generate_nested_stmts(ctx)
    else:
        t.finalbody = []
    return t


def generate_try(ctx: Context) -> ast.Try:
    return _generate_try(ctx, ast.Try())


if sys.version_info > (3, 10):

    def generate_trystar(ctx: Context) -> ast.TryStar:
        return _generate_try(ctx, ast.TryStar())

else:

    def generate_trystar(ctx: Context) -> ast.Try:
        return _generate_try(ctx, ast.Try())


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

closed_patterns_cycle = rcycle(CLOSED_PATTERNS)


def generate_closed_pattern(ctx: Context) -> typing.Union[ast.pattern, ast.Constant]:
    return next(closed_patterns_cycle)(ctx)


def generate_matchvalue(ctx: Context) -> ast.MatchValue:
    m = ast.MatchValue()
    m.value = generate_constant(ctx, values_only=True)
    return m


singleton_cycle = rcycle([None, True, False])


def generate_matchsingleton(ctx: Context) -> ast.MatchSingleton:
    m = ast.MatchSingleton()
    m.value = next(singleton_cycle)
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

match_const_cycle = rcycle(MATCH_CONST_GENERATORS)


def generate_matchsequence(ctx: Context) -> ast.MatchSequence:
    m = ast.MatchSequence()
    m.patterns = [
        next(match_const_cycle)(ctx)
        for _ in range(randint(ctx, 1, 3))  # TODO: Vary length
    ]
    if randbool(ctx):
        m.patterns.append(generate_matchstar(ctx))
    return m


mapping_generator_cycle = rcycle(
    [
        generate_matchvalue,
        generate_matchsingleton,
    ]
)


def generate_matchmapping(ctx: Context) -> ast.MatchMapping:
    m = ast.MatchMapping()
    m.keys = []
    m.patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        with ctx.nested():
            m.keys.append(
                generate_constant(ctx, values_only=True)
            )  # TODO: Handle value_pattern tokens
            m.patterns.append(next(mapping_generator_cycle)(ctx))
    if randbool(ctx):
        m.rest = make_name(ctx)
    return m


def generate_matchclass(ctx: Context) -> ast.MatchClass:
    m = ast.MatchClass()
    m.cls = generate_name(ctx)  # TODO: Can be expr in ASDL but not in reality
    m.patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        with ctx.nested():
            m.patterns.append(next(match_const_cycle)(ctx))
    m.kwd_attrs = []
    m.kwd_patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        with ctx.nested():
            m.kwd_attrs.append(make_name(ctx))
            m.kwd_patterns.append(next(match_const_cycle)(ctx))
    return m


def generate_matchas(ctx: Context) -> ast.MatchAs:
    m = ast.MatchAs()
    if randbool(ctx):
        m.pattern = next(closed_patterns_cycle)(ctx)
    if randbool(ctx):
        m.name = make_name(ctx, new=True)
    return m


def generate_matchor(ctx: Context) -> ast.MatchOr:
    m = ast.MatchOr()
    m.patterns = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        m.patterns.append(next(closed_patterns_cycle)(ctx))
    return m


MATCH_GENERATORS = [
    generate_matchvalue,
    generate_matchsingleton,
    generate_matchsequence,
    generate_matchmapping,
    generate_matchclass,
    # generate_matchstar, # Causes lots of problems with syntax?
    generate_matchas,
    generate_matchor,
]

match_cycle = rcycle(MATCH_GENERATORS)


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
    return next(match_cycle)(ctx)


def generate_match(ctx: Context) -> ast.Match:
    m = ast.Match()
    m.subject = generate_expr(ctx)
    m.cases = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        case = ast.match_case()
        case.pattern = generate_matchpattern(ctx)
        if randbool(ctx):
            case.guard = generate_expr(ctx)
        case.body = generate_nested_stmts(ctx)
        m.cases.append(case)
    return m


# Constraint, is nested, generator
STMT_GENERATORS = (
    (GeneratorConstraints.ANY, False, generate_assign),
    (GeneratorConstraints.ANY, False, generate_augassign),
    (GeneratorConstraints.ANY, False, generate_annassign),
    (GeneratorConstraints.ANY, True, generate_function),
    (GeneratorConstraints.ANY, True, generate_asyncfunction),
    (GeneratorConstraints.ANY, True, generate_class),
    (GeneratorConstraints.ONLY_IN_FUNCTIONS, False, generate_return),
    (GeneratorConstraints.ANY, False, generate_delete),
    (GeneratorConstraints.ANY, True, generate_for),
    (GeneratorConstraints.ANY, True, generate_asyncfor),
    (GeneratorConstraints.ANY, True, generate_while),
    (GeneratorConstraints.ANY, True, generate_if),
    (GeneratorConstraints.ANY, True, generate_with),
    (GeneratorConstraints.ANY, True, generate_asyncwith),
    (GeneratorConstraints.ANY, True, generate_match),
    (GeneratorConstraints.ANY, False, generate_raise),
    (GeneratorConstraints.ANY, True, generate_try),
    (GeneratorConstraints.ANY, True, generate_trystar),
    (GeneratorConstraints.ANY, False, generate_assert),
    (GeneratorConstraints.ANY, False, generate_import),
    (GeneratorConstraints.ANY, False, generate_importfrom),
    (GeneratorConstraints.ANY, False, generate_global),
    (GeneratorConstraints.ONLY_IN_FUNCTIONS, False, generate_nonlocal),
    (GeneratorConstraints.ANY, False, generate_expression),
    (GeneratorConstraints.ANY, False, generate_pass),
    (GeneratorConstraints.ONLY_IN_LOOPS, False, generate_break),
    (GeneratorConstraints.ONLY_IN_LOOPS, False, generate_continue),
    # (GeneratorConstraints.ANY, generate_ellipsis), # This causes chaos
)

list_ctx_cycle = rcycle([ast.Load, ast.Store, ast.Del])


def generate_list(ctx: Context) -> ast.List:
    l = ast.List()
    l.elts = generate_exprs(ctx)
    if randbool(ctx):
        l.ctx = next(list_ctx_cycle)()
    return l


def generate_tuple(ctx: Context) -> ast.Tuple:
    t = ast.Tuple()
    t.elts = generate_exprs(ctx)
    return t


bool_op_cycle = rcycle([ast.And, ast.Or])


def generate_boolop(ctx: Context) -> ast.BoolOp:
    b = ast.BoolOp()
    b.values = [generate_expr(ctx)]  # TODO Vary length
    b.op = next(bool_op_cycle)()
    return b


binop_cycle = rcycle(OPERATORS)


def generate_binop(ctx: Context) -> ast.BinOp:
    b = ast.BinOp()
    b.left = generate_expr(ctx)
    b.right = generate_expr(ctx)
    b.op = next(binop_cycle)()
    return b


unary_cycle = rcycle([ast.Invert, ast.Not, ast.UAdd, ast.USub])


def generate_unaryop(ctx: Context) -> ast.UnaryOp:
    u = ast.UnaryOp()
    u.operand = generate_expr(ctx)
    u.op = next(unary_cycle)()
    return u


def generate_lambda(ctx: Context) -> ast.Lambda:
    l = ast.Lambda()
    l.args = ast.arguments()
    l.args.args = [generate_arg(ctx) for _ in range(randint(ctx, 0, ctx.width))]
    l.args.posonlyargs = []
    l.args.kwonlyargs = []
    l.args.defaults = []
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
    d.keys = generate_exprs(ctx)
    d.values = generate_exprs(ctx)
    return d


def generate_set(ctx: Context) -> ast.Set:
    s = ast.Set()
    s.elts = generate_exprs(ctx)
    return s


def generate_comprehension(ctx: Context) -> ast.comprehension:
    c = ast.comprehension()
    c.target = generate_name(ctx, new=True)
    c.iter = generate_expr(ctx)
    c.ifs = []
    for _ in range(randint(ctx, 0, 3)):  # TODO: Vary length
        c.ifs.append(generate_expr(ctx))
    c.is_async = False  # TODO: Vary?
    return c


def generate_listcomp(ctx: Context) -> ast.ListComp:
    l = ast.ListComp()
    l.elt = generate_expr(ctx)
    l.generators = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        l.generators.append(generate_comprehension(ctx))
    return l


def generate_setcomp(ctx: Context) -> ast.SetComp:
    s = ast.SetComp()
    s.elt = generate_expr(ctx)
    s.generators = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        s.generators.append(generate_comprehension(ctx))
    return s


def generate_dictcomp(ctx: Context) -> ast.DictComp:
    d = ast.DictComp()
    d.key = generate_expr(ctx)
    d.value = generate_expr(ctx)
    d.generators = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        d.generators.append(generate_comprehension(ctx))
    return d


def generate_generatorexp(ctx: Context) -> ast.GeneratorExp:
    g = ast.GeneratorExp()
    g.elt = generate_expr(ctx)
    g.generators = []
    for _ in range(randint(ctx, 1, 3)):  # TODO: Vary length
        g.generators.append(generate_comprehension(ctx))
    return g


def generate_await(ctx: Context) -> ast.Await:
    a = ast.Await()
    a.value = generate_expr(ctx)
    return a


def generate_yield(ctx: Context) -> ast.Yield:
    y = ast.Yield()
    y.value = generate_expr(ctx)
    return y


def generate_yieldfrom(ctx: Context) -> ast.YieldFrom:
    y = ast.YieldFrom()
    y.value = generate_expr(ctx)
    return y


cmpop_cycle = rcycle(CMPOPS)


def generate_compare(ctx: Context) -> ast.Compare:
    c = ast.Compare()
    c.left = generate_expr(ctx)
    c.comparators = [
        generate_expr(ctx) for _ in range(randint(ctx, 1, 3))
    ]  # TODO: Use width or varied length
    c.ops = [
        next(cmpop_cycle)() for _ in range(randint(ctx, 1, 3))
    ]  # TODO: Vary length
    return c


def generate_call(ctx: Context) -> ast.Call:
    c = ast.Call()
    c.func = generate_expr(ctx)
    c.args = []
    for _ in range(randint(ctx, 0, ctx.width // 2)):
        c.args.append(generate_expr(ctx))
    c.keywords = []
    for _ in range(randint(ctx, 0, ctx.width // 2)):
        kw = ast.keyword()
        kw.arg = make_name(ctx, new=True)
        kw.value = generate_expr(ctx)
        c.keywords.append(kw)
    return c


def generate_formattedvalue(ctx: Context) -> ast.FormattedValue:
    f = ast.FormattedValue()
    # Use generate_name when Python < 3.12
    if sys.version_info < (3, 12):
        f.value = generate_name(ctx, new=True)
    else:
        f.value = generate_expr(ctx)
    f.format_spec = None  # TODO : Generate format specs
    f.conversion = -1  # TODO : Work out what this is?
    return f


def generate_joinedstr(ctx: Context) -> ast.JoinedStr:
    j = ast.JoinedStr()
    j.values = [
        randchoice(ctx, [generate_str_constant, generate_formattedvalue])(ctx)
        for _ in range(ctx.width)
    ]
    return j


def generate_namedexpr(ctx: Context) -> ast.NamedExpr:
    n = ast.NamedExpr()
    n.target = generate_name(ctx, new=True)
    n.value = generate_expr(ctx)
    return n


def generate_slice(ctx: Context) -> ast.Slice:
    s = ast.Slice()
    s.lower = generate_expr(ctx)
    s.upper = generate_expr(ctx)
    s.step = generate_expr(ctx)
    return s


EXPR_GENERATORS = (
    generate_boolop,
    generate_namedexpr,
    generate_binop,
    generate_unaryop,
    generate_lambda,
    generate_ifexp,
    generate_dict,
    generate_set,
    generate_listcomp,
    generate_setcomp,
    generate_dictcomp,
    generate_generatorexp,
    generate_await,
    generate_yield,
    generate_yieldfrom,
    generate_compare,
    generate_call,
    generate_formattedvalue,
    generate_joinedstr,
    generate_constant,
    generate_attribute,
    generate_subscript,
    # generate_starred,
    generate_name,
    generate_list,
    generate_tuple,
)

""" Expressions that don't themselves contain expressions. """
FLAT_EXPR_GENERATORS = [
    generate_name,
    generate_constant,
]


# Create another list with the first item in the tuple for each item in STMT_GENERATORS
STMT_ALL_GENERATORS_ITER = rcycle(STMT_GENERATORS)


def _generate_stmts(ctx: Context) -> list[ast.stmt]:
    if ctx.depth >= ctx.max_depth:
        logger.debug("Hit max depth for stmt")
        return [generate_pass(ctx)]
    stmts = []
    while len(stmts) < ctx.width:
        next_stmt = next(STMT_ALL_GENERATORS_ITER)
        if next_stmt[1] and ctx.depth >= ctx.max_depth - 1:
            logger.debug("Hit max depth for nested stmt")
            continue
        if next_stmt[0] == GeneratorConstraints.ANY:
            stmts.append(next_stmt[2](ctx))
        elif next_stmt[0] == GeneratorConstraints.ONLY_IN_FUNCTIONS and ctx.in_function:
            stmts.append(next_stmt[2](ctx))
        elif next_stmt[0] == GeneratorConstraints.ONLY_IN_LOOPS and ctx.in_loop:
            stmts.append(next_stmt[2](ctx))
    return stmts


def generate_nested_stmts(ctx: Context) -> list[ast.stmt]:
    with ctx.nested():
        return _generate_stmts(ctx)


flat_expr_generators_cycle = rcycle(FLAT_EXPR_GENERATORS)
expr_generators_cycle = rcycle(EXPR_GENERATORS)


def generate_expr(ctx: Context) -> ast.expr:
    with ctx.nested():
        if ctx.depth >= ctx.max_depth:
            logger.debug("Hit max depth")
            return next(flat_expr_generators_cycle)(ctx)
        return next(expr_generators_cycle)(ctx)


def generate_exprs(ctx: Context) -> list[ast.expr]:
    if ctx.depth >= ctx.max_depth:
        return []
    return [generate_expr(ctx) for _ in range(randint(ctx, 1, ctx.width))]


def generate_module(depth: int, width: int, log_level: str | None = None) -> ast.Module:
    if log_level is not None:
        logger.setLevel(log_level)
    ctx = Context()
    ctx.max_depth = depth
    ctx.width = width
    mod = ast.Module()
    mod.type_ignores = []
    mod.body = generate_nested_stmts(ctx)
    return mod
