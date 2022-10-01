import sys
import os

from pair import *
from scheme_utils import *
from ucb import main, trace

import scheme_forms

##############
# Eval/Apply #
##############


def scheme_eval(expr, env, tail=False):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # BEGIN Problem 1/2
    if self_evaluating(expr):
        return expr
    if scheme_symbolp(expr):
        value = env.lookup(expr)
        # assert self_evaluating(value) or scheme_procedurep(value) or scheme_listp(value), value
        return value

    if not isinstance(expr, Pair):
        raise SchemeError(f"unknown identifier: {expr}")

    if tail:
        return Unevaluated(expr, env)

    result = Unevaluated(expr, env)
    while isinstance(result, Unevaluated):
        if isinstance(result.expr.first, str) and result.expr.first in scheme_forms.SPECIALS:
            result = scheme_forms.SPECIALS[result.expr.first](result.expr.rest, result.env)
        else:
            expr = result.expr.map(lambda e: scheme_eval(e, result.env))
            validate_procedure(expr.first) # Now first is a procedure. Then we need to get its argument(s).
            result = scheme_apply(expr.first, expr.rest, result.env)
    return result
    # END Problem 1/2


def scheme_apply(procedure, args, env):
    """
    Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment.
    Input: 
        - procedure: an instance of Procedure
        - args: a Scheme list (linked Pair) of arguments of procedure
    """
    # BEGIN Problem 1/2
    try:
        if isinstance(procedure, BuiltinProcedure):
            args_list = []
            while args is not nil:
                args_list.append(args.first)
                args = args.rest
            if procedure.need_env:
                args_list.append(env)
            return procedure.py_func(*args_list)
        elif isinstance(procedure, LambdaProcedure):
            current_frame = Frame(procedure.env)
            formals = procedure.formals
            while formals is not nil:
                if args is nil:
                    raise SchemeError("too few operands in form")
                current_frame.define(formals.first, args.first)
                formals = formals.rest
                args = args.rest
            if args is not nil:
                raise SchemeError("too many operands in form")
            return scheme_eval(Pair("begin", procedure.body), current_frame, True)
        elif isinstance(procedure, MuProcedure):
            current_frame = Frame(env)
            formals = procedure.formals
            while formals is not nil:
                if args.first is nil:
                    raise SchemeError("too few operands in form")
                current_frame.define(formals.first, args.first)
                formals = formals.rest
                args = args.rest
            if args is not nil:
                raise SchemeError("too many operands in form")
            return scheme_eval(Pair("begin", procedure.body), current_frame)
        else:
            raise NotImplementedError   
            
    except Exception as e:
        print(e)
        raise SchemeError(e)
    # END Problem 1/2


##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here!
# BEGIN Problem EC 1
class Unevaluated:
    def __init__(self, expr, env) -> None:
        self.expr = expr
        self.env = env
# END Problem EC 1


def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not Unevaluated.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    validate_procedure(procedure)
    # BEGIN
    result = scheme_apply(procedure, args, env)
    if isinstance(result, Unevaluated):
        result = scheme_eval(result.expr, result.env)
    return result
    # END
