from django.shortcuts import render
from django.http import HttpResponse
from .views_utils import *
import os
import json
from tkinter import filedialog
from tkinter import Tk


# Create your views here.
def main_page(request):
	return render(request, "editor/molvi.html", {})


def open_file_dialog(request):
	return HttpResponse("OK")


def get_last_mol_file(request):
	ans = ""
	atoms = list()

	# чтение файла currentFile.txt
	try:
		# "./files/2Cl3NTh_mf_cc3_cub.mol"
		path = os.path.abspath("editor/files/currentFile.txt")
		with open(path, encoding="UTF-8") as f:
			file_name = f.read()
	except FileNotFoundError:
		ans += "currentFile.txt not found on server"
		# ans += str(os.listdir())
		return HttpResponse(ans)
	# чтение файла, указанного в currentFile.txt
	try:
		with open(file_name) as f:
			lines = f.readlines()
	except FileNotFoundError as ex:
		ans += "error while reading .mol data. "
		ans += str(ex)
		# ans += str(os.listdir())
		return HttpResponse(ans)

	mode = "scan"  # активный режим работы
	n = len(lines)
	i = 0
	while i < n:  # цикл по строкам файла
		if mode == "end":
			break

		line = lines[i]
		ans += dprint(">> " + line + "<br/>")

		if mode == "scan":
			if "[Atoms]" in line:
				dprint("GO readAtoms")
				mode = "readAtoms"
		elif mode == "readAtoms":  # считывание информации об атомах
			if line.isspace():  # пустая строка - это конец считывания
				# mode = "scan"
				dprint("END: readAtoms: finded end<br/>")
				mode = "end"
				i += 1
				continue
			if line.startswith('//') or line.lower().startswith("length") or line.lower().startswith("count"):
				i += 1
				continue

			elems = line.strip().split(' ')
			elems = list(filter(None, elems))

			first = elems[0]
			try:
				dprint("first: " + str(first) + "<br/>")
				dprint(elems)
				number = int(first)
				dprint("ReadAtom [{}]".format(number))
				ax = float(elems[1])
				dprint("!")
				ay = float(elems[2])
				az = float(elems[3])
				name = elems[4]
				mass = int(elems[5])
				new_atom = Atom(ax, ay, az, name, mass)
				atoms.append(new_atom)

			except ValueError as ex:
				dprint("get_last_mol_file error: " + str(ex))
				mode = "scan"
				continue
		i += 1

	# считывание из файла завершено заполнен список atoms
	ans = atoms2json(atoms)
	return HttpResponse(ans)


def save_document(request):
	ans = "OK"
	if 'document' not in request.POST:
		return HttpResponse("There is no 'document' field in request")

	doc_ajax = request.POST['document']
	doc_dict = json.loads(doc_ajax, encoding='utf-8')
	if ('documentName' not in doc_dict) or ('clusters' not in doc_dict) or ('links' not in doc_dict):
		return HttpResponse("Wrong json structure: documentName, clusters and links must be include")

	# открыть диалог выбора файла
	filename = os.path.join("editor", "files", "documents")
	filename = os.path.abspath(filename)
	# создать папку, если её нет
	if not os.path.exists(filename):
		os.mkdir(filename)
	filename = os.path.join(filename, doc_dict['documentName'] + ".molvidoc")

	if filename == "":
		return HttpResponse("File not selected")
	else:
		try:
			with open(filename, 'wt', encoding='utf-8') as f:
				f.write(doc_ajax)
			return HttpResponse("OK")
		except IOError:
			return HttpResponse("Cann't write to file. System error!")


def get_documents(request):
	doc_dir = os.path.abspath(os.path.join("editor", "files", "documents"))
	ans = json.dumps(os.listdir(doc_dir))
	return HttpResponse(ans)


def get_mol_files(request):
	doc_dir = os.path.abspath(os.path.join("editor", "files", "mols"))
	ans = json.dumps(os.listdir(doc_dir))
	return HttpResponse(ans)


def get_document(request):
	if 'document-name' not in request.GET:
		return HttpResponse("document-name parameter not specified")
	document_name = request.GET['document-name']
	doc_dir = os.path.abspath(os.path.join("editor", "files", "documents"))
	doc_file = os.path.join(doc_dir, document_name)
	try:
		with open(doc_file, 'rt') as f:
			content = f.read()
			return HttpResponse(content)
	except IOError as ex:
		return HttpResponse("Error while file reading: " + str(ex))

