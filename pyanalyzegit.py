import pbs
import numpy
import nltk
import math

#https://pypi.python.org/pypi/pbs

class ExtendGit:
	def __init__(self):
		self.git = pbs.git

	def branch(self):
		''' get a current branch'''
		return self.git("branch").split()[1]

	def commit(self, value):
		self.git("commit" + value)

	#Use infromation from basic git log command
	def log(self, *args, **kwargs):
		#Append git log patch
		data = self.git("log", ("--numstat")).split('\n')
		return GitLogAnalyzer(data)


class ChangedFiles:
	def __init__(self, count, value):
		self.count = count
		self.value = value

#http://git-scm.com/docs/git-log
#dirstat = pbs.git("log", ("--dirstat"))
#Show source --ignore-all-space 
#binary = pbs.git("log", ("--binary"))
class GitLogAnalyzer:
	def __init__(self, data):
		self._result = self._parseResult(data)

	def _parseResult(self, data):
		result = []
		commits = {}
		for d in range(len(data)):
			value = data[d].split('\n')
			for j in range(len(value)):
				if value[j].startswith('Author') and 'Author' not in commits:
					commits['Author'] = self._cleardata(value[j], 'Author')
					#print(value[j].split('Author')[1:])
				elif value[j].startswith('Date') and 'Date' not in commits:
					commits['Date'] = self._cleardata(value[j], 'Date')
				elif value[j].startswith('commit'):
					if len(commits) > 0:
						result.append(commits)
					commits = {}
					commits['Commit'] = self._cleardata(value[j], 'commit')
				elif len(value[j]) > 0:
					if value[j].startswith(' '):
						commits['CommitTitle'] = value[j].replace('  ','')
					else:
						commits['Files'] = value[j].split()
		return result

	def _cleardata(self, data, param):
		return data.split(param)[1:][0]

	def analyze(self, func):
		'''
			User function for filter target results
		'''
		return list(filter(func, self.result))


	def mostchangingfiles(self, limit=1):
		'''
			Get most changing files in project
		'''
		files = {}
		for commit in self._result:
			f = commit['Files']
			add = int(f[0])
			rem = int(f[1])
			if f[2] not in files:
				files[f[2]] = ChangedFiles(1, abs(add - rem))
			else:
				cf = files[f[2]]
				files[f[2]] = ChangedFiles(cf.count+1, cf.value + abs(add-rem))
		f = sorted(files.items(), key=lambda x: x[1].count, reverse=True)
		return f

ex = ExtendGit()
print(ex.log().mostchangingfiles())