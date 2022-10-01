from scheme_eval_apply import scheme_eval
from scheme_utils import *
from scheme_classes import *
from scheme_builtins import *

#################
# Special Forms #
#################

"""
How you implement special forms is up to you. We recommend you encapsulate the
logic for each special form separately somehow, which you can do here.
"""

# BEGIN PROBLEM 2/3
SPECIALS = dict()


def special(*names):
    """An annotation to convert a Python function into a BuiltinProcedure."""
    def add(py_func):
        for name in names:
            SPECIALS[name] = py_func
        return py_func
    return add

@special("define")
def scheme_define(expr_rest, env):
    args = expr_rest
    symbol = args.first
    if scheme_listp(symbol): # this is a user-defined procedure
        formals = symbol.rest
        symbol = symbol.first
        val = scheme_eval(Pair("lambda", Pair(formals, args.rest)), env)
    elif not scheme_symbolp(symbol):
        raise SchemeError(f"non-symbol: {symbol}")
    else: # this is a user-defined value
        validate_form(args.rest, 1, 1)
        val = scheme_eval(args.rest.first, env)
    env.define(symbol, val)
    return symbol

@special("quote")
def scheme_quote(expr_rest, env):
    validate_form(expr_rest, 1, 1)
    return expr_rest.first

@special("begin")
def scheme_begin(expr_rest, env):
    if expr_rest is not nil:
        sub_expr = expr_rest
        while sub_expr is not nil:
            value = scheme_eval(sub_expr.first, env, sub_expr.rest is nil)
            sub_expr = sub_expr.rest
        return value

@special("lambda")
def scheme_lambda(expr_rest, env):
    formals = expr_rest.first
    body = expr_rest.rest
    validate_formals(formals)
    if body is nil:
        raise SchemeError("too few operands in form")
    return LambdaProcedure(formals, body, env)

@special("and")
def scheme_and(expr_rest, env):
    if expr_rest is nil:
        return True
    sub_expr = expr_rest
    while sub_expr.rest is not nil:
        value = scheme_eval(sub_expr.first, env)
        if is_scheme_false(value):
            return value
        sub_expr = sub_expr.rest
    return scheme_eval(sub_expr.first, env, True)

@special("or")
def scheme_or(expr_rest, env):
    if expr_rest is nil:
        return False
    sub_expr = expr_rest
    while sub_expr.rest is not nil:
        value = scheme_eval(sub_expr.first, env)
        if is_scheme_true(value):
            return value
        sub_expr = sub_expr.rest
    return scheme_eval(sub_expr.first, env, True)

@special("if")
def scheme_if(expr_rest, env):
    validate_form(expr_rest, 2, 3)
    predicate = scheme_eval(expr_rest.first, env)
    consequent = expr_rest.rest.first
    if is_scheme_true(predicate):
        return scheme_eval(consequent, env, True)
    if expr_rest.rest.rest is not nil:
        return scheme_eval(expr_rest.rest.rest.first, env, True)

@special("cond")
def scheme_cond(expr_rest, env):
    while expr_rest is not nil:
        clause = expr_rest.first
        test = True if clause.first == "else" else scheme_eval(clause.first, env)
        if is_scheme_true(test):
            if clause.rest is nil:
                return test
            else:
                return scheme_eval(Pair("begin", clause.rest), env, True)
        expr_rest = expr_rest.rest

@special("let")
def scheme_let(expr_rest, env):
    validate_form(expr_rest, 2)
    bindings = expr_rest.first # for example: ((x 4) (y 5))
    body = expr_rest.rest
    new_frame = Frame(env)
    while bindings is not nil:
        if not scheme_listp(bindings.first):
            raise SchemeError(f"badly formed expression: {bindings.first}")
        validate_form(bindings.first, 2, 2)
        if not scheme_symbolp(bindings.first.first):
            raise SchemeError(f"non-symbol: {bindings.first.first}")
        new_frame.define(bindings.first.first, scheme_eval(bindings.first.rest.first, env))
        bindings = bindings.rest
    return scheme_eval(Pair("begin", body), new_frame, True)

@special("mu")
def scheme_mu(expr_rest, env):
    formals = expr_rest.first
    body = expr_rest.rest
    validate_formals(formals)
    if body is nil:
        raise SchemeError("too few operands in form")
    return MuProcedure(formals, body)
# END PROBLEM 2/3
