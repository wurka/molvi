import sys

elements = {
	'H': 0,
	'h': 0,
	'He': 1,
	'he': 1,
	'Li': 2,
	'li': 2,
	'Be': 3,
	'be': 3,
	'B': 4,
	'b': 4,
	'c': 5,
	'C': 5
}

if __name__ == "__main__":
	if len(sys.argv) < 2: 
		print("say element name, e.g. <python mentab.py H> for hydrogenius")
	else:
		if not sys.argv[1] in elements:
			print("no such element ({}) in table".format(sys.argv[1]))
		else:
			print("{} index is: {}".format(sys.argv[1], elements[sys.argv[1]]))
