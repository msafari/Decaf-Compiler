from ast_class import *
from Method import *
from Type import *
from Statements.SkipStmt import *

classtable = {}  # initially empty dictionary of classes.

# Class table.  Only user-defined classes are placed in the class table.
def lookup(table, key):
    if key in table:
        return table[key]
    else:
        return None

def addtotable(table, key, value):
    table[key] = value


def print_ast():
    for cid in classtable:
        c = classtable[cid]
        c.printout()
    print "-----------------------------------------------------------------------------"

def typecheck():
    global errorflag
    errorflag = False
    # add default constructors to all classes first!
    for cid in classtable:
        c = classtable[cid]
        if not c.builtin:
            c.add_default_constructor()
    for cid in classtable:
        c = classtable[cid]
        c.typecheck()
    return not errorflag
    

def initialize_ast():
    # define In class:
    cin = Class("In", None)
    cin.builtin = True     # this is a builtin class
    cout = Class("Out", None)
    cout.builtin = True     # this, too, is a builtin class

    scanint = Method('scan_int', cin, 'public', 'static', Type('int'))
    scanint.update_body(SkipStmt(None))    # No line number information for the empty body
    cin.add_method(scanint)
    
    scanfloat = Method('scan_float', cin, 'public', 'static', Type('float'))
    scanfloat.update_body(SkipStmt(None))    # No line number information for the empty body
    cin.add_method(scanfloat)

    printint = Method('print', cout, 'public', 'static', Type('void'))
    printint.update_body(SkipStmt(None))    # No line number information for the empty body
    printint.add_var('i', 'formal', Type('int'))   # single integer formal parameter
    cout.add_method(printint)
    
    printfloat = Method('print', cout, 'public', 'static', Type('void'))
    printfloat.update_body(SkipStmt(None))    # No line number information for the empty body
    printfloat.add_var('f', 'formal', Type('float'))   # single float formal parameter
    cout.add_method(printfloat)
    
    printboolean = Method('print', cout, 'public', 'static', Type('void'))
    printboolean.update_body(SkipStmt(None))    # No line number information for the empty body
    printboolean.add_var('b', 'formal', Type('boolean'))   # single boolean formal parameter
    cout.add_method(printboolean)
    
    printstring = Method('print', cout, 'public', 'static', Type('void'))
    printstring.update_body(SkipStmt(None))    # No line number information for the empty body
    printstring.add_var('b', 'formal', Type('string'))   # single string formal parameter
    cout.add_method(printstring)

    addtotable(classtable, "In", cin)
    addtotable(classtable, "Out", cout)