#!/usr/bin/env python

import sys

from parser import (parse_string, Flag, Implication, NaryOperator)
from replace_nary import replace_nary


def nested_implications(conditions, final_constraint):
    val = final_constraint
    for v in reversed(conditions):
        val = Implication(v, [val])
    return val


def flatten_implications(ast, current_implications=[]):
    for expr in ast:
        if isinstance(expr, list):
            yield Implication(current_implications, expr)
        if isinstance(expr, Flag):
            yield Implication(current_implications, [expr])
        elif isinstance(expr, Implication):
            c = current_implications + expr.condition
            for x in flatten_implications(expr.constraint, c):
                yield x
        else:
            raise ValueError('N-ary operators should be replaced already (%s)'%expr)


if __name__ == '__main__':
    print(repr(list(flatten_implications(replace_nary(parse_string(sys.argv[1]))))))
