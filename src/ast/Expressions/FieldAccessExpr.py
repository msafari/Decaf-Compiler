from '../helpers' import ast_helpers 

class FieldAccessExpr(Expr):
    def __init__(self, base, fname, lines):
        self.lines = lines
        self.base = base
        self.fname = fname
        self.__typeof = None
        self.field = None
        self.objID = None
        
    def __repr__(self):
        return "Field-access({0}, {1}, {2})".format(self.base, self.fname, self.field.id)

    def typeof(self):
        if (self.__typeof == None):
            # resolve the field name first
            btype = self.base.typeof()
            if btype.isok():
                if btype.kind not in ['user', 'class_literal']:
                    signal_type_error("User-defined class/instance type expected, found {0}".format(str(btype)), self.lines)
                    self.__typeof = Type('error')
                else:
                    if btype.kind == 'user':
                        # user-defined instance type:
                        acc = 'instance'
                    else:
                        # user-defined class type
                        acc = 'static'

                    baseclass =  btype.baseclass
                    j = resolve_field(acc, baseclass, self.fname, current_class)
                    if (j == None):
                        signal_type_error("No accessible field with name {0} in class {1}".format(self.fname, baseclass.name), self.lines)
                        self.__typeof = Type('error')
                    else:
                        self.field = j
                        self.__typeof = j.type
                        
        return self.__typeof