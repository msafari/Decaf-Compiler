class VarTable:
    """ Table of variables in each method/constructor"""
    def __init__(self):
        self.vars = {0:{}}
        self.lastvar = 0
        self.lastblock = 0
        self.levels = [0]

    def enter_block(self):
        self.lastblock += 1
        self.levels.insert(0, self.lastblock)
        self.vars[self.lastblock] = {}

    def leave_block(self):
        self.levels = self.levels[1:]
        # where should we check if we can indeed leave the block?

    def add_var(self, vname, vkind, vtype):
        self.lastvar += 1
        c = self.levels[0]   # current block number
        v = Variable(vname, self.lastvar, vkind, vtype)
        vbl = self.vars[c]  # list of variables in current block
        vbl[vname] = v
    
    def _find_in_block(self, vname, b):
        if (b in self.vars):
            # block exists
            if (vname in self.vars[b]):
                return self.vars[b][vname]
        # Otherwise, either block b does not exist, or vname is not in block b
        return None

    def find_in_current_block(self, vname):
        return self._find_in_block(vname, self.levels[0])

    def find_in_scope(self, vname):
        for b in self.levels:
            v = self._find_in_block(vname, b)
            if (v != None):
                return v
            # otherwise, locate in enclosing block until we run out
        return None

    def get_params(self):
        outermost = self.vars[0]  # 0 is the outermost block
        vars = [outermost[vname] for vname in outermost if outermost[vname].kind=='formal']
        vars_ids = [(v.id,v) for v in vars]  # get the ids as well, so that we can order them
        vars_ids.sort()
        return [v for (i,v) in vars_ids]   # in their order of definition!

    def printout(self):
        print "Variable Table:"
        for b in range(self.lastblock+1):
            for vname in self.vars[b]:
                v = self.vars[b][vname]
                v.printout()