from sourceanalysis.mainsourceanalyzer import MainSourceAnalyzer
from collections import Counter

class PySourceAnalyzer:
	'''
		Analyze append and removed from source
	'''
	def __init__(self, data):
		self._dataobj = MainSourceAnalyzer(data)

	def getFunctions(self, objfunc=None):
		return self._dataobj.getFunctions('def')

	def getFunctionsStat(self):
		keyword = 'def '
		lines = self._dataobj.grepData(keyword).split('\n')
		if len(lines) == 0:
			raise Exception("This data not contain any lines of code")
		count = Counter()
		names = Counter()
		lenfunc = 0
		for line in lines:
			data = line.split(':')
			if len(data) > 1:
				cfunc = data[1][len(keyword) + 1:len(data[1])]
				lenfunc += len(cfunc.split('(')[0])
				count[data[0]] += 1
				names[cfunc] += 1
		return dict(count), round(lenfunc/len(lines)), \
		dict(names)

	def getCountLinesFuncs(self):
		return self._dataobj.getCountLinesFuncs('def', 'return')

	def getCurrentClasses(self):
		return self._dataobj.grepData('class') 

	def analyze(self, func):
		return self._dataobj.analyze(func)
