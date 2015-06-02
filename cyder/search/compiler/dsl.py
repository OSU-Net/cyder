from os import path

from ometa.grammar import OMeta
from ometa.runtime import OMetaBase
from parsley import wrapGrammar

from activate import cy_path


with open(cy_path('cyder/search/compiler/search.parsley')) as g:
    B = OMeta.makeGrammar(g.read()).createParserClass(OMetaBase, globals())


class ICompiler(B):
    def directive(self, d, v):
        raise NotImplemented()

    def mac_addr(self, addr):
        raise NotImplemented()

    def regexpr(self, r):
        raise NotImplemented()

    def text(self, t):
        raise NotImplemented()

    def compile(self, initial, values):
        raise NotImplemented()

    def OR_op(self, a, b):
        raise NotImplemented()

    def AND_op(self, a, b):
        raise NotImplemented()

    def NOT_op(self, a):
        raise NotImplemented()


class DebugCompiler(ICompiler):
    def directive(self, d, v):
        return d, v

    def mac_addr(self, addr):
        return '[' + addr + ']'

    def regexpr(self, r):
        return r

    def text(self, t):
        return t

    def compile(self, initial, values):
        ret = initial
        for op, value in values:
            ret = op(ret, value)
        return ret

    def OR_op(self):
        return lambda a, b: '({} OR {})'.format(a, b)

    def AND_op(self):
        return lambda a, b: '({} AND {})'.format(a, b)

    def NOT_op(self):
        return lambda a: '(NOT {})'.format(a)


def make_debug_compiler():
    return wrapGrammar(DebugCompiler)
