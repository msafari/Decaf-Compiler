from Expr import *
from ast.ast_helpers import *
from ast.Type import *

class BinaryExpr(Expr):
    def __init__(self, bop, arg1, arg2, lines):
        self.lines = lines
        self.bop = bop
        self.arg1 = arg1
        self.arg2 = arg2
        self.__typeof = None
    def __repr__(self):
        return "Binary({0}, {1}, {2})".format(self.bop,self.arg1,self.arg2)            

    def typeof(self):
        if (self.__typeof == None):
            arg1type = self.arg1.typeof()
            arg2type = self.arg2.typeof()
            self.__typeof = Type('error')
            if (self.bop in ['add', 'sub', 'mul', 'div']):
                if (arg1type.isint()) and (arg2type.isint()):
                    self.__typeof = arg1type
                elif (arg1type.isnumeric()) and (arg2type.isnumeric()): 
                    self.__typeof = Type('float')
                else:
                    if (arg1type.isok() and arg2type.isok()):
                        signal_bop_error('first', self.bop, arg1type, self.arg1,
                                         ['int', 'float'], 'int/float')
                        signal_bop_error('second', self.bop, arg2type, self.arg2,
                                         ['int', 'float'], 'int/float')
                    
            elif (self.bop in ['lt', 'leq', 'gt', 'geq']):
                if ((arg1type.isnumeric()) and (arg2type.isnumeric())): 
                    self.__typeof = Type('boolean')
                else:
                    if (arg1type.isok() and arg2type.isok()):
                        signal_bop_error('first', self.bop, arg1type, self.arg1,
                                         ['int', 'float'], 'int/float')
                        signal_bop_error('second', self.bop, arg2type, self.arg2,
                                         ['int', 'float'], 'int/float')
                    
            elif (self.bop in ['and', 'or']):
                if ((arg1type.isboolean()) and (arg2type.isboolean())):
                    self.__typeof = Type('boolean')
                else:
                    if (arg1type.isok() and arg2type.isok()):
                        signal_bop_error('first', self.bop, arg1type, self.arg1,
                                         ['boolean'], 'boolean')
                        signal_bop_error('second', self.bop, arg2type, self.arg2,
                                         ['boolean'], 'boolean')
            else:
                # equality/disequality
                if ((arg1type.isok()) and (arg2type.isok())):
                    if ((arg1type.is_subtype_of(arg2type)) or (arg2type.is_subtype_of(arg1type))):
                        self.__typeof = Type('boolean')
                    else:
                        signal_type_error('Type error in arguments of binary {0} expression: compatible types expected, found {1} and {2}'.format(self.bop, str(arg1type), str(arg2type)), self.lines)
                       
        return self.__typeof
