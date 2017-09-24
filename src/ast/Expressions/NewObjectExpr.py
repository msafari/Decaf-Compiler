from Expr import *
from ast.ast_helpers import *
from ast.Type import *
from ast.Class import *
import ast.Config as Config

class NewObjectExpr(Expr):
    def __init__(self, cref, args, lines):
        self.lines = lines
        self.classref = cref
        self.args = args
        self.__typeof = None
        self.objID = None
    def __repr__(self):
        return "New-object({0}, {1})".format(self.classref.name, self.args)

    def typeof(self):
        if (self.__typeof == None):
            # resolve the constructor name first
            argtypes = [a.typeof() for a in self.args]
            if (all([a.isok() for a in argtypes])):
                j = resolve_constructor(Config.current_class, self.classref, argtypes, self.lines)
                if (j == None):
                    self.__typeof = Type('error')
                else:
                    self.constructor = j
                    self.__typeof = Type(self.classref)
            else:
                # type error in some argument; already signaled before
                self.__typeof = Type('error')
        return self.__typeof