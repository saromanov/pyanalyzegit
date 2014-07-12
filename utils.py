from fn import _, F, underscore

def clearDates(dates):
	'''
		input: list of date from git log
		return 'clear' date without timezone +0000
		example: [  Fri Jul 11 23:58:14 2014 +0600] =>[Fri Jul 11 23:58:14 2014]
	'''

	return list(map(F() << (_.call("replace",':   ','')) << 
			(_.call("split","+")[0]), dates))


def countCommitsByDate(dates):
	'''
		Get list of date (before prepare with ClearDates)
		and return zip with (date, number of commits)
	'''
	result = {}
	for d in dates:
		tup = (d.day, d.month, d.year)
		if tup not in result:
			result[tup] = 1
		else:
			result[tup] += 1
	#return list(zip(result.keys(), result.values()))
	return list(result.keys()), list(result.values())