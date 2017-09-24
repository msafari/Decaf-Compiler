# Intermediate code generator
from collections import deque
from absmc import abstract_machine
from ast import *

# Create the abstract machine
am = abstract_machine()
outputFile = None 

localVarRegisters = {} #Key: <var id>, Value: <register number>
argumentRegisters = {
	0 : am.getNewArgReg()
}

#A dict of labels associated with each method in each class
#Use for method calls
methodLabels = {}	#Key: <Method ID>, Value: <label name>

#offset from the base of the heap to the top of the heap
#Allocate memory for new objects here
heapTop = 0 

#Use to get heap offset for object instances
heapOffset = {} #Key: <Variable id>, Value: <heap offset>


def generateCode(filename):
	global outputFile
	outputName = "{0}.ami".format(filename)
	outputFile = open(outputName, 'w')
	am.allocateStaticFields()
	code = generateClassCode(ast.classtable)
	outputFile.write(code)


def generateClassCode(classtable):
	code = ""

	# Iterate over all parsed classes
	for key in classtable:
		dClass = classtable[key]

		code += "# ---{0}---\n".format(dClass.name)

		# Generate code blocks for every method in the class
		for method in dClass.methods:
			code += generateMethodCode(method)

		# Generate code blocks for every constructor in the class
		for constr in dClass.constructors:
			code += generateConstructorCode(constr)

	return code


def generateMethodCode(method):
	global localVarRegisters, methodLabels, am

	outputCode = "" #Final output to write to file
	blockLabel = getMethodLabel(method)
	outputCode += "{0}:\n".format(blockLabel)	# add block label

	methodLabels[method.id] = blockLabel

	localVarRegisters = {} #reset dict for local vars
	#Allocate registers for all local vars in this method
	varTable = method.vars.vars
	for block in varTable:
		for varname in varTable[block]:
			var = varTable[block][varname]
			localVarRegisters[var.id] = am.getNewReg()
	
	#Add method paramters to this dict
	params = method.vars.get_params()
	for i in xrange(0, len(params)):
		localVarRegisters[params[i]] = "a" + str(i)
		argumentRegisters[am.argumentRegNum] = am.getNewArgReg() 


	if isinstance(method.body, SkipStmt):
		outputCode += ""
	else:
		for stmt in method.body.stmtlist:
			outputCode += generateStmtCode(stmt)

	#Add return statement
	outputCode += "ret \n\n"

	return outputCode

def generateConstructorCode(constructor):
	global localVarRegisters, am

	code = ""
	constructorLabel = "C_{0}".format(constructor.id)
	c_class = ast.lookup(ast.classtable, constructor.name)
	class_field_len = len(c_class.fields)

	heapExtendReg = am.getNewReg()
	code += "move_immed_i {0}, {1}\n".format(heapExtendReg, class_field_len)
	hallocReg = am.getNewReg()
	code += "halloc {0}, {1}\n".format(hallocReg, heapExtendReg)


	localVarRegisters = {} #reset dict for local vars
	#Allocate registers for all local vars in this method
	varTable = constructor.vars.vars
	for block in varTable:
		for varname in varTable[block]:
			var = varTable[block][varname]
			localVarRegisters[var.id] = am.getNewReg()
	
	#Add method paramters to this dict
	params = constructor.vars.get_params()
	for i in xrange(0, len(params)):
		argReg = "a" + str(i)
		localVarRegisters[params[i]] = argReg
		argumentRegisters[am.argumentRegNum] = am.getNewArgReg() 
		code += "save {0}\n".format(argReg)

	code += "save {0}\n".format(hallocReg)
	code += "call {0}\n".format(constructorLabel)

	# restore address of new obj
	code += "restore {0}\n".format(hallocReg)

	# restore arguments
	i = len(params) - 1
	while 0 <= i:
		argReg = "a" + str(i)
		code += "restore {0}\n".format(argReg)
		i -= 1

	code += "{0}:\n".format(constructorLabel)
	code += generateStmtCode(constructor.body)
	return code


def generateStmtCode(stmt):
	if isinstance(stmt, IfStmt):
		return generateIfStmtCode(stmt)
	elif isinstance(stmt, WhileStmt):
		return generateWhileStmtCode(stmt)
	elif isinstance(stmt, ForStmt):
		return generateForStmtCode(stmt)
	elif isinstance(stmt, ReturnStmt):
		return generateReturnStmtCode(stmt)
	elif isinstance(stmt, ExprStmt):
		return generateExprStmtCode(stmt)
	elif isinstance(stmt, BlockStmt):
		return generateBlockStmtCode(stmt)
	elif isinstance(stmt, BreakStmt):
		return generateBreakStmtCode(stmt)
	elif isinstance(stmt, SkipStmt):
		return generateSkipStmtCode(stmt)
	elif isinstance(stmt, ContinueStmt):
		return generateContinueStmtCode(stmt)

# statement of form if (e) S1 else S2 is evaluated by first
# evaluating e. If e evaluates to true, then S1 is executed. If e evaluates to
# false, then S2 is executed. A statement of the form if (e) S1 is executed as
# if it were if (e) S1 else ;.
def generateIfStmtCode(ifStmt):
	code = ""
	global am
	condRegandCode = generateExprCode(ifStmt.condition)
	condReg = condRegandCode[0]
	condCode = condRegandCode[1]
	code += condCode 			# add code for conditon

	elseLabel = "else_{0}".format(am.getUniqueLabelNum())
	code += "bz {0}, {1}\n".format(condReg, elseLabel)

	# add the then code
	thenCode = generateStmtCode(ifStmt.thenpart)
	code += thenCode

	# add the else part
	# generate new label
	code += "{0}:\n".format(elseLabel)
	elseCode = generateStmtCode(ifStmt.elsepart)
	code += elseCode

	return code

# A statement of the form while (e) S1 is executed in the following steps:
# 1. Evaluate e.
# 2. If the result of evaluating e is true, then execute S1. The execution
# then starts over again at step 1.
# 3. If the result of evaluating e is false, then execution of the while statement is finished.
def generateWhileStmtCode(whileStmt):
	code = ""
	global am
	condRegandCode = generateExprCode(whileStmt.cond)
	condReg = condRegandCode[0]
	condCode = condRegandCode[1]
	code += condCode 		# add code for while condition

	whileLabel = "Loop_{0}".format(am.getUniqueLabelNum())
	am.loopLabelStack.append(whileLabel)
	endWhileLabel = "End_loop_{0}".format(am.getUniqueLabelNum())
	am.loopEndLabelStack.append(endWhileLabel)

	code += "{0}:\n".format(whileLabel)
	code += "bz {0}, {1}\n".format(condReg, endWhileLabel)

	# generate while body code
	bodyCode = generateStmtCode(whileStmt.body)
	code += bodyCode
	# add the jmp statement at the end of body code
	code += "jmp {0}\n".format(whileLabel)

	# output end while label
	code += "{0}:\n".format(endWhileLabel)

	return code

def generateForStmtCode(forStmt):
	code = ""
	global am
	# output init code
	initRegandCode = generateExprCode(forStmt.init)
	initReg = initRegandCode[0]
	initCode = initRegandCode[1]
	code += initCode

	continueLabel = "Loop_{0}".format(am.getUniqueLabelNum())
	endLabel = "End_Loop_{0}".format(am.getUniqueLabelNum())
	am.loopEndLabelStack.append(endLabel)
	am.loopLabelStack.append(continueLabel)

	# output condition code
	condRegandCode = generateExprCode(forStmt.cond)
	condReg = condRegandCode[0]
	condCode = condRegandCode[1]
	code += "{0}:\n".format(continueLabel)
	code += condCode
	code += "bz {0}, {1}\n".format(condReg, endLabel)

	# output update code
	oneReg = am.getNewReg()
	code += "mode_immed_i {0}, 1\n".format(oneReg)
	code += "iadd {0}, {1}, {2}\n".format(initReg, initReg, oneReg)

	#output for body
	code += generateStmtCode(forStmt.body)
	code += "jmp {0}\n".format(continueLabel)

	#output end label
	code += "{0}:\n".format(endLabel)
	return code


def generateReturnStmtCode(returnStmt):
	code = ""
	if returnStmt.expr:
		ResultRegandCode = generateExprCode(returnStmt.expr)
		code += ResultRegandCode[1]
		code += "move {0}, {1}\n".format("a0", ResultRegandCode[0])
		code += "ret\n"
	return code

def generateExprStmtCode(exprStmt):
	code = ""
	expr = exprStmt.expr

	if isinstance(expr, AssignExpr):
		code += generateAssignExprCode(expr)
	elif isinstance(expr, MethodInvocationExpr):
		code += generateMethodInvocationExprCode(expr)[1]

	return code

def generateBlockStmtCode(blockStmt):
	code = ""
	for stmt in blockStmt.stmtlist:
		code += generateStmtCode(stmt)
	return code

def generateBreakStmtCode(breakStmt):
	global am
	mostRecentEndLabel = am.loopEndLabelStack.pop()
	code = "jmp {0}\n".format(mostRecentEndLabel)
	return code

def generateSkipStmtCode(skipStmt):
	return ""

def generateContinueStmtCode(contStmt):
	global am
	mostRecentLoopLabel = am.loopLabelStack.pop()
	code = "jmp {0}\n".format(mostRecentLoopLabel)
	return code

def generateExprCode(expr):
	if isinstance(expr, ConstantExpr):
		return generateConstExprCode(expr)
	elif isinstance(expr, VarExpr):
		return generateVarExprCode(expr)
	elif isinstance(expr, UnaryExpr):
		return generateUnaryExprCode(expr)
	elif isinstance(expr, BinaryExpr):
		return generateBinaryExprCode(expr)
	elif isinstance(expr, AutoExpr):
		return generateAutoExpr(expr)
	elif isinstance(expr, FieldAccessExpr):
		return generateFieldAccessExprCode(expr)
	elif isinstance(expr, MethodInvocationExpr):
		return generateMethodInvocationExprCode(expr)
	elif isinstance(expr, NewObjectExpr):
		return generateNewObjectExprCode(expr)
	elif isinstance(expr, AssignExpr):
		return generateAssignExprCode(expr)

#Generate code to load the constant expr into a register before it is used
def generateConstExprCode(constExpr):
	code = ""
	global am
	#Register to set value
	register = am.getNewReg()
	
	if constExpr.kind == 'int':
		code += "move_immed_i {0}, {1}\n".format(register, constExpr.int)
	elif constExpr.kind == 'float':
		code += "move_immed_f {0}, {1}\n".format(register, constExpr.float)
	elif constExpr.kind == 'Null': 
		#TODO: Null value?
		pass
	elif constExpr.kind == 'True':
		code += "move_immed_i {0}, 1\n".format(register)
	elif constExpr.kind == 'False':
		code += "move_immed_i {0}, 0\n".format(register)

	#A tuple with the register holding this expression's value and the generated code string
	return (register, code)

#Generate code to load the varExpr's value into a register before it is used
def generateVarExprCode(varExpr):
	code = ""
	global am
	var = varExpr.var
	code += "#LINE {0} - Load value for '{1}'\n".format(varExpr.lines, var.name)
	
	#VarExpr is either for object instance, static field or, local variable

	#Try getting heap offset 
	try:
		#Load base of object
		objOffset = heapOffset[var.id]
		objBaseReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(objBaseReg, objOffset)
		return (objBaseReg, code)
	except KeyError, e:
		pass

	#Try getting static area offset
	try:
		offset = am.staticFieldOffset[var.id]
		offsetReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(offsetReg, offset)
		valueReg = am.getNewReg()
		code += "hload {0}, sap, {1}\n".format(valueReg, offsetReg)
		return (valueReg, code)

	#Neiter loading object from heap or static area worked, must be in a temp register
	except:
		register = localVarRegisters[var.id]
		return (register, code)

def generateUnaryExprCode(unaryExpr):
	code = ""
	global am
	expr = unaryExpr.arg
	regandcode = generateExprCode(expr)
	exprReg = regandcode[0]
	code += regandcode[1]

	#Generate code to multiply the expression by -1
	if unaryExpr.uop == 'uminus':
		negOneReg = am.getNewReg()
		code += "move_immed_i {0}, -1\n".format(negOneReg)
		resultReg = am.getNewReg()
		code += "imul {0}, {1}, {2}\n".format(resultReg, exprReg, negOneReg)
		return (resultReg, code)
	#Generate code to negate (NOT) the expression
	elif unaryExpr.uop == 'neg':
		trueLabel = getTrueCaseLabel()
		afterLabel = getAfterCaseLabel()

		#Code to branch if the expr value is 'true'
		code += "bnz {0}, {1}\n".format(exprReg, trueLabel)
		code += "move_immed_i {0}, 1\n".format(exprReg)	#set the valuereg to 'false'
		code += "jmp {0}\n".format(afterLabel)

		#Branch code if expr is false
		code += "\n{0}:\n".format(trueLabel)
		code += "move_immed_i {0}, 0\n".format(exprReg)	#set the valuereg to 'false'
		code += "jmp {0}\n".format(afterLabel)

		#Continuing after label
		code += "\n{0}:\n".format(afterLabel)

		return (exprReg, code)

def generateBinaryExprCode(binaryExpr):
	code = ""
	global am
	leftExpr = binaryExpr.arg1
	rightExpr = binaryExpr.arg2

	#generate code and get the registers for the left and right expressions
	leftRegandCode = generateExprCode(leftExpr)
	rightRegandCode = generateExprCode(rightExpr)
	leftExprReg = leftRegandCode[0]
	rightExprReg = rightRegandCode[0]
	code += leftRegandCode[1]
	code += rightRegandCode[1]

	#Result of binary operation will be in this register
	resultReg = am.getNewReg()
	if binaryExpr.bop in ['add', 'sub', 'mul', 'div', 'lt', 'leq', 'gt', 'geq']:
		code += "#LINE {0} - binary '{1}' op\n".format(binaryExpr.lines, binaryExpr.bop)
		opcode = "i" + binaryExpr.bop
		code += "{0} {1}, {2}, {3}\n".format(opcode, resultReg, leftExprReg, rightExprReg)
	elif binaryExpr.bop == 'and':
		code += "#LINE {0} - binary '{1}' op\n".format(binaryExpr.lines, binaryExpr.bop)
		falseLabel = getFalseCaseLabel()
		afterLabel = getAfterCaseLabel()

		#Code to branch if either of the expressions are not true
		code += "bz {0}, {1}\n".format(leftExprReg, falseLabel)
		code += "bz {0}, {1}\n".format(rightExprReg, falseLabel)
		#Code to set expression's value to true
		code += "#logical expression is true\n"
		code += "move_immed_i {0}, 1\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Code for the false case
		code += "\n{0}:\n".format(falseLabel)
		code += "#logical expression is false\n"
		code += "move_immed_i {0}, 0\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Label to continue after this conditional case
		code += "\n{0}:\n".format(afterLabel)
	elif binaryExpr.bop == 'or':
		code += "#LINE {0} - binary '{1}' op\n".format(binaryExpr.lines, binaryExpr.bop)
		trueLabel = getTrueCaseLabel()
		afterLabel = getAfterCaseLabel()

		#Code to branch if either of the expressions are not true
		code += "bnz {0}, {1}\n".format(leftExprReg, trueLabel)
		code += "bnz {0}, {1}\n".format(rightExprReg, trueLabel)
		#Code to set expression's value to false
		code += "#logical expression is false\n"
		code += "move_immed_i {0}, 0\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Code for the true case
		code += "\n{0}:\n".format(trueLabel)
		code += "#logical expression is true\n"
		code += "move_immed_i {0}, 1\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Label to continue after this conditional case
		code += "\n{0}:\n".format(afterLabel)
	elif binaryExpr.bop == "==":
		code += "#LINE {0} - binary '{1}' op\n".format(binaryExpr.lines, binaryExpr.bop)
		falseLabel = getFalseCaseLabel()
		afterLabel = getAfterCaseLabel()

		subResultReg = am.getNewReg()
		#Code to check equivalence
		code += "isub {0}, {1}, {2}\n".format(subResultReg, leftExprReg, rightExprReg)
		code += "bnz {0}, {1}\n".format(subResultReg, falseLabel)
		#Code to set equivalence to true
		code += "#Equivalence is true\n"
		code += "move_immed_i {0}, 1\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Code for false equivalence
		code += "\n{0}:\n".format(falseLabel)
		code += "#Equivalence is false"
		code += "move_immed_i {0}, 0\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Label to continue after equivalence check
		code += "\n{0}:\n".format(afterLabel)
	else:	#For binary op '!='
		code += "#LINE {0} - binary '{1}' op\n".format(binaryExpr.lines, binaryExpr.bop)
		falseLabel = getFalseCaseLabel()
		afterLabel = getAfterCaseLabel()

		subResultReg = am.getNewReg()
		#Code to check equivalence
		code += "isub {0}, {1}, {2}\n".format(subResultReg, leftExprReg, rightExprReg)
		code += "bz {0}, {1}\n".format(subResultReg, falseLabel)
		#Code to set equivalence to true
		code += "#Equivalence is true\n"
		code += "move_immed_i {0}, 1\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Code for false equivalence
		code += "\n{0}:\n".format(falseLabel)
		code += "#Equivalence is false"
		code += "move_immed_i {0}, 0\n".format(resultReg)
		code += "jmp {0}\n".format(afterLabel)

		#Label to continue after equivalence check
		code += "\n{0}:\n".format(afterLabel)

	return (resultReg, code)

def generateAssignExprCode(assignExpr):
	code = ""
	global am
	#Load a register with the rhs expression
	rhsRegandCode = generateExprCode(assignExpr.rhs)
	#Load a register with the address of the lhs expression
	lhsRegandCode = generateLCode(assignExpr.lhs)

	lhsAddrReg = lhsRegandCode[0]
	rhsValueReg = rhsRegandCode[0]
	code += lhsRegandCode[1]
	code += rhsRegandCode[1]

	if len(lhsRegandCode) == 2:
		zeroReg = am.getNewReg()
		code += "#LINE {0} - Store the value in {1} at addr in {2}\n".format(assignExpr.lines, rhsValueReg, lhsAddrReg)
		code += "move_immed_i {0}, 0\n".format(zeroReg)
		code += "hstore {0}, {1}, {2}\n".format(zeroReg, lhsAddrReg, rhsValueReg)
	#The length is 3 and thus, lhsAddrReg is just a temp register and NOT a heap address
	else:
		code += "#LINE {0} - Store the value in {1} in {2}\n".format(assignExpr.lines, rhsValueReg, lhsAddrReg)
		code += "move {0}, {1}\n".format(lhsAddrReg, rhsValueReg)
	return code

	

def generateMethodInvocationExprCode(methodInvocationExpr):
	code = ""
	global am
	line = methodInvocationExpr.lines
	method = methodInvocationExpr.method
	methodLabel = methodLabels[method.id]

	code += "#LINE {0} - Call method '{1}'\n".format(line, method.name)
	#Save argument registers onto the stack
	code += "#Save registers\n"
	for i in xrange(0, len(argumentRegisters)):
		argReg = "a" + str(i)
		code += "save {0}\n".format(argReg)
	#Call the function	
	code += "call {0}\n".format(methodLabel)
	#Move the return value from a0 to it's own temp register
	code += "#Save return value to temp register\n"

	returnValReg = am.getNewReg()
	code += "move {0}, a0	#return value in {0}\n".format(returnValReg)
	#Restore argument registers from stack
	code += "#Restore registers\n"
	for i in xrange(len(argumentRegisters), 0, -1):
		argReg = "a" + str(i)
		code += "restore {0}\n".format(argReg)

	return (returnValReg, code)

#Generate code to load the address of the field access into a register
def generateLCode(expr):
	code = ""
	global am

	if isinstance(expr, FieldAccessExpr):
		fieldAccessExpr = expr
		baseExpr = fieldAccessExpr.base
		field = fieldAccessExpr.field

		#FIELD ACCESS USING THIS KEYWORD IS NOT SUPPORTED
		if isinstance(baseExpr, ThisExpr):
			code += "#LINE {0} - Load addr for 'this' field access".format(expr.lines)
			objID = fieldAccessExpr.objID
			baseClass = baseExpr.current_class

			#Load base of object
			objOffset = heapOffset[objID]
			objBaseReg = am.getNewReg()
			code += "move_immed_i {0}, {1}\n".format(objBaseReg, offset)

			#Load offset of field
			fieldIndex = baseClass.lookup_field_index(field)
			fieldIndexReg = am.getNewReg()
			code += "move_immed_i {0}, {1}\n".format(fieldIndexReg, fieldIndex)
			
			#Calculate the field's heap addr
			fieldAddrReg = am.getNewReg()
			code += "iadd {0}, {1}, {2}".format(fieldAddrReg, objBaseReg, fieldIndexReg)

			return (fieldAddrReg, code)

		#FIELD ACCESS USING SUPER KEYWORD IS NOT SUPPORTED
		elif isinstance(baseExpr, SuperExpr):
			code += "#LINE {0} - Load addr for 'super' field access".format(expr.lines)
			objID = fieldAccessExpr.objID
			baseClass = baseExpr.current_class.superclass

			#Load base of object
			objOffset = heapOffset[objID]
			objBaseReg = am.getNewReg()
			code += "move_immed_i {0}, {1}\n".format(objBaseReg, offset)

			#Load offset of field
			fieldIndex = baseClass.lookup_field_index(field)
			fieldIndexReg = am.getNewReg()
			code += "move_immed_i {0}, {1}\n".format(fieldIndexReg, fieldIndex)
			
			#Calculate the field's heap addr
			fieldAddrReg = am.getNewReg()
			code += "iadd {0}, {1}, {2}".format(fieldAddrReg, objBaseReg, fieldIndexReg)

			return (fieldAddrReg, code)


		elif isinstance(baseExpr, ClassReferenceExpr):
			#Calculate address of the static variable
			code += "#LINE {0} - Retrieve address of field '{1}'\n".format(fieldAccessExpr.lines, field.name)

			offset = am.staticFieldOffset[field.id]

			offsetReg = am.getNewReg()
			code += "move_immed_i {0}, {1}\n".format(offsetReg, offset)
			fieldAddrReg = am.getNewReg()
			code += "iadd {0}, sap, {1}\n".format(fieldAddrReg, offsetReg)
			return (fieldAddrReg, code)
		
		#Otherwise, baseExpr is an object instance, and is a VarExpr
		else:
			code += "#LINE {0} - Load address for var field access\n".format(expr.lines)
			variable = baseExpr.var
			objID = variable.id
			baseClass = variable.type.baseclass

			#Load base of object
			objOffset = heapOffset[objID]
			objBaseReg = am.getNewReg()
			code += "move_immed_i {0}, {1} #obj offset\n".format(objBaseReg, objOffset)

			#Load offset of field
			fieldIndex = baseClass.lookup_field_index(field)
			fieldIndexReg = am.getNewReg()
			code += "move_immed_i {0}, {1} #field offset\n".format(fieldIndexReg, fieldIndex)
			
			#Calculate the field's heap address
			fieldAddrReg = am.getNewReg()
			code += "iadd {0}, {1}, {2}\n".format(fieldAddrReg, objBaseReg, fieldIndexReg)

			return (fieldAddrReg, code)

	elif isinstance(expr, VarExpr):
		variable = expr.var
		objID = variable.id

		#Try using this variable ID to retrive a heap offset
		try:
			objOffset = heapOffset[objID]
			objOffsetReg = am.getNewReg()
			code += "#LINE {0} - Get var '{1}' address\n".format(expr.lines, variable.name)
			code += "move_immed_i {0}, {1}\n".format(objOffsetReg, objOffset)
			return (objOffsetReg, code)

		#This variable doesn't have a heap offset and thus, is not an object
		#Use the associated temporary register as a location
		except KeyError:
			varReg = localVarRegisters[variable.id]
			code += "#LINE {0} - var '{1}' is in {2}\n".format(expr.lines, variable.name, varReg)
			
			#Return 3 elements to indicate the location is just a temp register and not a 
			#heap addrs
			return (varReg, code, True)

def generateAutoExpr(autoExpr):
	code = ""
	global am
	addrRegandCode = generateLCode(arg)
	addrReg = addrRegandCode[0]
	code += addrRegandCode[1]

	operation = autoExpr.oper
	order = autoExpr.when

	valueReg = am.getNewReg()
	if order == 'pre':
		#Load the expression value using the addr register and a zero register
		zeroReg = am.getNewReg()
		code += "move_immed_i {0}, 0\n".format(zeroReg)
		code += "hload {0}, {1}, {2}\n".format(valueReg, addrReg, zeroReg)

		#add or decrement the value
		if operation == 'inc':
			code += "iadd {0}, {0}, 1\n".format(valueReg)
		else:
			code += "isub {0}, {0}, 1\n".format(valueReg)

		#Store the value
		code += "hstore {0}, {1}, {2}\n".format(zeroReg, addrReg, valueReg)
	else:	#Post order
		#Load the expression value using the addr register and a zero register
		zeroReg = am.getNewReg()
		code += "move_immed_i {0}, 0\n".format(zeroReg)
		code += "hload {0}, {1}, {2}\n".format(valueReg, addrReg, zeroReg)

		#Use seperate value reg that is post incremented
		postValueReg = am.getNewReg()

		#add or decrement the value
		if operation == 'inc':
			code += "iadd {0}, {1}, 1\n".format(postValueReg, valueReg)
		else:
			code += "isub {0}, {1}, 1\n".format(postValueReg, valueReg)

		#Store the post incremented value
		code += "hstore {0}, {1}, {2}\n".format(zeroReg, addrReg, postValueReg)

	return (valueReg, code)

def generateFieldAccessExprCode(expr):
	code = ""
	global am
	baseExpr = expr.base
	field = expr.field
	fieldAccessExpr = expr

	#FIELD ACCESS USING THIS KEYWORD IS NOT SUPPORTED
	if isinstance(baseExpr, ThisExpr):
		code += "#LINE {0} - Load value for 'this' field access".format(expr.lines)
		objID = fieldAccessExpr.objID
		baseClass = baseExpr.current_class

		#Load base of object
		objOffset = heapOffset[objID]
		objBaseReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(objBaseReg, offset)

		#Load offset of field
		fieldIndex = baseClass.lookup_field_index(field)
		fieldIndexReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(fieldIndexReg, fieldIndex)
		
		#Load the field's value from heap
		fieldValReg = am.getNewReg()
		code += "hload {0}, {1}, {2}".format(fieldValReg, objBaseReg, fieldIndexReg)

		return (fieldValReg, code)

	#FIELD ACCESS USING SUPER KEYWORD IS NOT SUPPORTED
	elif isinstance(baseExpr, SuperExpr):
		code += "#LINE {0} - Load value for 'super' field access".format(expr.lines)
		objID = fieldAccessExpr.objID
		baseClass = baseExpr.current_class.superclass

		#Load base of object
		objOffset = heapOffset[objID]
		objBaseReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(objBaseReg, offset)

		#Load offset of field
		fieldIndex = baseClass.lookup_field_index(field)
		fieldIndexReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(fieldIndexReg, fieldIndex)
		
		#Load the field's value from heap
		fieldValReg = am.getNewReg()
		code += "hload {0}, {1}, {2}".format(fieldValReg, objBaseReg, fieldIndexReg)

		return (fieldValReg, code)

	elif isinstance(baseExpr, ClassReferenceExpr):
		#Retrieve the value of the static field
		code += "#LINE {0} - Retrieve value of field {1}\n".format(expr.lines, field.name)

		#Get the static field offset
		offset = am.staticFieldOffset[field.id]
		offsetReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(offsetReg, offset)

		#Load the field value from the static area
		valueReg = am.getNewReg()
		code += "hload {0}, sap, {1}\n".format(valueReg, offsetReg)
		return (valueReg, code)
	
	#Otherwise, baseExpr is an object instance, and is a VarExpr
	else:
		code += "#LINE {0} - Load address for var field access".format(expr.lines)
		variable = baseExpr.var
		objID = variable.id
		baseClass = variable.type.baseclass

		#Load base of object
		objOffset = heapOffset[objID]
		objBaseReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(objBaseReg, offset)

		#Load offset of field
		fieldIndex = baseClass.lookup_field_index(field)
		fieldIndexReg = am.getNewReg()
		code += "move_immed_i {0}, {1}\n".format(fieldIndexReg, fieldIndex)
		
		#Load the field's value from heap
		fieldValReg = am.getNewReg()
		code += "hload {0}, {1}, {2}".format(fieldValReg, objBaseReg, fieldIndexReg)

		return (fieldValReg, code)

def generateNewObjectExprCode(newObjectExpr):
	global heapTop
	global am
	code = ""
	line = newObjectExpr.lines
	dClass = newObjectExpr.classref
	args = newObjectExpr.args
	heapOffset[newObjectExpr.objID] = heapTop

	#Count the number of class fields and super class fields
	numFields = 0
	current = dClass
	while current != None:
		numFields += len(current.fields)
		current = current.superclass


	code += "#LINE {0} - Create new '{1}' object\n".format(line, dClass.name)
	baseReg = am.getNewReg()
	code += "move_immed_i {0}, {1} #Base of object in {0}\n".format(baseReg, heapTop)
	numCellsReg = am.getNewReg()
	code += "move_immed_i {0}, {1} #Num of cells in {0}\n".format(numCellsReg, numFields)
	code += "halloc {0}, {1}\n".format(baseReg, numCellsReg)

	#TODO: number of cells should be numFields - numOfStaticFields in class
	heapTop += numFields

	#Return the register with the heap offset for this register
	return (baseReg, code)

#Use to make labels for result of conditional statements
def getTrueCaseLabel():
	global am
	label = "trueCase" + str(am.getUniqueLabelNum())
	return label

def getFalseCaseLabel():
	global am
	label = "falseCase" + str(am.getUniqueLabelNum())
	return label

def getAfterCaseLabel():
	global am
	label = "afterCase" + str(am.getUniqueLabelNum())
	return label


def getBlockLabel():
	global am
	label = "block" + str(am.getUniqueLabelNum())
	return label

def getMethodLabel(method):
	label = "M_{0}_{1}".format(method.name, method.id)
	return label
