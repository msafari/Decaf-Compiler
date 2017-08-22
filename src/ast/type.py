class Type:
    """A class encoding Types in Decaf"""
    def __init__(self, basetype, params=None, literal=False):
        if ((params == None) or (params == 0)):
            if (basetype in ['int', 'boolean', 'float', 'string', 'void', 'error', 'null']):
                self.kind = 'basic'
                self.typename = basetype
            elif (not literal):
                self.kind = 'user'
                self.baseclass = basetype
            else:
                self.kind = 'class_literal'
                self.baseclass = basetype
        else:
            if (params == 1):
                bt = basetype
            else:
                bt = Type(basetype, params=params-1)
            self.kind = 'array'
            self.basetype = bt

    def __str__(self):
        if (self.kind == 'array'):
            return 'array(%s)'%(self.basetype.__str__())
        elif (self.kind == 'user'):
            return 'user(%s)'%str(self.baseclass.name)
        elif (self.kind == 'class_literal'):
            return 'class_literal(%s)'%str(self.baseclass.name)
        else:
            return self.typename

    def __repr(self):
        return self.__str__()

    def is_subtype_of(self, other):
        if (self.kind == 'basic'):
            if other.kind == 'basic':
                if (self.typename == other.typename):
                    return True
                elif (self.typename == 'int') and (other.typename == 'float'):
                    return True
            elif (self.typename == 'null'):
                return (other.kind == 'user') or (other.kind == 'array')
        elif (self.kind == 'user'):
            if (other.kind == 'user'):
                return self.baseclass.is_subclass_of(other.baseclass)
        elif (self.kind == 'class_literal'):
            if (other.kind == 'class_literal'):
                return self.baseclass.is_subclass_of(other.baseclass)
        elif (self.kind == 'array') and (other.kind =='array'):
            return self.basetype.is_subtype_of(other.basetype)
        return False 

    def isint(self):
        return self.kind == 'basic' and self.typename == 'int'
        
    def isnumeric(self):
        return self.kind == 'basic' and (self.typename == 'int'
                                         or self.typename == 'float')
    def isboolean(self):
        return self.kind == 'basic' and self.typename == 'boolean'

    def isok(self):
        return not (self.kind == 'basic' and self.typename == 'error')
