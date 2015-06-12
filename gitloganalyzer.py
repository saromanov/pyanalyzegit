from abc import ABCMeta, abstractmethod
from collections import Counter


class AbstractAnalyze(metaclass=ABCMeta):

    @abstractmethod
    def analyze(self, func):
        '''
            User analyze method with data
        '''
        pass


class ChangedFiles:

    def __init__(self, count, app, rems, lines):
        self.count = count
        self.app = app
        self.rems = rems
        self.lines = lines


class EventData:
    def __init__(self, commit):
        self.message = commit.summary
        self.date = commit.committed_date
        self.insertions = commit.stats.total['insertions']
        self.deletions = commit.stats.total['deletions']
        self.total = self.insertions + self.deletions


class GitLogAnalyzer(AbstractAnalyze):

    def __init__(self, data):
        self.commits = data

    def analyze(self, func):
        '''
            User function for filter target results
        '''
        return list(filter(func, self.result))

    def _parseIntData(self, add, rem):
        try:
            add = int(add)
            rem = int(rem)
            return add, rem
        except Exception:
            return 0, 0

    def mostChangedFiles(self, limit=1):
        '''
            Get most modified files in project
            return dict of number of file: {count: Number of changes, insertions: Number of insertions, deletions: Number of deletions}
        '''
        files = {}
        for commit in self.commits:
            stat = commit.stats.files
            commit_files = list(stat.keys())
            for comfile in commit_files:
                insert = stat[comfile]['insertions']
                dels = stat[comfile]['deletions']
                lines = stat[comfile]['lines']
                if comfile not in files:
                    files[comfile] = ChangedFiles(1, insert, dels, lines)
                else:
                    current = files[comfile]
                    files[comfile] = ChangedFiles(
                        current.count + 1, current.app + insert, current.rems + dels, current.lines + lines)
        filessorted = sorted(
            files.items(), key=lambda x: x[1].count, reverse=True)
        result = map(lambda data: (data[0], {'count': data[1].count,
                                             'insertions': data[1].app, 'deletions': data[1].rems}), filessorted)
        return dict(result)

    def _getFileName(self, path):
        nums = path.split('/')
        return nums[len(nums) - 1]

    def wordsAddRemInfo(self):
        '''
            Most change in files
        '''
        result = []
        for s in self._result:
            for f in s['Files']:
                add = f[0]
                rem = f[1]
                zdata = (add + rem)
                if zdata != 0:
                    result.append((f[2], (add - rem) / (add + rem)))
        return result

    def getFunctionNames(self, lang):
        if lang == 'python':
            return PySourceAnalyzer(self._result)
        if lang == 'js':
            return JavaScriptSourceAnalyzer(self._result)
        raise Exception("This language is not supported")

    def getAuthorsStat(self):
        ''' Return {git.Actor: number of commits}
        '''
        return dict(Counter([commit.author for commit in self.commits]))


    def getBigEvents(self, count=5):
        ''' This method returns list of commits with large numbers of insertions or deletions
            count - number of big events
        '''
        return list(reversed(sorted([EventData(commit) for commit in self.commits], key=lambda x: x.total)))

    def getCommitsByWord(self, word):
        ''' This method returns list of commits where contains target word'''
        return [commit for commit in self.commits if commit.message.find(word) != -1]


    def checkBug(self):
        '''
            Get author of bug
        '''
        return None

    def showChangingFiles(self, func=None):
        '''
          Plot data about append and removed lines
        '''
        data = self._collectData(func)
        keys = data.keys()
        a = list(map(data[_]['a'], keys))
        r = list(map(data[_]['r'], keys))
        self.s.barplot_commits(a, r, list(data.keys()))

    def showCommitsByDate(self, func=None):
        '''
            Plot data about commits
        '''
        from time import mktime, time, strptime
        import datetime
        dates = list(map(lambda x: x['Date'], self.getCommits()))
        cd = clearDates(dates)

        result = map(lambda x:
                     datetime.datetime.fromtimestamp(mktime(strptime(x, '%a %b %d %H:%M:%S %Y '))), cd)
        d, c = countCommitsByDate(result)
        self.s.showByDate(d, c)

    def commentsFromCommit(self):
        return self.glog.getComments()
