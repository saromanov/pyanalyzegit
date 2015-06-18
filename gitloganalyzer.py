from abc import ABCMeta, abstractmethod
from collections import Counter
import logging
from functools import reduce


logging.basicConfig(
    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)


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

    ''' GitLogAnalyzer provides analysis of log from git
    '''

    def __init__(self, data):
        self.commits = data

    def analyze(self, func):
        '''
            User function for filter target results
        '''
        return list(filter(func, self.result))

    def mostChangedFiles(self, limit=1):
        '''
            Get most modified files in project
            return dict of number of file: {count: Number of changes, insertions: Number of insertions, deletions: Number of deletions}
        '''
        logging.info("Start to getting moct changed files")
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

    def statCommitsByWord(self, word):
        ''' This method returns list of tuples(commit message, total number of insertions, total number of deletions)'''
        return [(commit.message, commit.stats.total['insertions'], commit.stats.total['deletions']) for commit in self.getCommitsByWord(word)]

    def _filterTime(self, commitlist, committime):
        return list(filter(lambda x: x[1].tm_year == committime.year and x[1].tm_mon == committime.month and x[1].tm_mday == committime.day, commitlist))

    def getCommitsByDate(self, committime):
        '''
            Get all commits by date (datetime object)
        '''
        import datetime
        if not isinstance(committime, datetime.datetime):
            logging.error("committime should be in datetime format")
            return
        from time import gmtime
        return self._filterTime([(commit.message, gmtime(commit.committed_date)) for commit in self.commits], committime)

    def getPopularWords(self):
        """
           Get popular words from commits

           Returns:
               List of popular words
        """
        words = [commit.message.split() for commit in self.commits]
        allwords = reduce(list.__add__, words, [])
        return Counter(allwords)
