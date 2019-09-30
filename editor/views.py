# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404
from .views_utils import *
from .mathutils import rotate_by_deg
from .models import Document, Link, Atom, Cluster, ClusterAtom, DihedralAngle, DihedralAngleLink
from .models import ValenceAngle, ValenceAngleLink
from .models import MolFile, MatrixZ
import os
import json
from .geom import Point, Line, Plane
from math import sqrt, pi, acos, degrees, isnan
from django.db.transaction import atomic
from .geom import Quaternion, Point
from pyquaternion import Quaternion as Quater
from re import sub as resub
import numpy as np
import pickle


class MolFileReadingException(Exception):
	message = ""

	def __init__(self, message):
		self.message = message


def angle_from_atoms(atom1, atom2, atom3):
	# вычисление угла, образованного в пространстве атомами atom1, atom2 и atom3
	ax, ay, az = atom1.x - atom2.x, atom1.y - atom2.y, atom1.z - atom2.z
	bx, by, bz = atom3.x - atom2.x, atom3.y - atom2.y, atom3.z - atom2.z
	value = ax * bx + ay * by + az * bz
	moda = sqrt(ax ** 2 + ay ** 2 + az ** 2)
	modb = sqrt(bx ** 2 + by ** 2 + bz ** 2)
	value = value / moda / modb
	value = acos(value) / pi * 180
	return value


# Create your views here.
def main_page(request):
	return render(request, "editor/molvi.html", {})


def open_file_dialog(request):
	return HttpResponse("OK")


def mol_file_data(file_name: str, molfile: MolFile = None):
	"""
	Return Atom array, contains data from .mol file
	with name <file_name>
	:param file_name: name of .mol file
	:param molfile: models.ModelFile object
	:return: json string
	"""
	ans = ""
	atoms = list()
	ValenceAngle.objects.all().delete()
	ValenceAngleLink.objects.all().delete()

	matrix_z_coordinates = "unknown"
	matrix_z_units = "unknown"
	mz_espec = 2
	mz_skipped = False
	mz_cline = 0
	mz_crow = 0
	mz_last_line = 0
	mz_next_column = 0

	matrix_z_lines = list()
	active_doc = None
	atom_number = 1
	try:
		active_doc = Document.objects.get(is_active=True)
		atom_number = len(Atom.objects.filter(document=active_doc)) + 1
	except Document.DoesNotExist:
		pass

	# чтение файла file_name
	try:
		with open(file_name) as f:
			lines = f.readlines()
			f.seek(0)
			text = f.read()
			molfile = MolFile.objects.create(text=text)

	except FileNotFoundError as ex:
		ans += "error while reading .mol data. "
		ans += str(ex)
		# ans += str(os.listdir())
		raise MolFileReadingException("File not found")

	mode = "scan"  # активный режим работы
	n = len(lines)
	i = 0
	while i < n:  # цикл по строкам файла
		i += 1
		if mode == "end":
			break

		line = lines[i-1].split("//")[0]
		if not line:
			continue
		ans += dprint(">> " + line + "<br/>")

		if mode == "scan":
			if "[Atoms]" in line:
				dprint("GO readAtoms")
				mode = "readAtoms"
				continue
			if "[Matrix Z]" in line:
				dprint("Go readMatrixZ")
				mode = "readMatrixZ"
				continue
		if mode == "readMatrixZ":
			if line.isspace():
				continue
			if not line.startswith("[") and i != n:  # not end of readMatrixZ section and not end of file
				matrix_z_lines.append(resub(r"[ \t\r\n]+",  " ", line.replace("\r", "").replace("\n", "")))
			else:  # end of readMatrixZ
				mz_size = len(atoms) * 3
				matrix_z = np.zeros((mz_size, mz_size), dtype=np.float32)

				for mline in matrix_z_lines:
					if mline.startswith("Coordinates="):
						matrix_z_coordinates = mline.split('=')[1]
						continue
					if mline.startswith("Units="):
						matrix_z_units = mline.split('=')[1]
						continue
					splited = list(filter(None, mline.split(" ")))
					if len(splited) != mz_espec:
						if not mz_skipped:  # first time skipped
							mz_skipped = True
							mz_espec -= 1
							mz_last_line = mz_cline
							mz_next_column += len(splited) - 1
						else:  # already skipped
							mz_espec -= 1

					if not mz_skipped:  # normal line
						for ind in range(mz_espec-1):
							val = float(splited[ind+1])
							matrix_z[mz_cline, mz_crow+ind] = val
							matrix_z[mz_crow+ind, mz_cline] = val
						mz_espec += 1
						mz_cline += 1
					else:  # line with skip
						if len(splited) != mz_espec:
							mz_skipped = False
							mz_espec = 2
							mz_cline = mz_last_line
							mz_crow = mz_next_column
							continue
						for ind in range(len(splited) - 1):
							try:
								val = float(splited[ind+1])
								matrix_z[mz_cline, mz_crow + ind] = val
								matrix_z[mz_crow + ind, mz_cline] = val
							except ValueError:
								mz_espec = 2
								continue
						mz_espec += 1
						mz_cline += 1

				# сохранение результатов чтения
				MatrixZ.objects.create(
					owner=molfile,
					coordinates=matrix_z_coordinates,
					units=matrix_z_units,
					data=matrix_z.dumps()
				)

				mode = "scan"

		elif mode == "readAtoms":  # считывание информации об атомах
			if line.isspace():  # пустая строка - это конец считывания
				# mode = "scan"
				dprint("END: readAtoms: finded end<br/>")
				mode = "scan"
				continue
			if line.startswith('//') or line.lower().startswith("length") or line.lower().startswith("count"):
				continue

			elems = line.strip().split(' ')
			elems = list(filter(None, elems))

			first = elems[0]
			try:
				if first == "[Atoms]":
					continue
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
				new_atom = Atom(
					x=ax, y=ay, z=az, name=name, mass=mass, document=active_doc, molfileindex=number)
				new_atom.molfile = molfile
				new_atom.documentindex = atom_number
				atom_number += 1
				new_atom.save()

				if new_atom.name == "H":
					new_atom.valence = 1
					new_atom.mentableindex = 0

				if new_atom.name == "C":
					new_atom.valence = 4
					new_atom.mentableindex = 5

				atoms.append(new_atom)

			except ValueError as ex:
				dprint("get_last_mol_file error: " + str(ex))
				mode = "scan"
				continue
		elif mode == "readMatrixZ":
			pass

	# считывание из файла завершено заполнен список atoms
	# ans = atoms2json(atoms)
	# return ans

	# вернём активный документ
	return atoms


def get_active_data_old(request):
	adoc = Document.objects.get(is_active=True)
	free_atoms = Atom.objects.filter(document=adoc)
	clusters = Cluster.objects.filter(document=adoc)
	atoms = [ClusterAtom.objects.get(claster=c).atom for c in clusters]

	# чтение файла currentFile.txt
	try:
		# "./files/2Cl3NTh_mf_cc3_cub.mol"
		path = os.path.abspath("editor/files/currentFile.txt")
		with open(path, encoding="UTF-8") as f:
			file_name = f.read()
	except FileNotFoundError:
		ans = "currentFile.txt not found on server"
		# ans += str(os.listdir())
		return HttpResponse(ans)
	# обработка файла, указанного в currentFile.txt
	ans = mol_file_data(file_name)
	return HttpResponse(ans)


def get_last_mol_file(request):
	ans = ""

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
	# обработка файла, указанного в currentFile.txt
	ans = json.dumps(mol_file_data(file_name))
	return HttpResponse(ans)


def get_mol_file(request):
	# чтение .mol файла GET['filename']
	if 'filename' not in request.GET:
		return Http404("There is no <filename> parameter!")
	file_name = request.GET['filename']
	mol_dir = os.path.abspath(os.path.join("editor", "files", "mols"))
	file_name = os.path.join(mol_dir, file_name)
	try:
		with open(file_name, "tr") as file:
			text = file.read()
			molfile = MolFile.objects.create(text=text)
			atom_list = mol_file_data(file_name, molfile)
	except Exception as ex:
		return HttpResponse("Error in file reading: " + str(ex))

	return HttpResponse(atom_list)


def save_document(request):
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
	# doc_dir = os.path.abspath(os.path.join("editor", "files", "documents"))
	# ans = json.dumps(os.listdir(doc_dir))
	# return HttpResponse(ans)
	docs = Document.objects.all()
	doc_list = list()
	try:
		for doc in docs:
			doc_list.append({"id": doc.id, "name": doc.name})
		ans = json.dumps(doc_list)
	except Exception as e:
		return HttpResponse("Error: " + str(e), status=500)
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
		with open(doc_file, 'rt', encoding='utf-8') as f:
			content = f.read()
			return HttpResponse(content)
	except IOError as ex:
		return Http404("Error while file reading: " + str(ex))


def harvest_connected(current: list, offs: list, collected: list, all_links: list):
	#  Найти все соединённые атомы
	#  current - список "активных" атомов
	#  offs - исключённые из поиска атомы
	#  collected - "найденные" атомы

	connected = list()  # атомы, соединённые с каждым атомом cur в current

	while len(current) > 0:  # обработаем каждый из указанных атомов
		cur = current[0]
		collected.append(cur)
		current.remove(cur)
		offs.append(cur)  # второй раз не работаем с этим атомом

		for link in all_links:
			if link.atom1 == cur:
				if link.atom2 not in offs:
					connected.append(link.atom2)
			if link.atom2 == cur:
				if link.atom1 not in offs:
					connected.append(link.atom1)

	for x in connected:
		current.append(x)

	if len(current) > 0:
		harvest_connected(current, offs, collected, all_links)
	print("harvest_connected done.")


def rotate_cluster_around_link(request):
	must_be = ("link", "origin-atom", "degrees")
	for must in must_be:
		if must not in request.GET:
			return HttpResponse("there is no parameter: "+must, status=500)

	lid = int(request.GET["link"])
	origin_atom_id = int(request.GET["origin-atom"])
	degrees = float(request.GET["degrees"])

	active_doc = Document.objects.get(is_active=True)
	link = Link.objects.get(id=lid)
	atoms = Atom.objects.filter(document=active_doc)
	current = [link.atom1]
	offs = [link.atom2]
	collected = list()
	all_links = Link.objects.filter(document=active_doc)
	harvest_connected(current, offs, collected, all_links)

	link = Link.objects.get(id=lid)
	oa = Atom.objects.get(id=origin_atom_id)

	if link.atom1.id == origin_atom_id:
		a_from = link.atom1
		a_to = link.atom2
	elif link.atom2.id == origin_atom_id:
		a_from = link.atom2
		a_to = link.atom1
	else:
		return HttpResponse("wrong origin atom", status=500)

	vx, vy, vz = a_to.x - a_from.x, a_to.y - a_from.y, a_to.z - a_from.z

	quat = Quaternion.create_quaternion(vx, vy, vz, degrees/180.0*pi)
	quat.normalize()

	# catoms = collected
	atoms = collected  # [catom.atom for catom in catoms]

	for atom in atoms:
		point = Point(atom.x, atom.y, atom.z)
		point = point.translate(-oa.x, -oa.y, -oa.z)
		point = point.rotate_by_quaternion(quat)
		point = point.translate(oa.x, oa.y, oa.z)
		atom.x, atom.y, atom.z = point.X, point.Y, point.Z
		atom.save()

	return HttpResponse("OK")


def rotate_cluster(request):
	"""
	Вращение кластера вокруг точки. Обязательные GET параметры:
	points = json array [{x: x1, y: y1, z:z1}, {x: x2, y: y2, z: z2}]
	origin = json object {x: x0, y: y0, z: z0}
	:return: json array такой же как Points, но с другими координатами
	"""
	if 'points' not in request.GET:
		return Http404("there is no points parameter")
	if 'origin' not in request.GET:
		return Http404("there is no origin parameter")
	ax, ay, az = 0, 0, 0  # углы разворота
	if 'ax' in request.GET:
		ax = float(request.GET['ax'])
	if 'ay' in request.GET:
		ay = float(request.GET['ay'])
	if 'az' in request.GET:
		az = float(request.GET['az'])
	points = json.loads(request.GET['points'])
	origin = json.loads(request.GET['origin'])
	ox, oy, oz = float(origin['x']), float(origin['y']), float(origin['z'])
	newpoints = list()
	for point in points:
		x, y, z = float(point['x']), float(point['y']), float(point['z'])
		newpoint = rotate_by_deg(x, y, z, ox, oy, oz, ax, ay, az)
		newpoints.append(newpoint)

	ans = json.dumps(newpoints)
	return HttpResponse(ans)


def dihedral_angle_create(request):
	if "atoms" not in request.POST:
		return HttpResponse("there is no atoms parameter in POST", status=500)

	atoms = json.loads(request.POST["atoms"])
	if not isinstance(atoms, list):
		return HttpResponse("atoms must be valid list of items", status=500)

	if len(atoms) != 4:
		return HttpResponse("please specify exactly 4 atoms", status=500)

	# двугранный угол состоит из 4 атомов. Между ними обязаны быть связи
	try:
		adoc = Document.objects.get(is_active=True)
		doc_atoms = [Atom.objects.get(document=adoc, documentindex=atomid) for atomid in atoms]

		if len(doc_atoms) != 4:
			return HttpResponse("one or more atoms not found {atoms}", status=500)

		# массив из массивов по 1 или 0 элементу
		links_temp = [list(Link.objects.filter(
			atom1=doc_atoms[i], atom2=doc_atoms[i+1])) + list(Link.objects.filter(
				atom1=doc_atoms[i+1], atom2=doc_atoms[i])) for i in range(3)]

		links = [link[0] for link in links_temp if len(link)>0]

		if len(links) != 3:
			return HttpResponse("Check if all atoms linked correctly with links")

		name = f"{doc_atoms[0].documentindex}-{doc_atoms[1].documentindex}-{doc_atoms[2].documentindex}"
		newda = DihedralAngle.objects.create(
			document=adoc, name=name)
		link1 = DihedralAngleLink.objects.create()


	except Atom.DoesNotExist:
		return HttpResponse(f"One or more atoms not founded: {atoms}")

	return HttpResponse("OK")


def change_dihedral_angle(request):
	# изменение двугранного угла
	if "id" not in request.POST:
		return HttpResponse("there is no parameter: id", status=500)

	aid = int(request.POST["id"])
	angle = DihedralAngle.objects.get(id=aid)
	links = DihedralAngleLink.objects.filter(angle=angle)
	return HttpResponse("not implemented")


def valence_angle_change(request):
	# изменение валентного угла
	if "id" not in request.POST:
		return HttpResponse("there is no parameter: id", status=500)
	if "angle" not in request.POST:
		return HttpResponse("there is no parameter: angle", status=500)

	try:
		rotation_angle = float(request.POST["angle"])
		if isnan(rotation_angle):
			raise ValueError("Wrong float value for angle: NaN")
	except ValueError:
		return HttpResponse("Wrong float value for angle: {}".format(request.POST["angle"]), status=500)

	aid = int(request.POST["id"])
	angle = ValenceAngle.objects.get(id=aid)
	links = ValenceAngleLink.objects.filter(angle=angle)

	if len(links) != 2:
		return HttpResponse("wrong input info about links", status=500)

	# угол A1-A2-A3 образован 3-мя точками (центрами атомов), где
	# A2 - общий атом
	a1, a2, a3 = None, None, None
	link1, link2 = links[0].link, links[1].link
	if link1.atom1 == link2.atom1:
		a2 = link1.atom1
		a1 = link1.atom2
		a3 = link2.atom2
	elif link1.atom2 == link2.atom2:
		a2 = link1.atom2
		a1 = link1.atom1
		a3 = link2.atom1
	elif link1.atom1 == link2.atom2:
		a2 = link1.atom1
		a1 = link1.atom2
		a3 = link2.atom1
	elif link1.atom2 == link2.atom1:
		a2 = link1.atom2
		a1 = link1.atom1
		a3 = link2.atom2

	v1 = (a1.x - a2.x, a1.y - a2.y, a1.z - a2.z)  # вектор от атома a2 до атома а1
	v2 = (a3.x - a2.x, a3.y - a2.y, a3.z - a2.z)  # вектор от амтома а2 до атома а3
	vector = (v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v2[0]-v1[0]*v2[2], v1[0]*v2[1]-v1[1]*v2[0])
	q = Quater(axis=vector, angle=rotation_angle)

	active_doc = Document.objects.get(is_active=True)
	current = [a2]
	offs = [a1]
	collected = list()
	all_links = Link.objects.filter(document=active_doc)
	harvest_connected(current, offs, collected, all_links)
	collected.remove(a2)

	# цикл по собранным атомам
	for some_a in collected:
		rotated = q.rotate((some_a.x-a2.x, some_a.y-a2.y, some_a.z-a2.z))
		some_a.x = rotated[0] + a2.x
		some_a.y = rotated[1] + a2.y
		some_a.z = rotated[2] + a2.z
		some_a.save()

	value = angle_from_atoms(a1, a2, a3)
	angle.value = value
	angle.save()

	return HttpResponse("OK")


def valence_angles_autotrace(request):
	# формирование валентных углов
	# цикл по всем парам связей

	document = Document.objects.get(is_active=True)

	# удаление старых валентных углов
	old_angles = ValenceAngle.objects.filter(document=document).delete()

	all_links = Link.objects.filter(document=document)

	for i, link1 in enumerate(all_links):
		j = i+1
		while j < len(all_links):
			link2 = all_links[j]

			# есть общий атом - это валентный угол
			if (
					link1.atom1 == link2.atom1 or link1.atom1 == link2.atom2
					or link1.atom2 == link2.atom1 or link1.atom2 == link2.atom2):

				# определение "красивого" порядка атомов
				atom1, atom2, atom3 = None, None, None
				if link1.atom1 == link2.atom1:
					atom2 = link1.atom1
					if link1.atom2.id < link2.atom2.id:
						atom1 = link1.atom2
						atom3 = link2.atom2
					else:
						atom1 = link2.atom2
						atom3 = link1.atom2
				elif link1.atom1 == link2.atom2:
					atom2 = link1.atom1
					if link1.atom2.id < link2.atom1.id:
						atom1 = link1.atom2
						atom3 = link2.atom1
					else:
						atom1 = link2.atom1
						atom3 = link1.atom2
				elif link1.atom2 == link2.atom1:
					atom2 = link1.atom2
					if link1.atom1.id < link2.atom2.id:
						atom1 = link1.atom1
						atom3 = link2.atom2
					else:
						atom1 = link2.atom2
						atom3 = link1.atom1
				else:  # link1.atom2 == link2.atom2
					atom2 = link1.atom2
					if link1.atom1.id < link2.atom1.id:
						atom1 = link1.atom1
						atom3 = link2.atom1
					else:
						atom1 = link2.atom1
						atom3 = link1.atom1

				# создание нового валентного угла в БД
				value = angle_from_atoms(atom1, atom2, atom3)

				new_va = ValenceAngle.objects.create(
					document=document,
					name="{}{}-{}{}-{}{}".format(
						atom1.name, atom1.documentindex,
						atom2.name, atom2.documentindex,
						atom3.name, atom3.documentindex
					),
					value=value
				)
				ValenceAngleLink.objects.create(angle=new_va, link=link1)
				ValenceAngleLink.objects.create(angle=new_va, link=link2)
			j += 1

	return HttpResponse("OK")


def valence_angles_delete(request):
	if "id" not in request.GET:
		return HttpResponse("there is no parameter: id", status=500)

	vid = int(request.GET["id"])
	ValenceAngle.objects.get(id=vid).delete()
	return HttpResponse("OK")


# создание нового документа
def create_document(request):
	creator = "Wurka"
	if "creator" in request.POST:
		creator = request.POST["creator"]

	details = ""
	if "details" in request.POST:
		details = request.POST["details"]

	name = "Новый документ"
	if "name" in request.POST:
		name = request.POST["name"]

	new_document = Document.objects.create(name=name, details=details, creator=creator)
	return HttpResponse(new_document.id)


# получить содержание активного документа
def get_active_data(request):
	try:
		sdoc = Document.objects.get(is_active=True)
	except Document.DoesNotExist:
		sdoc = Document.objects.create(creator="noname", name="new document", is_active=True)

	clusters = dict()
	sclusters = Cluster.objects.filter(document=sdoc)
	for cluster in sclusters:
		ca = ClusterAtom.objects.filter(cluster=cluster)

		# new_cluster = {
		# 	"id": cluster.id,
		# 	"caption": cluster.caption,
		# 	"atoms": [atom.atom.id for atom in ca]
		# }
		clusters[cluster.id] = {
			"caption": cluster.caption,
			"atoms": [atom.atom.id for atom in ca]
		}

	slinks = Link.objects.filter(document=sdoc)
	links = {
		slink.id: {
			"atom1": slink.atom1.id,
			"atom2": slink.atom2.id,
			"name": "{}{}-{}{}".format(slink.atom1.name, slink.atom1.id, slink.atom2.name, slink.atom2.id),
			"value": round(slink.get_length(), 3)
		} for slink in slinks}
	bdatoms = Atom.objects.filter(document=sdoc)
	atoms = {
		a.id: {
			"documentindex": a.documentindex, "x": a.x, "y": a.y, "z": a.z, "name": a.name, "color": a.color, "radius": a.radius
		} for a in bdatoms}

	# двугранные углы
	dihedral_angles = list()
	da_from_doc = DihedralAngle.objects.filter(document=sdoc)
	for angle in da_from_doc:
		myl = DihedralAngleLink.objects.filter(angle=angle)
		if len(myl) == 4:
			buf = list()
			for m in myl:
				if m.id not in buf:
					buf.append(m.id)

			dihedral_angles.append({
				"id": angle.id,
				"name": angle.name,
				"atom1": buf[0],
				"atom2": buf[1],
				"atom3": buf[2],
				"atom4": buf[3]
			})

	# валентные углы
	valence_angles = dict()
	va_from_doc = ValenceAngle.objects.filter(document=sdoc)
	for angle in va_from_doc:
		val = ValenceAngleLink.objects.filter(angle=angle)
		if len(val) != 2:
			return HttpResponse("bad data with ValenceAngleLink", status=500)

		buf = list()  # список атомов
		for a in val:
			if a.link.atom1.id not in buf:
				buf.append(a.link.atom1.id)
			if a.link.atom2.id not in buf:
				buf.append(a.link.atom2.id)

		if len(buf) == 3:  # у валентного угла всегда 3 атома
			valence_angles[angle.id] = {
				"name": angle.name,
				"value": angle.value,
				"atom1": buf[0],
				"atom2": buf[1],
				"atom3": buf[2],
				"link1": val[0].link.id,
				"link2": val[1].link.id
			}

	adoc = {
		"name": sdoc.name,
		"clusters": clusters,
		"links": links,
		"atoms": atoms,
		"dihedral_angles": dihedral_angles,
		"valence_angles": valence_angles
	}

	return HttpResponse(json.dumps(adoc))


def open_mol_file(request):
	if "filename" not in request.GET:
		return HttpResponse("there si no parameter: filename", status=500)

	active_doc = Document.objects.get(is_active=True)

	clear = False
	if 'clear' in request.GET:
		clear = json.loads(request.GET["clear"])
	if clear:
		Link.objects.filter(document=active_doc).delete()
		Cluster.objects.filter(document=active_doc).delete()
		Atom.objects.filter(document=active_doc).delete()

	file_name = request.GET['filename']
	mol_dir = os.path.abspath(os.path.join("editor", "files", "mols"))
	file_name = os.path.join(mol_dir, file_name)
	atom_list = mol_file_data(file_name)

	mol_cluster = Cluster.objects.create(document=active_doc, caption="mol-file")
	for atom in atom_list:
		atom.save()
		ClusterAtom.objects.create(cluster=mol_cluster, atom=atom)

	return get_active_data(request)


def save_mol_file(request):
	if 'filename' not in request.POST:
		return HttpResponse("There is no filename specified!", status=500)
	file_name = json.loads(request.POST["filename"]) + ".mol"
	mol_dir = os.path.abspath(os.path.join("editor", "files", "mols"))
	file_name = os.path.join(mol_dir, file_name)

	# подготовка текста
	txt = ""
	try:
		active_doc = Document.objects.get(is_active=True)
	except Document.DoesNotExist:
		return HttpResponse("There is no active document!", status=500)
	atoms = Atom.objects.filter(document=active_doc).order_by("documentindex")
	molfiles = list()

	txt += "[Coordinates]\nType=Cartesian\n\n"

	txt += "[Atoms]\n"
	txt += "Length=Angstroms\n"
	txt += "Count={}\n".format(len(atoms))
	txt += "//No\tx\ty\tz\tName\tMass\n"
	for a in atoms:
		txt += "{}\t{}\t{}\t{}\t{}\t{}\n".format(
			a.documentindex, a.x, a.y, a.z, a.name, a.mass
		)
		if a.molfile not in molfiles:
			molfiles.append(a.molfile)
	txt += "\n"

	txt += "[Matrix Z]\n"
	txt += "Coordinates=Cartesian\n"
	txt += "Units=Hartree\n"
	matrixes = list()
	for molfile in molfiles:
		matrixes.append(MatrixZ.objects.get(owner=molfile))
	if len(matrixes) == 1:  # один кластер
		data = pickle.loads(matrixes[0].data)
		size = len(data[0])
		for i in range(size):
			atom = atoms[i % 3]  # полагается, что атомы стоят в том же порядке, что и в матрице + 3 строки на атом
			txt += atom.name + "\t" + "\t".join(["{:f}".format(v) for v in data[i][:i+1]]) + "\n"
	elif len(matrixes) == 2:  # два кластера
		data1 = pickle.loads(matrixes[0].data)
		data2 = pickle.loads(matrixes[1].data)
		size1 = len(data1)
		size2 = len(data2)
		axes = ("x", "y", "z")
		for i in range(size1):
			atom = atoms[i // 3]  # полагается, что атомы первой группы в списке стоят первыми
			nm = "{}{}{}".format(atom.name, atom.documentindex, axes[i % 3])
			txt += nm + "\t" + "\t".join(["{:f}".format(v) for v in data1[i][:i + 1]]) + "\n"
		for i in range(size2):
			atom = atoms[size1//3 + i // 3]  # полагается, что атомы второй группы в списке стоят последними
			nm = "{}{}{}".format(atom.name, atom.documentindex, axes[i % 3])
			txt += nm + "\t" + "0.000000\t"*size1 + "\t".join(["{:f}".format(v) for v in data2[i][:i + 1]]) + "\n"
	else:
		return HttpResponse("There is no algorithm to storing {} clusters".format(len(matrixes)), status=500)
	txt += "\n"
	with open(file_name, "wt") as file:
		file.write(txt)
	return HttpResponse("OK")


def save_links(request):
	if "links" not in request.GET:
		return HttpResponse("there is no parameter links", status=500)

	clear = False
	if "clear" in request.GET:
		clear = bool(request.GET)

	active_doc = Document.objects.get(is_active=True)

	if clear:
		Link.objects.filter(document=active_doc).delete()

	links = json.loads(request.GET["links"])
	for link in links:
		atom1 = Atom.objects.get(id=link["from"], document=active_doc)
		atom2 = Atom.objects.get(id=link["to"], document=active_doc)
		Link.objects.create(document=active_doc, atom1=atom1, atom2=atom2)

	return HttpResponse("OK")


def create_link(request):
	must_be = ["atom1", "atom2"]

	for must in must_be:
		if must not in request.POST:
			return HttpResponse("there is no parameter: {}".format(must), status=500)

	adoc = Document.objects.get(is_active=True)
	try:
		atom1 = Atom.objects.get(document=adoc, documentindex=int(request.POST["atom1"]))
		atom2 = Atom.objects.get(document=adoc, documentindex=int(request.POST["atom2"]))
	except ValueError:
		return HttpResponse("atom1 and atom2 must be valid integer numbers", status=500)
	except Atom.MultipleObjectsReturned:
		return HttpResponse("MultipleObjects for atom1 or atom2", status=500)
	except Atom.DoesNotExist:
		return HttpResponse("There is no such atom in cluster and document", status=500)

	Link.objects.create(document=adoc, atom1=atom1, atom2=atom2)
	return HttpResponse("OK")


def edit_cluster_move(request):
	must_be = ("cluster", "x", "y", "z")
	for must in must_be:
		if must not in request.GET:
			return HttpResponse("there is no parameter: "+must, status=500)

	active_doc = Document.objects.get(is_active=True)
	cid = int(request.GET["cluster"])
	x = float(request.GET["x"])
	y = float(request.GET["y"])
	z = float(request.GET["z"])
	cluster = Cluster.objects.get(id=cid)
	catoms = ClusterAtom.objects.filter(cluster=cluster)
	atoms = [catom.atom for catom in catoms]
	for atom in atoms:
		atom.x += x
		atom.y += y
		atom.z += z
		atom.save()

	return HttpResponse("OK")


def get_document_object(request):
	if "id" not in request.POST:
		return HttpResponse("there is no id parameter", status=500)


# @atomic
def edit_link_set_length(request):
	for must in ("link", "length"):
		if must not in request.GET:
			return HttpResponse("there is no parameter: " + must, status=500)

	link = Link.objects.get(id=int(request.GET["link"]))
	atom1 = link.atom1
	atom2 = link.atom2
	document = link.atom1.document
	all_atoms = list(Atom.objects.filter(document=document))
	all_atoms.remove(atom1)

	point1 = Point(x=atom1.x, y=atom1.y, z=atom1.z)
	point2 = Point(x=atom2.x, y=atom2.y, z=atom2.z)
	try:
		new_distance = float(request.GET["length"])
	except ValueError:
		return HttpResponse("Not valid float number: {}".format(request.GET["length"]), status=500)

	old_distance = point1.distance_to(point2)
	delta = (new_distance - old_distance)  # двигаем в обе стороны от точки

	line = Line.from_points(point1, point2)
	plane = Plane.from_line_and_point(line, point1)
	points = [Point(x=atom.x, y=atom.y, z=atom.z) for atom in all_atoms]
	on_top = dict()
	for indx, a in enumerate(all_atoms):
		point = points[indx]
		on_top[a.id] = point.on_top(plane)
	# on_top = [point.on_top(plane) for point in points]
	# TODO: заменить одной строкой
	devider = sqrt(line.kx**2 + line.ky**2 + line.kz**2)
	movex = delta * line.kx / devider
	movey = delta * line.ky / devider
	movez = delta * line.kz / devider

	all_links = Link.objects.filter(document=document)
	collected = list()
	current = [atom2]
	offs = [atom1]
	harvest_connected(current, offs, collected, all_links)
	# collected.remove(atom1)

	for indx, atom in enumerate(collected):
		if on_top[atom.id]:
			atom.x += movex
			atom.y += movey
			atom.z += movez
		# else:
		# 	atom.x -= movex
		# 	atom.y -= movey
		#	atom.z -= movez
		atom.save()

	return HttpResponse("OK")
