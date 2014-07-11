import pbs
import numpy
import math

import show

#https://pypi.python.org/pypi/pbs

AUTHOR = 'Author'
DATE = 'Date'
COMMIT = 'commit'

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

#This is inner class, not in API
class GitLogAnalyzer:
	def __init__(self, data):
		'''
			Parse results from pbs call
			For example: GitLogAnalyzer(self.git("log", ("--numstat")).split('\n'))
		'''
		self._result = self._parseResult(data)
		s = show.Show()

	def _parseResult(self, data):
		''' 
			Get some ordered data from pbs
		'''
		result = []
		commits = {}
		cleardata = self._cleardata
		for d in data:
			cands = d.split('\n')
			for cand in cands:
				if cand.startswith(AUTHOR) and AUTHOR not in commits:
					commits[AUTHOR] = cleardata(cand, AUTHOR)
				elif cand.startswith(DATE) and DATE not in commits:
					commits[DATE] = cleardata(cand, DATE)
				elif cand.startswith(COMMIT):
					if len(commits) > 0:
						result.append(commits)
					commits = {}
					commits['Commit'] = cleardata(cand, COMMIT)
				elif len(cand) > 0:
					if cand.startswith(' '):
						commits['CommitTitle'] = cand.replace('  ','')
					else:
						if 'Files' not in commits:
							commits['Files'] = []
						commits['Files'].append(self._prepareFiles(cand))
		return result

	def _cleardata(self, data, param):
		return data.split(param)[1:][0]

	def _prepareFiles(self, value):
		'''
		  Convert append and removed lines in int type
		  And output with filename
		'''
		return list(map(lambda x: x if x.isdigit() == False else int(x), value.split()))

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
		return sorted(files.items(), key=lambda x: x[1].count, reverse=True)


	def getCommits(self):
		return self._result

	def _collectData(self, func=None):
		files = {}
		for data in self._result:
			for f in data['Files']:
				if f[0] < 1000:
					name = self._getFileName(f[2])
					if name not in files:
						files[name] = {'a':f[0], 'r':f[1]}
					else:
						value = files[name]
						files[name] = {'a': value['a'] + f[0], 'r': value['r'] + f[1]}
		return files

	def _getFileName(self, path):
		nums = path.split('/')
		return nums[len(nums)-1]


	def wordsAddRemInfo(self):
		words = self._collectWords(self._result)
		result = []
		for s in self._result:
			for f in s['Files']:
				add = f[0]
				rem = f[1]
				result.append((f[2], (add-rem)/(add+rem)))
		return result

	def _collectWords(self, data):
		words = {}
		for d in data:
			for w in d['CommitTitle'].split():
				if not(w in words):
					words[w] = 0
				else:
					words[w] += 1
		return words

	def showChangingFiles(self, func=None):
		'''
		  Plot data about append and removed lines
		'''
		data = self._collectData(func)
		keys = data.keys()
		a = list(map(lambda x: data[x]['a'], keys))
		r = list(map(lambda x: data[x]['r'], keys))
		s.barplot_commits(a, r, list(data.keys()))

	def showCommitsByDate(self, func=None):
		from time import mktime, time, strptime
		import datetime
		result = map(lambda x: 
			datetime.datetime.fromtimestamp(mktime(strptime(x['Date'], '"%Y-%m-%d %H:%M"'))),self.getCommits())
		#s.showByDate(self.getCommits())
