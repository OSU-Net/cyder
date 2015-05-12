from itertools import izip

from parsley import wrapGrammar
from ometa.runtime import ParseError

from cyder.search.compiler.dsl import ICompiler
from cyder.search.compiler.invfilter import (
    BadDirective, DirectiveFilter, MacAddressFilter, REFilter, searchables,
    TextFilter)


def compile_to_django(search):
    search = search.strip()
    compiled_qs, error = compile_q_objects(search)
    if error:
        return None, error
    return qs_to_object_map(compiled_qs), ""


def search_type(search, rdtype):
    """A simple wrapper for returning an rdtypes queryset"""
    obj_map, error = compile_to_django(search)
    if error:
        return None, error
    return obj_map[rdtype], None


def qs_to_object_map(qs):
    obj_map = {}
    for q, (type_, Klass) in izip(qs, searchables):
        if not q:
            obj_map[type_] = []
        else:
            obj_map[type_] = Klass.objects.filter(q)
    obj_map['misc'] = []
    return obj_map


def compile_q_objects(search):
    compiler = wrapGrammar(DjangoCompiler)
    try:
        qs = compiler(search).expr()
        return qs, None
    except (BadDirective, ParseError) as why:
        return None, why.formatReason()


class DjangoCompiler(ICompiler):
    # directive, regexpr, and text all return a list of Qsets

    def directive(self, directive, value):
        return DirectiveFilter(directive, value).compile_Q()

    def mac_addr(self, addr):
        return MacAddressFilter(addr).compile_Q()

    def regexpr(self, reg_expr):
        return REFilter(reg_expr).compile_Q()

    def text(self, text):
        return TextFilter(text).compile_Q()

    def compile(self, initial, values):
        ret = initial
        for op, value in values:
            ret = map(lambda args: op(*args), izip(ret, value))
        return ret

    def OR_op(self):
        def OR(q, p):
            if q and p:
                return q | p
            return q or p or None
        return OR

    def AND_op(self, *args):
        def AND(q, p):
            if q and p:
                return q & p
            # Something AND nothing is nothing
            return None
        return AND

    def NOT_op(self):
        def NOT(t):
            return map(lambda Q: ~Q, t)
        return NOT
