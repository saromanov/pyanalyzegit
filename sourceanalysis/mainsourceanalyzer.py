class MainSourceAnalyzer:
	def __init__(self, data):
		self._result = self._parseResult(data)

	def _parseResult(self, data):
		return [value.split() for value in data]

	def getFunctions(self, funcstart, objfunc=None):
		'''
			objfunc - target function
			Probably need to remove
		'''
		FUNCSTART = funcstart
		PLUS = '+'
		REM = '-'
		if objfunc == None:
			''' Get default function '''
			def getFunc(line):
				if len(line) > 1:
					if line[0] == PLUS:
						if line[1] == FUNCSTART:
							return [PLUS, line[2].split('(')[0]]
					if line[1] == REM:
						if line[1] == FUNCSTART:
							return [REM, line[2].split('(')[0]]
			objfunc = getFunc

		for line in self._result:
			result = objfunc(line)
			if result != None:
				yield result

	def grepData(self, keyword):
		import pbs
		return pbs.git('grep', keyword)

	def getCountLinesFuncs(self, startfunc, endfunc):
		#Only functions with return 
		def getFunc(line):
			if startfunc in line:
				return 0
			if endfunc in line:
				return 1
		objfunc = getFunc
		count = 0
		for line in self._result:
			print(line)
			result = objfunc(line)
			if result == 0:
				count = 0
			if result == 1:
				yield count
			else:
				count += 1

	def analyze(self, func):
		return list(filter(func, self._result))

	def _mostOftenHelpful(self, func, fstart):
		try:
			data = self.grepData(func).split('\n')
			return len(list(filter (lambda x: self._mostOftenfilterNames(fstart, x), \
				self.grepData(func + '(').split('\n'))))
		except Exception as e:
			return 0

	def _mostOftenfilterNames(self, funcident, data):
		return data.index(funcident + data) != -1

	def mostOftenFuncs(self, fstart):
		#result = self._mostOftenHelpful('getAuthors', fstart)
		return list(reversed(sorted(\
			list(map(lambda x: (x, self._mostOftenHelpful(x)), 
				set(map(lambda x:x[1], self.getFunctions('def'))))),\
			key=lambda x:x[1])))