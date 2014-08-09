from mainsourceanalyzer import MainSourceAnalyzer

class JavaScriptSourceAnalyzer:
	''' Working with source in JS '''
	def __init__(self, data):
		self._dataobj = MainSourceAnalyzer(data)

	def getFunctions(self, objfunc=None):
		return self._dataobj.getFunctions('function')

	def getCountLinesFuncs(self):
		return self._dataobj.getCountLinesFuncs('function', 'return')

	def analyze(self, func):
		return self._dataobj.analyze(func)