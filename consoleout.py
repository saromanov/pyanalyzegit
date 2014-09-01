'''
	Output for console view
'''

import builtins

def tableOutput(data):
	if len(data) == 0:
		raise "Data contain zero elements"
	print('ELEMENTS: ')
	for value in data:
		print('  '.join(map(lambda x: str(x), value)))
	print('End of elements', ...)


def infoOutput(data):
	'''
		Outout for some statistical information
	'''
	pass
