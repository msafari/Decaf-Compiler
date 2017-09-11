def signal_type_error(string, lineno):
    global errorflag
    print "{1}: {0}".format(string, lineno)
    errorflag = True

def signal_bop_error(argpos, bop, argtype, arg, possible_types, ptype_string):
    if (argtype.kind not in (['error'] + possible_types)):
        # not already in error
        signal_type_error("Type error in {0} argument of binary {1} expression: {2} expected, found {3}".format(argpos, bop, ptype_string, str(argtype)), arg.lines)

def find_applicable_methods(acc, baseclass, mname, argtypes):
    ms = []
    for m in baseclass.methods:
        if ((m.name == mname) and (m.storage == acc)):
            params = m.vars.get_params()
            paramtypes = [v.type for v in params]
            if ((len(paramtypes) == len(argtypes)) and
                all([(a.is_subtype_of(p)) for (a,p) in (zip(argtypes, paramtypes))])):
                # if every arg is a subtype of corresponding parameter
                ms.append((m, paramtypes))
    
    return ms

def find_applicable_constructors(baseclass, argtypes):
    cs = []
    for c in baseclass.constructors:
        params = c.vars.get_params()
        paramtypes = [v.type for v in params]
        if ((len(paramtypes) == len(argtypes)) and
            all([(a.is_subtype_of(p)) for (a,p) in (zip(argtypes, paramtypes))])):
            # if every arg is a subtype of corresponding parameter
            cs.append((c, paramtypes))
    
    return cs

def most_specific_method(ms):
    mst = None
    result = None
    for (m, t) in ms:
        if (mst == None):
            mst = t
            result = m
        else:
            if all([a.is_subtype_of(b) for (a,b) in zip(mst, t)]):
                # current most specific type is at least as specific as t
                continue
            elif all([b.is_subtype_of(a) for (a,b) in zip(mst, t)]):
                # current t is at least as specific as the most specific type 
                mst = t
                result = m
            else:
                # t is no more specific than mst, nor vice-versa
                return (None, (mst, result, t, m))
                break
    return (result, None)
        
def subtype_or_incompatible(tl1, tl2):
    #  True iff tl1 is a subtype of tl2 or tl2 is a subtype of tl1, or the two type lists are incompatible
    n = len(tl1)
    if (len(tl2) != n):
        return True

    # is tl1 a subtype of tl2?  return False if any incompatible types are found
    subt = True
    for i in range(0,n):
        t1 = tl1[i]
        t2 = tl2[i]
        if (not t1.is_subtype_of(t2)):
            subt = False
            if (t2.is_subtype_of(t1)):
                # tl2 may be a subtype of tl1, so we need to wait to check that
                break
            else:
                # types are incompatible
                return True
    if (subt):
        return True
    # Check the other direction
    for i in range(0,n):
        t1 = tl1[i]
        t2 = tl2[i]
        if (not t2.is_subtype_of(t1)):
            return False
    # tl2 is a subtype of tl1
    return True    

def resolve_method(acc, baseclass, mname, argtypes, current, lineno):
    original_baseclass = baseclass
    while (baseclass != None):
        ms = find_applicable_methods(acc, baseclass, mname, argtypes)
        (m, errorc) = most_specific_method(ms)
        if ((len(ms) > 0) and 
            (m != None) and ( (m.visibility == 'public') or (baseclass == current) )):
            return m
        elif (len(ms) > 0) and (m == None):
            # there were applicable methods but no unique one.
            (t1, m1, t2, m2) = errorc
            signal_type_error("Ambiguity in resolving overloaded method {0}: methods with types '{1}' and '{2}' in class {3}".format(mname, str(t1), str(t2), baseclass.name), lineno)
            return None
        else:
            baseclass = baseclass.superclass
    # search for mname failed,
    signal_type_error("No accessible method with name {0} in class {1}".format(mname, original_baseclass.name), lineno)
    return None

def resolve_constructor(baseclass, current, argtypes, lineno):
    cs = find_applicable_constructors(baseclass, argtypes)
    (c, errorc) = most_specific_method(cs)
    if ((len(cs) > 0) and 
        (c != None) and ( (c.visibility == 'public') or (baseclass == current) )):
        return c
    elif (len(cs) > 0) and (c == None):
        # there were applicable constructors but no unique one.
        (t1, c1, t2, c2) = errorc
        signal_type_error("Ambiguity in resolving overloaded constructor {0}: constructors with types '{1}' and '{2}'}".format(baseclass.name, str(t1), str(t2)), lineno)
        return None
    else:
        signal_type_error("No accessible constructor for class {0}".format(baseclass.name), lineno)
        return None
    

def resolve_field(acc, baseclass, fname, current):
    while (baseclass != None):
        f = baseclass.lookup_field(fname)
        if ((f != None) and (f.storage == acc)
            and ( (f.visibility == 'public') or (baseclass == current) )):
            return f
        else:
            baseclass = baseclass.superclass
    # search for fname failed,
    return None
