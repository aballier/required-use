#!/usr/bin/env python

import sys

from parser import (parse_string, Flag, Implication, NaryOperator,
        AnyOfOperator, ExactlyOneOfOperator, AtMostOneOfOperator)


def nested_negations(constraint, final_constraint):
    return Implication([v.negated() for v in constraint], final_constraint)


def replace_nary(ast):
    for expr in ast:
        if isinstance(expr, Flag):
            yield expr
        elif isinstance(expr, Implication):
            yield Implication(expr.condition, list(replace_nary(expr.constraint)))
        elif isinstance(expr, NaryOperator):
            # replace subexpressions first, if any
            constraint = list(replace_nary(expr.constraint))
            for subexpr in constraint:
                if not isinstance(subexpr, Flag):
                    raise NotImplementedError('Nested operators not supported')
            # then replace the expression itself
            if isinstance(expr, AnyOfOperator) or isinstance(expr, ExactlyOneOfOperator):
                # || ( a b c ... ) -> !a? !b? ( !c? ( ...? ( a ) ) )
                # ^^ ( a b c ... ) -> || ( a b c ... ) ?? ( a b c ... )
                yield nested_negations(constraint[0:], [constraint[0]])
            if isinstance(expr, AtMostOneOfOperator) or isinstance(expr, ExactlyOneOfOperator):
                # ?? ( a b c ... ) -> a? ( !b !c ... ) !a? b? ( !c ... ) ...
                # ^^ ( a b c ... ) -> || ( a b c ... ) ?? ( a b c ... )
                o = []
                while len(constraint) > 1:
                    k = constraint.pop(0)
                    l = o + [k]
                    yield Implication(l, [f.negated() for f in constraint])
                    o = o + [k.negated()]


def sort_nary(ast, sort_key):
    for expr in ast:
        if isinstance(expr, Flag):
            yield expr
        elif isinstance(expr, Implication):
            yield Implication(expr.condition, list(sort_nary(expr.constraint, sort_key)))
        elif isinstance(expr, NaryOperator):
            # sort subexpressions first, if any
            constraint = list(sort_nary(expr.constraint, sort_key))
            constraint.sort(key=sort_key)
            yield expr.__class__(constraint)


if __name__ == '__main__':
    print(repr(list(replace_nary(parse_string(sys.argv[1])))))
