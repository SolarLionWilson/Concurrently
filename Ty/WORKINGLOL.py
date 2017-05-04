#!/usr/bin/python


# ! C:\Program Files\Python26\pythonw\
# Ty Walters
# TODO do the LABEL function and the goto function. Figure out how enter works with label. How to save the line number to jump to the statement
# TODO maybe look at the repeat function
# ID:848348
import sys, string, threading, time

labelMax = 5
norw = 33  # number of reserved words (mod)
txmax = 100  # length of identifier table
nmax = 14  # max number of digits in number
al = 10  # length of identifiers
CXMAX = 500  # maximum allowed lines of assembly code
STACKSIZE = 500
MAXTHREADS = 50  # maximum amount of threads
a = []
chars = []
rword = []
table = []  # symbol table
thTable = [] * MAXTHREADS  # threadTable for threads
code = []  # code array
stack = [0] * STACKSIZE  # interpreter stack
global infile, outfile, ch, sym, id, num, linlen, kk, line, errorFlag, linelen, codeIndx, prevIndx, codeIndx0


# -------------values to put in the symbol table------------------------------------------------------------
class tableValue():
	def __init__(self, name, kind, level, adr, value):
		self.name = name
		self.kind = kind
		self.adr = adr
		self.value = value
		self.level = level
		self.params = []
		self.nest = 0


class threadStruct(threading.Thread):
	def __init__(self, address, top, base, currentBase, stak, statLinks, orginalStack):
		self.address = address
		self.top = top
		self.base = base
		self.currentBase = currentBase
		self.position = position
		self.stack = stack
		self.orginalStack = orginalStack

	def run(self, counter):
		multiThreading(counter)

	def sleep(seconds):
		time.sleep(seconds)


# ----------commands to put in the array of assembly code-----------------------------------------------
class Cmd():
	def __init__(self, line, cmd, statLinks, value):
		self.line = line
		self.cmd = cmd
		self.statLinks = statLinks
		self.value = value


# -------------function to generate assembly commands--------------------------------------------------
def gen(cmd, statLinks, value):
	global codeIndx, CXMAX
	if codeIndx > CXMAX:
		print >> outfile, "Error, Program is too long"
		exit(0)
	x = Cmd(codeIndx, cmd, statLinks, value)
	code.append(x)
	codeIndx += 1


# --------------function to change jump commands---------------------------------------
def fixJmp(cx, jmpTo):
	code[cx].value = jmpTo


# --------------Function to print p-Code for a given block-----------------------------
def printCode():
	global codeIndx, codeIndx0
	print>> outfile
	for i in range(codeIndx0, codeIndx):
		print >> outfile, code[i].line, code[i].cmd, code[i].statLinks, code[i].value
	prevIndx = codeIndx


# -------------Function to find a new base----------------------------------------------
def Base(statLinks, base):
	b1 = base
	while (statLinks > 0):
		b1 = stack[b1]
		statLinks -= 1
	return b1


def multiThreading(count):
	top = 0
	base = 1
	pos = 0
	stack[1] = 0
	stack[2] = 0
	stack[3] = 0


# -------------P-Code Interpreter-------------------------------------------------------
def Interpret():
	print >> outfile, "Start PL/0"
	top = 0
	base = 1
	pos = 0
	stack[1] = 0
	stack[2] = 0
	stack[3] = 0
	counter =0
	total_threads = 0
	running = 0

	thread_array = []

	while True:
		instr = code[pos]
		pos += 1
		#       LIT COMMAND
		if instr.cmd == "LIT":
			top += 1
			stack[top] = int(instr.value)
		# OPR COMMAND
		elif instr.cmd == "OPR":
			if instr.value == 0:  # end
				top = base - 1
				base = stack[top + 2]
				pos = stack[top + 3]
			elif instr.value == 1:  # unary minus
				stack[top] = -stack[top]
			elif instr.value == 2:  # addition
				top -= 1
				stack[top] = stack[top] + stack[top + 1]
			elif instr.value == 3:  # subtraction
				top -= 1
				stack[top] = stack[top] - stack[top + 1]
			elif instr.value == 4:  # multiplication
				top -= 1
				stack[top] = stack[top] * stack[top + 1]
			elif instr.value == 5:  # integer division
				top -= 1
				stack[top] = stack[top] / stack[top + 1]
			elif instr.value == 6:  # logical odd function
				if stack[top] % 2 == 0:
					stack[top] = 1
				else:
					stack[top] = 0
			# case 7 n/a, used to debuge programs
			elif instr.value == 8:  # test for equality if stack[top-1] = stack[top], replace pair with true, otherwise false
				top -= 1
				if stack[top] == stack[top + 1]:
					stack[top] = 1
				else:
					stack[top] = 0
			elif instr.value == 9:  # test for inequality
				top -= 1
				if stack[top] != stack[top + 1]:
					stack[top] = 1
				else:
					stack[top] = 0
			elif instr.value == 10:  # test for < (if stack[top-1] < stack[t])
				top -= 1
				if stack[top] < stack[top + 1]:
					stack[top] = 1
				else:
					stack[top] = 0
			elif instr.value == 11:  # test for >=
				top -= 1
				if stack[top] >= stack[top + 1]:
					stack[top] = 1
				else:
					stack[top] = 0
			elif instr.value == 12:  # test for >
				top -= 1
				if stack[top] > stack[top + 1]:
					stack[top] = 1
				else:
					stack[top] = 0
			elif instr.value == 13:  # test for <=
				top -= 1
				if stack[top] <= stack[top + 1]:
					stack[top] = 1
				else:
					stack[top] = 0
			elif instr.value == 14:  # write/print stack[top]
				print >> outfile, stack[top],
				top -= 1
			elif instr.value == 15:  # write/print a newline
				print
		# LOD COMMAND
		elif instr.cmd == "LOD":
			top += 1
			stack[top] = stack[Base(instr.statLinks, base) + instr.value]
		# STI COMMAND (begin mod)
		elif instr.cmd == "STI":
			stack[stack[Base(instr.statLinks, base) + instr.value]] = stack[top]
			top -= 1
		# LDI COMMAND
		elif instr.cmd == "LDI":
			top += 1
			stack[top] = stack[stack[Base(instr.statLinks, base) + instr.value]]
		# LDA COMMAND
		elif instr.cmd == "LDA":
			top += 1
			stack[top] = Base(instr.statLinks, base) + instr.value  # end mod
		# STO COMMAND
		elif instr.cmd == "STO":
			stack[Base(instr.statLinks, base) + instr.value] = stack[top]
			top -= 1
		# CAL COMMAND
		elif instr.cmd == "CAL":
			stack[top + 1] = Base(instr.statLinks, base)
			stack[top + 2] = base
			stack[top + 3] = pos
			base = top + 1
			pos = instr.value
		# INT COMMAND
		elif instr.cmd == "INT":
			top = top + instr.value
		# JMP COMMAND
		elif instr.cmd == "JMP":
			pos = instr.value
		# JPC COMMAND
		elif instr.cmd == "JPC":
			if stack[top] == instr.statLinks:
				pos = instr.value
			top -= 1
		if pos == 0:
			break
		# begin mod
		#     CTS COMMAND
		elif instr.cmd == "CTS":
			top += 1
			stack[top] = stack[top - 1]
			continue
		# end mod
		elif instr.cmd == "CBG":  # just to show in the pcode
			continue
		elif instr.cmd == "CND":  # co end
			for i in range(counter,total_threads):
				thread_array[i] = threading.Thread()
				thread_array[i].start()
				try:
					thread_array[counter].sleep(1)
				except IntException as err:
					print("Thread was interrupted")
			while True:
				for i in range(counter,total_threads):
					if thread_array[i].isAlive():
						running = 1
				if running > 0:
					running = 0
				else:
					break
			counter = 0
			total_threads = 0
			thread_array = []
		elif instr.cmd == "FRK":
			temp_stack = stack
			
			temp = threadStruct(instr.value, top, Base(instr.statLinks, base), base, pos, temp_stack, stack)
			thTable.append(temp)
			counter += 1
	print "End PL/0"


# --------------Error Messages----------------------------------------------------------
def error(num):
	global errorFlag;
	errorFlag = 1
	print
	if num == 1:
		print >> outfile, "Use = instead of :="
	elif num == 2:
		print >> outfile, "= must be followed by a number."
	elif num == 3:
		print >> outfile, "Identifier must be followed by ="
	elif num == 4:
		print >> outfile, "Const, Var, Procedure must be followed by an identifier."
	elif num == 5:
		print >> outfile, "Semicolon or comman missing"
	elif num == 6:
		print >> outfile, "Incorrect symbol after procedure declaration."
	elif num == 7:
		print >> outfile, "Statement expected."
	elif num == 8:
		print >> outfile, "Incorrect symbol after statment part in block."
	elif num == 9:
		print >> outfile, "Period expected."
	elif num == 10:
		print >> outfile, "Semicolon between statements is missing."
	elif num == 11:
		print >> outfile, "Undeclared identifier"
	elif num == 12:
		print >> outfile, "Assignment to a constant or procedure is not allowed."
	elif num == 13:
		print >> outfile, "Assignment operator := expected."
	elif num == 14:
		print >> outfile, "call must be followed by an identifier"
	elif num == 15:
		print >> outfile, "Call of a constant or a variable is meaningless."
	elif num == 16:
		print >> outfile, "Then expected"
	elif num == 17:
		print >> outfile, "Semicolon or end expected. "
	elif num == 18:
		print >> outfile, "DO expected"
	elif num == 19:
		print >> outfile, "Incorrect symbol following statement"
	elif num == 20:
		print >> outfile, "Relational operator expected."
	elif num == 21:
		print >> outfile, "Expression must not contain a procedure identifier or function identifier"
	elif num == 22:
		print >> outfile, "Right parenthesis missing"
	elif num == 23:
		print >> outfile, "The preceding factor cannot be followed by this symbol."
	elif num == 24:
		print >> outfile, "An expression cannot begin with this symbol."
	elif num == 25:
		print >> outfile, "Constant or Number is expected."
	elif num == 26:
		print >> outfile, "This number is too large."
	elif num == 27:
		print >> outfile, "Left parenthesis missing"
	elif num == 28:
		print >> outfile, "Expected TO or DOWNTO keyword"
	elif num == 29:
		print >> outfile, "Error: Expected OF keyword"
	elif num == 30:
		print >> outfile, "Error: Expected a Number or Identifier"
	elif num == 31:
		print >> outfile, "Error: Identifier must be a constant"
	elif num == 32:
		print >> outfile, "Expected colon"
	elif num == 33:
		print >> outfile, "Expected semicolon"
	elif num == 34:
		print >> outfile, "Expected UNTIL keyword"
	elif num == 35:
		print >> outfile, "Expected identifier"
	elif num == 36:
		print >> outfile, "Variable expected or variable undeclared"
	elif num == 37:
		print >> outfile, "Expected CEND keyword"
	elif num == 38:
		print >> outfile, "Must be inside function body"
	elif num == 39:
		print >> outfile, "Must be function"
	elif num == 40:
		print>> outfile, "Not value or reference"
	elif num == 41:
		print>> outfile, "Must be procedure"
	exit(0)


# ---------------Alt Errors---------------------------------
def altError(num):
	print
	if num == 1:
		print >> outfile, "sym is not in First"
	elif num == 2:
		print >> outfile, "sym is not in Follow"


# ---------GET CHARACTER FUNCTION-------------------------------------------------------------------
def getch():
	global whichChar, ch, linelen, line;
	if whichChar == linelen:  # if at end of line
		whichChar = 0
		line = infile.readline()  # get next line
		linelen = len(line)
		sys.stdout.write(line)
	if linelen != 0:
		ch = line[whichChar]
		whichChar += 1
	return ch


# ----------GET SYMBOL FUNCTION---------------------------------------------------------------------
def getsym():
	global charcnt, ch, al, a, norw, rword, sym, nmax, id, num
	while ch == " " or ch == "\n" or ch == "\r":
		getch()
	a = []
	if ch.isalpha():
		k = 0
		while True:
			a.append(string.upper(ch))
			getch()
			if not ch.isalnum():
				break
		id = "".join(a)
		flag = 0
		for i in range(0, norw):
			if rword[i] == id:
				sym = rword[i]
				flag = 1
		if flag == 0:  # sym is not a reserved word
			sym = "ident"
	elif ch.isdigit():
		k = 0
		num = 0
		sym = "number"
		while True:
			a.append(ch)
			k += 1
			getch()
			if not ch.isdigit():
				# Added label functionality
				if ch == ':':
					if k <= labelMax:
						sym = "label"
						break;
					else:
						error(31)
						# done adding for label functionality
				else:
					break
		if k > nmax:
			error(30)
		else:
			num = "".join(a)
	elif ch == ':':
		getch()
		if ch == '=':
			sym = "becomes"
			getch()
		else:
			sym = "colon"
	elif ch == '>':
		getch()
		if ch == '=':
			sym = "geq"
			getch()
		else:
			sym = "gtr"
	elif ch == '<':
		getch()
		if ch == '=':
			sym = "leq"
			getch()
		elif ch == '>':
			sym = "neq"
			getch()
		else:
			sym = "lss"
	else:
		sym = ssym[ch]
		getch()


# --------------POSITION FUNCTION----------------------------
def position(tx, id):
	global table;
	table[0] = tableValue(id, "TEST", "TEST", "TEST", "TEST")
	i = tx
	while table[i].name != id:
		i = i - 1
	return i


# ---------------ENTER PROCEDURE-------------------------------
def enter(tx, k, level, dx):
	global id, num, codeIndx;
	tx[0] += 1
	while (len(table) > tx[0]):
		table.pop()
	if k == "const":
		x = tableValue(id, k, level, "NULL", num)
	elif k == "variable" or k == "ref" or k == "val":  # Added value and reference
		x = tableValue(id, k, level, dx, "NULL")
		dx += 1
	elif k == "procedure":
		x = tableValue(id, k, level, dx, "NULL")
	# function added
	elif k == "function":
		x = tableValue(id, k, level, dx, "NULL")
	table.append(x)
	return dx


# -------------Label Declaration-----------
# TODO
def labeldeclaration(tx, level):
	global sym, id, num;

	if sym == "number":
		if sym >= 9999:  # checking here to make sure that label is within 1-9999
			enter(tx, "label", level, "null")
			getsym()
		else:
			error(31)
	else:
		error(2)


# --------------CONST DECLARATION---------------------------
def constdeclaration(tx, level):
	global sym, id, num;
	if sym == "ident":
		getsym()
		if sym == "eql":
			getsym()
			if sym == "number":
				enter(tx, "const", level, "null")
				getsym()
			else:
				error(2)
		else:
			error(3)
	else:
		error(4)


# -------------VARIABLE DECLARATION--------------------------------------
def vardeclaration(tx, level, dx):  # moded
	global sym;
	if sym == "ident":
		dx = enter(tx, "variable", level, dx)
		getsym()
	else:
		error(4)
	return dx


# -------------BLOCK-------------------------------------------------------------
def block(tableIndex, level):
	# took out first
	#	blockFirst_Follow = firstWord()
	#	blockFirst_Follow.first.extend(("VAR", "CONST", "PROCEDURE", "FUNCTION", "IF", "WHILE", "CALL" ,"BEGIN", "IDENT", "PERIOD", "SEMICOLON", "END"))
	#	blockFirst_Follow.follow.extend(("PERIOD", "SEMICOLON"))
	global sym, id, codeIndx, codeIndx0, funcMap;
	tx = [1]
	tx[0] = tableIndex
	tx0 = tableIndex
	dx = 3
	cx1 = codeIndx
	gen("JMP", 0, 0)
	txVal = position(tx0, id)

	# took out first
	#	inFirst = 0
	#	for x in blockFirst_Follow.first:
	#		if sym == x:
	#			inFirst += 1
	#	if inFirst == 0:
	#		print >> outfile, "Block:"
	#		altError(1)
	if (level > 0):  # begin mod
		if level == 1:
			table[txVal].nest = 0
		if sym == "lparen":
			if level == 1:
				table[txVal].nest = 0
			varCnt = 0
			cont = 1
			tempSym = ""
			while (cont == 1):
				getsym()
				if sym == "VAL":
					tempSym = "VAL"
				elif sym == "REF":
					tempSym = "REF"
				else:
					error(40)
				while True:
					getsym()
					if sym != "ident":
						error(35)
					if tempSym == "VAL":
						dx = enter(tx, "val", level, dx)
						table[txVal].params.append(False)
					elif tempSym == "REF":
						dx = enter(tx, "ref", level, dx)
						table[txVal].params.append(True)
					varCnt += 1
					getsym()
					if sym != "comma":
						break
				if sym != "semicolon":
					break

			if table[txVal].kind == "function":
				funcMap.update({table[txVal].name: varCnt})  # begin mod
			if sym != "rparen":
				error(22)
			getsym()
		if sym != "semicolon":
			error(10)
		getsym()
	t = 1  # begin mod for restricted globals
	while (t == 1):
		if sym == "CONST":
			while True:  # makeshift do while in python
				getsym()
				constdeclaration(tx, level)
				if sym != "comma":
					break
			if sym != "semicolon":
				error(10);
			getsym()
		if sym == "VAR":
			while True:
				getsym()
				dx = vardeclaration(tx, level, dx)
				if sym != "comma":
					break
			if sym != "semicolon":
				error(10)
			getsym()
		if sym == "LABEL":
			while True:  # makeshift do while
				getsym()
				labeldeclaration(tx, level)
				if sym != "comma":
					break
			if sym != "semicolon":
				error(10)
			getsym()
		if sym == "label":
			# while True:  # another makeshift do while in python :)
			# TODO finish this mug
			i = position(tx[0], num)
			table[i].adr = codeIndx
			getsym()
			if sym == "colon":  # make sure the next sym is colon
				getsym()  # grab the next instruction
			else:
				error(32)
		while sym == "PROCEDURE" or sym == "FUNCTION":  # mod
			if (level > 0 and txVal != 0):
				table[txVal].nest += 1
			tmpSym = sym
			getsym()
			if sym == "ident":
				if tmpSym == "FUNCTION":  # added function and procedure
					enter(tx, "function", level, codeIndx)
				if tmpSym == "PROCEDURE":
					enter(tx, "procedure", level, codeIndx)
				getsym()
			else:
				error(4)
			block(tx[0], level + 1)
			if sym != "semicolon":
				error(10)
			getsym()
		if sym == "PROCEDURE" or sym == "VAR" or sym == "CONST" or sym == "FUNCTION" or sym == "LABEL":
			t = 1
		else:
			t = 0
	# fix the jump
	fixJmp(cx1, codeIndx)
	if tx0 != 0:
		table[tx0].adr = codeIndx
	codeIndx0 = codeIndx
	gen("INT", 0, dx)
	statement(tx[0], level)
	gen("OPR", 0, 0)
	printCode()


# took out follow
#	inFollow = 0
#	for x in blockFirst_Follow.follow:
#		if sym == x:
#			inFollow += 1
#	if inFollow == 0:
#		print >> outfile, "Block:"
#		altError(2)
# print code for this block


# --------------STATEMENT----------------------------------------
def statement(tx, level):
	caseCount = 0
	global sym, id, num, funcMap;
	# taking out first
	# statementFirst_Follow = firstWord()
	# statementFirst_Follow.first.extend(("IF", "WHILE", "CALL", "BEGIN", "IDENT","PERIOD", "SEMICOLON", "END"))
	# statementFirst_Follow.follow.extend(("PERIOD", "SEMICOLON", "END"))
	# # added 'FUNCTION' to if
	# inFirst = 0
	# for x in statementFirst_Follow.first:
	#     if sym == x:
	#         inFirst+=1
	# if inFirst == 0:
	#     print >> outfile, "Statement:"
	#     altError(1)
	if sym == "label":  # putting this in here for to allow  begin to use a label
		# while True:  # another makeshift do while in python :)
		# TODO finish this mug
		i = position(tx, num)  # tx[0] must be in block and tx in every other use of it (for label that is)
		table[i].adr = codeIndx
		getsym()
		if sym != "colon":  # make sure the next sym is colon
			error(32)  # grab the next instruction
		getsym()
		statement(tx, level)

	elif sym == "RETURN":
		while sym != "END":
			getsym()
			if sym == "END":  # if the sym is equal to the end we will fix the jump and opr 0,0
				cx1 = codeIndx0
				fixJmp(cx1, codeIndx)
				gen("OPR", 0, 0)

	elif sym == "GOTO":
		getsym()  # grab next sym
		if sym != "number":  # making sure the sym is a number. Labels are numbers
			error(25)
		i = position(tx, num)  # grabbing the position
		if table[i].adr == "NULL":  # says it is not in the table yet
			while sym != "label":
				getsym()
				statement(tx, level)
			table[i].adr = codeIndx
			if sym != "colon":
				error(32)
			getsym()
		gen("JMP", 0, table[i].adr)
		getsym()

	if sym == "ident" or sym == "FUNCTION" or sym == "REF" or sym == "VAL":  # added ref and val
		i = position(tx, id)
		if i == 0:
			error(11)
		else:
			if (table[i].kind != "variable" and table[i].kind != "function" and table[
				i].kind != "ref" and table[i].kind != "val"):
				error(12)
		tmpKind = table[i].kind
		getsym()
		if sym != "becomes":
			error(13)
		getsym()
		expression(tx, level)
		if (tmpKind == "variable" or tmpKind == "val"):
			gen("STO", level - table[i].level, table[i].adr)
		if (tmpKind == "function"):
			if (i == (tx - funcMap[table[i].name]) - table[i].nest):
				gen("STO", 0, -1)
			else:
				error(38)  # this must be in function body
		if (tmpKind == "ref"):
			gen("STI", level - table[i].level, table[i].adr)
	elif sym == "CALL":
		getsym()
		if sym != "ident":
			error(14)
		i = position(tx, id)
		if i == 0:
			error(11)
		if table[i].kind != "procedure":
			error(41)
		getsym()
		if (sym == "lparen"):
			con = 1
			numParams = 0
			gen("INT", 0, 3)
			while con == 1:
				getsym()
				if (sym == "ident" and table[i].params[numParams] == True):
					j = position(tx, id)  # check for val or variable and ref down below
					if table[j].kind == "val" or table[j].kind == "variable":
						gen("LDA", level - table[j].level, table[j].adr)
					if table[j].kind == "ref":
						gen("LOD", level - table[j].level, table[j].adr)
					getsym()
				else:
					expression(tx, level)
				numParams += 1
				if sym != "comma":
					con = 0
			gen("INT", 0, -(3 + numParams))
			if sym != "rparen":
				error(22)
			getsym()
		gen("CAL", level - table[i].level, table[i].adr)
	# begin mod
	elif sym == "IF":
		getsym()
		generalExpression(tx, level)
		cx1 = codeIndx
		gen("JPC", 0, 0)
		if sym != "THEN":
			error(16)
		getsym()
		statement(tx, level)
		if sym == "ELSE":  # added ELSE
			cx2 = codeIndx
			gen("JMP", 0, 0)
			fixJmp(cx1, codeIndx)
			getsym()
			statement(tx, level)
			fixJmp(cx2, codeIndx)
		else:
			fixJmp(cx1, codeIndx)
	elif sym == "BEGIN":
		while True:
			getsym()
			statement(tx, level)
			if sym != "semicolon":
				break
		if sym != "END":
			error(17)
		getsym()
	# ADDED COBEGIN
	elif sym == "COBEGIN":
		counter = 0
		gen("CBG", 0, 0)
		while True:
			getsym()
			if(id == "COEND"):
				getsym();
				break;
				
			if (sym == "ident"):
				i = position(tx, id)
				if (i == 0):
					error(11)
				else:
					if (table[i].kind != "procedure"):
						error(15)
				counter = 0
				getsym()
				if sym == "lparen":
					con = 1
					numParams = 0  # parameter counter
					gen("INT", 0, 3)
					while con == 1:
						getsym()
						if (sym == "ident" and table[i].params[numParams] == True):
							k = position(tx, id)
							if table[k].kind == "val" or table[k].kind == "variable":
								gen("LDA", level - table[k].level, table[k].adr)
							if table[k].kind == "ref":
								gen("LOD", level - table[k].level, table[k].adr)
							getsym()
						else:
							expression(tx, level)
						numParams += 1
						if sym != "comma":
							break
					gen("INT", 0, -(3 + numParams))
					if sym != "rparen":
						error(22)
					getsym()
				gen('FRK', level - table[i].level, table[i].adr)
			else:
				error(14)  # TODO CHANGE ERROR
			if (sym != "semicolon"):
				break
			gen('CND', 0, 0)

	elif sym == "WHILE":
		getsym()
		cx1 = codeIndx
		generalExpression(tx, level)
		cx2 = codeIndx
		gen("JPC", 0, 0)
		if sym != "DO":
			error(18)
		getsym()
		statement(tx, level)
		gen("JMP", 0, cx1)
		fixJmp(cx2, codeIndx)
	# begin mod
	elif sym == "REPEAT":
		cx1 = codeIndx
		while True:
			getsym()
			statement(tx, level)
			if (sym != "semicolon"):
				break
		# getsym()
		if (sym != "UNTIL"):
			error(34)
		getsym()
		generalExpression(tx, level)
		gen("JPC", 0, cx1)
	# end mod
	# begin mod
	elif sym == "FOR":
		getsym()
		if (sym != "ident"):
			error(35)
		i = position(tx, id)
		if (i == 0):
			error(11)  # check if in table
		if (table[i].kind != "variable"):
			error(36)
		getsym()
		if (sym != "becomes"):
			error(13)
		getsym()
		expression(tx, level)
		gen("STO", level - table[i].level, table[i].adr)
		if not ((sym == "TO") or (sym == "DOWNTO")):
			error(28)
		# saving the sym in a temp sym
		tempSym = sym
		getsym()
		expression(tx, level)
		cx1 = codeIndx
		gen("CTS", 0, 0)
		gen("LOD", level - table[i].level, table[i].adr)
		if (tempSym == "TO"):
			gen("OPR", 0, 11)
		if (tempSym == "DOWNTO"):
			gen("OPR", 0, 13)
		cx2 = codeIndx
		gen("JPC", 0, 0)
		if (sym != "DO"):
			error(18)
		getsym()
		statement(tx, level)
		gen("LOD", level - table[i].level, table[i].adr)
		gen("LIT", 0, 1)
		if (tempSym == "TO"):
			gen("OPR", 0, 2)
		if (tempSym == "DOWNTO"):
			gen("OPR", 0, 3)
		gen("STO", level - table[i].level, table[i].adr)
		gen("JMP", 0, cx1)
		fixJmp(cx2, codeIndx)
		gen("INT", 0, -1)
	elif sym == "CASE":  # begin mod
		getsym()
		expression(tx, level)

		if (sym != "OF"):
			error(29)
		getsym()
		while (sym == "number" or sym == "ident"):
			caseCount += 1
			if sym == "ident":
				pos = position(tx, id)
				if pos == 0:
					error(11)
				if not (table[pos].kind == "const"):
					error(25)
				gen("CTS", 0, 0)
				gen("LIT", 0, table[pos].value)
				gen("OPR", 0, 8)
				cx1 = codeIndx
				gen("JPC", 0, 0)
				getsym()
				if not (sym == "colon"):
					error(32)
				getsym()
			else:
				gen("CTS", 0, 0)
				gen("LIT", 0, num)
				gen("OPR", 0, 8)
				cx1 = codeIndx
				gen("JPC", 0, 0)
				getsym()
				if not (sym == "colon"):
					error(32)
				getsym()

			statement(tx, level)
			if not (sym == "semicolon"):
				error(33)
			getsym()
			if caseCount == 1:
				cx2 = codeIndx
				gen("JMP", 0, 0)
			else:
				gen("JMP", 0, cx2)
				fixJmp(cx1, codeIndx)

		if not (sym == "CEND"):
			error(37)
		fixJmp(cx2, codeIndx)
		gen("INT", 0, -1)
		getsym()
	elif (sym == "WRITE" or sym == "WRITELN"):
		tempSym = sym
		getsym()
		if (sym != "lparen"):
			error(27)
		while True:
			getsym()
			expression(tx, level)
			gen("OPR", 0, 14)
			if (sym != "comma"):
				break
		if (sym != "rparen"):
			error(22);
		if (tempSym == "WRITELN"):
			gen("OPR", 0, 15)
		getsym()  # end mod


# --------------EXPRESSION--------------------------------------
def expression(tx, level):
	global sym;
	# took out first
	# expFirst_Follow =firstWord()
	#
	# expFirst_Follow.first.extend(("PLUS", "MINUS", "IDENT", "NUMBER", "LPAREN", "CALL", "NOT"))
	# expFirst_Follow.follow.extend(("PERIOD", "SEMICOLON", "END" ,"THEN" ,"DO", "RPAREN", "NE", "LT", "GT", "LTE", "GTE", "EQUAL"))
	# #this is for first checking
	# inFirst = 0
	# for x in expFirst_Follow.first:
	#     if sym == x:
	#         inFirst+=1
	# if inFirst == 0:
	#     print >> outfile, "Expression:"
	#     altError(1)

	if sym == "plus" or sym == "minus":
		tmpOp = sym
		getsym()
		term(tx, level)
		if (tmpOp == "minus"):  # if subtraction, do neg. OP
			gen("OPR", 0, 1)
	else:
		term(tx, level)

	while sym == "plus" or sym == "minus" or sym == "OR":
		tmpOp = sym
		getsym()
		term(tx, level)

		if (tmpOp == "minus"):
			gen("OPR", 0, 3)  # subtraction opcode
		else:
			gen("OPR", 0, 2)  # addition opcode and OR


# taking out follow
#	inFollow = 0
#	for x in expFirst_Follow.follow:
#		if sym == x:
#			inFollow += 1
#	if inFollow == 0:
#		print >> outfile, "Expression:"
#		altError(2)





# -------------TERM----------------------------------------------------
def term(tx, level):
	global sym;

	# took out first
	# termFirst_Follow = firstWord()
	# termFirst_Follow.first.extend(("IDENT", "NUMBER", "LPAREN", "CALL", "NOT"))
	# termFirst_Follow.follow.extend((
	#                                "PERIOD", "SEMICOLON", "END", "THEN", "DO", "RPAREN", "NE", "LT", "GT", "LTE", "GTE",
	#                                "EQUAL", "PLUS", "MINUS", "OR"))
	# # this is for first checking
	# inFirst = 0
	# for x in termFirst_Follow.first:
	#     if sym == x:
	#         inFirst += 1
	# if inFirst == 0:
	#     print >> outfile, "Term:"
	#     altError(1)
	factor(tx, level)
	while sym == "times" or sym == "slash" or sym == "AND":  # added "AND"
		andOp = sym
		getsym()
		factor(tx, level)
		# added "AND"
		if andOp == "times" or andOp == "AND":
			gen("OPR", 0, 4)  # multiplication opcode for "AND" too
		else:
			gen("OPR", 0, 5)  # division opcode

			# took out follow
			# inFollow = 0
			# for x in termFirst_Follow.follow:
			#     if sym == x:
			#         inFollow += 1
			# if inFollow == 0:
			#     print >> outfile, "Term:"
			#     altError(2)


# -------------FACTOR--------------------------------------------------
def factor(tx, level):  # begin mod
	global sym, num, id;
	if sym == "ident" or sym == "VAL" or sym == "REF":
		i = position(tx, id)
		if i == 0:
			error(11)
		if table[i].kind == "const":
			gen("LIT", 0, table[i].value)
		# checking for ref
		elif table[i].kind == "ref":
			gen("LDI", level - table[i].level, table[i].adr)
		# checking for val. Added it to the varible type
		elif table[i].kind == "variable" or table[i].kind == "val":
			gen("LOD", level - table[i].level, table[i].adr)
		# adding to through an error if it is a procedure or function in factor
		elif table[i].kind == "procedure" or table[i].kind == "function":
			error(21)
		getsym()
	elif sym == "number":
		gen("LIT", 0, num)
		getsym()
	elif sym == "NOT":
		getsym()
		factor(tx, level)
		gen("LIT", 0, 0)
		gen("OPR", 0, 8)  # =
	elif sym == "CALL":
		getsym()  # call -> ident
		i = position(tx, id)
		if i == 0:
			error(11)
		if sym != "ident":
			error(35)  # expected identifier
		if table[i].kind != "function":
			error(39)
		getsym()
		gen("INT", 0, 1)
		if sym == "lparen":
			con = 1
			numParams = 0  # parameter counter
			gen("INT", 0, 3)
			while con == 1:
				getsym()
				if (sym == "ident" and table[i].params[numParams] == True):
					j = position(tx, id)
					if table[j].kind == "val" or table[j].kind == "variable":
						gen("LDA", level - table[j].level, table[j].adr)
					if table[j].kind == "ref":
						gen("LOD", level - table[j].level, table[j].adr)
					getsym()
				else:
					expression(tx, level)
				numParams += 1
				if sym != "comma":
					break
			gen("INT", 0, -(3 + numParams))
			if sym != "rparen":
				error(22)
			getsym()
		gen("CAL", level - table[i].level, table[i].adr)
	elif sym == "lparen":
		getsym()
		generalExpression(tx, level)
		if sym != "rparen":
			error(22)
		getsym()
	else:
		error(24)  # end mod


# -----------GENERAL EXPRESSION-------------------------------------------------
def generalExpression(tx, level):  # changed from condition

	# took out first
	# genExpFirst_Follow = firstWord()
	# genExpFirst_Follow.first.extend(("ODD" ,"PLUS" ,"MINUS", "IDENT" ,"NUMBER" ,"LPAREN" ,"CALL" ,"NOT" ))
	# genExpFirst_Follow.follow.extend(("THEN", "DO"))
	# global sym;
	# # this is for first checking
	# inFirst = 0
	# for x in genExpFirst_Follow.first:
	#     if sym == x:
	#         inFirst += 1
	# if inFirst == 0:
	#     print >> outfile, "Gen Expression:"
	#     altError(1)

	if sym == "ODD":
		getsym()
		expression(tx, level)
		gen("OPR", 0, 6)
	else:
		expression(tx, level)
		if (sym in ["eql", "neq", "lss", "leq", "gtr", "geq"]):
			# else:
			temp = sym
			getsym()
			expression(tx, level)
			if temp == "eql":
				gen("OPR", 0, 8)
			elif temp == "neq":
				gen("OPR", 0, 9)
			elif temp == "lss":
				gen("OPR", 0, 10)
			elif temp == "geq":
				gen("OPR", 0, 11)
			elif temp == "gtr":
				gen("OPR", 0, 12)
			elif temp == "leq":
				gen("OPR", 0, 13)
				# took out follow
				# inFollow =0
				# for x in genExpFirst_Follow.follow:
				#     if sym == x:
				#         inFollow+=1
				# if inFollow == 0:
				#     print >> outfile, "Gen Expression:"
				#     altError(2)


# -------------------MAIN PROGRAM------------------------------------------------------------#
rword.append('BEGIN')
rword.append('CALL')
rword.append('CONST')
rword.append('VAL')  # added val
rword.append('REF')  # added ref
rword.append('LABEL')
rword.append('GOTO')
rword.append('HALT')
rword.append('RETURN')
rword.append('DO')
rword.append('END')
rword.append('IF')
rword.append('ODD')
rword.append('PROCEDURE')
rword.append('FUNCTION')
rword.append('THEN')
rword.append('VAR')
rword.append('WHILE')
rword.append('ELSE')
rword.append('REPEAT')
rword.append('UNTIL')
rword.append('FOR')
rword.append('TO')
rword.append('DOWNTO')
rword.append('CASE')
rword.append('OF')
rword.append('CEND')
rword.append('WRITE')
rword.append('WRITELN')
rword.append('AND')
rword.append('NOT')
rword.append('OR')
rword.append('COBEGIN')
rword.append('COEND')

ssym = {'+': "plus",
		'-': "minus",
		'*': "times",
		'/': "slash",
		'(': "lparen",
		')': "rparen",
		'=': "eql",
		',': "comma",
		'.': "period",
		'#': "neq",
		'<': "lss",
		'>': "gtr",
		'"': "leq",
		'@': "geq",
		';': "semicolon",
		':': "colon", }
charcnt = 0
whichChar = 0
linelen = 0
ch = ' '
funcMap = {}  # mod
kk = al
a = []
id = '     '
errorFlag = 0
table.append(0)  # making the first position in the symbol table empty
sym = ' '
codeIndx = 0  # first line of assembly code starts at 1
prevIndx = 0
infile = sys.stdin  # path to input file
outfile = sys.stdout  # path to output file, will create if doesn't already exist

getsym()  # get first symbol
block(0, 0)  # call block initializing with a table index of zero
if sym != "period":  # period expected after block is completed
	error(9)
print
if errorFlag == 0:
	print >> outfile, "Successful compilation!\n"

Interpret()
