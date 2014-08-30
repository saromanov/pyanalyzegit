import math
import random

def test1(x):
	return math.fsum(list(map(lambda x: random.randint(0,x), range(1,x))))
