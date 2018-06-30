# -*- encoding: utf-8 -*-
import json

debug = True


def dprint(message):
	if debug:
		return message


class Atom:
	def __init__(self, x, y, z, name, mass):
		self.x = x
		self.y = y
		self.z = z
		self.name = name
		self.mass = mass


atomChunk = """
<div class="atomView" onclick="selectAtom([[id]])" id="atomView_[[id]]">
	<div class="id">[[id]]: </div>
	<div class="name">[[name]]</div>
	<div class="devider"></div>
	<div class="x" contenteditable>x: [[x]]</div>
	<div class="y" contenteditable>y: [[y]]</div>
	<div class="z" contenteditable>z: [[z]]</div>
</div>
"""


def atoms2json(atom_list):
	ans = ""
	index = 0
	json_string = ""
	for atom in atom_list:
		new_txt = atomChunk.replace("[[id]]", str(index))
		new_txt = new_txt.replace("[[x]]", str(atom.x))
		new_txt = new_txt.replace("[[y]]", str(atom.y))
		new_txt = new_txt.replace("[[z]]", str(atom.z))
		new_txt = new_txt.replace("[[name]]", str(atom.name))
		ans += new_txt
		index += 1
		if index == 1:
			json_string += json.dumps(atom.__dict__)
		else:
			json_string += "," + json.dumps(atom.__dict__)

	# return ans

	return "[" + json_string + "]"
