from django.shortcuts import render
from django.http import HttpResponse, Http404
from .views_utils import *
from .mathutils import rotate_by_deg
from .models import Document, Link, Atom, Cluster, ClusterAtom, DihedralAngle, DihedralAngleLink
from .models import ValenceAngle, ValenceAngleLink
import os
import json
from .geom import Point, Line, Plane
from math import sqrt, pi
from django.db.transaction import atomic
from .geom import Quaternion, Point


# Create your views here.
def main_page(request):
	return render(request, "editor/molvi.html", {})


def open_file_dialog(request):
	return HttpResponse("OK")


def mol_file_data(file_name):
	"""
	Return Atom array, contains data from .mol file
	with name <file_name>
	:param file_name: name of .mol file
	:return: json string
	"""
	ans = ""
	atoms = list()

	active_doc = None
	try:
		active_doc = Document.objects.get(is_active=True)
	except Document.DoesNotExist:
		pass

	# чтение файла file_name
	try:
		with open(file_name) as f:
			lines = f.readlines()
	except FileNotFoundError as ex:
		ans += "error while reading .mol data. "
		ans += str(ex)
		# ans += str(os.listdir())
		return Http404(ans + ans)

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
				new_atom = Atom(x=ax, y=ay, z=az, name=name, mass=mass, document=active_doc)
				new_atom.save()
				atoms.append(new_atom)

			except ValueError as ex:
				dprint("get_last_mol_file error: " + str(ex))
				mode = "scan"
				continue
		i += 1

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
	if 'filename' not in request.GET:
		return Http404("There is no <filename> parameter!")
	file_name = request.GET['filename']
	mol_dir = os.path.abspath(os.path.join("editor", "files", "mols"))
	file_name = os.path.join(mol_dir, file_name)
	atom_list = mol_file_data(file_name)

	return HttpResponse(ans)


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

	for cur in current:  # обработаем каждый из указанных атомов
		connected = list()  # атомы, соединённые с атомом cur
		for link in all_links:
			if link.atom1 == cur:
				if link.atom2 not in offs:
					connected.append(link.atom2)
			if link.atom2 == cur:
				if link.atom2 not in offs:
					connected.append(link.atom1)



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

	return HttpResponse("OK")


	cluster = None
	link = Link.objects.get(id=lid)
	oa = Atom.objects.get(id=origin_atom_id)
	active_doc = Document.objects.get(is_active=True)
	clusters = Cluster.objects.filter(document=active_doc)

	for c in clusters:
		catoms = ClusterAtom.objects.filter(cluster=c)
		for cc in catoms:
			if cc.atom.id == origin_atom_id:
				cluster = c
				break

	if cluster is None:
		return HttpResponse("cluster not found", status=500)

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

	catoms = ClusterAtom.objects.filter(cluster=cluster)
	atoms = [catom.atom for catom in catoms]

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


def change_dihedral_angle(request):
	# изменение двугранного угла
	if "id" not in request.POST:
		return HttpResponse("there is no parameter: id", status=500)

	aid = int(request.POST["id"])
	angle = DihedralAngle.objects.get(id=aid)
	links = DihedralAngleLink.objects.filter(angle=angle)


def change_valence_angle(request):
	# изменение валентного угла
	if "id" not in request.POST:
		return HttpResponse("there is no parameter: id", status=500)

	aid = int(request.POST["id"])
	angle = ValenceAngle.objects.get(id=aid)
	links = ValenceAngleLink.objects.filter(angle=angle)


def valence_angles_autotrace(request):
	# формирование валентных углов
	# цикл по всем парам связей

	document = Document.objects.get(is_active=True)
	all_links = Link.objects.filter(document=document)

	for i, link1 in enumerate(all_links):
		j = i+1
		while j < len(all_links):
			link2 = all_links[j]

			# есть общий атом - это валентный угол
			if (
					link1.atom1 == link2.atom1 or link1.atom1 == link2.atom2
					or link1.atom2 == link2.atom1 or link1.atom2 == link2.atom2):

				# создание нового валентного угла в БД
				new_va = ValenceAngle.objects.create(
					document=document,
					name="{}-{}".format(link1.id, link2.id))
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

	clusters = list()
	sclusters = Cluster.objects.filter(document=sdoc)
	for cluster in sclusters:
		ca = ClusterAtom.objects.filter(cluster=cluster)

		new_cluster = {
			"id": cluster.id,
			"caption": cluster.caption,
			"atoms": [atom.atom.id for atom in ca]
		}
		clusters.append(new_cluster)

	slinks = Link.objects.filter(document=sdoc)
	links = [{
		"id": slink.id, "atom1": slink.atom1.id, "atom2": slink.atom2.id,
		"length": slink.get_length()
	} for slink in slinks]
	bdatoms = Atom.objects.filter(document=sdoc)
	atoms = [{
		"id": a.id, "x": a.x, "y": a.y, "z": a.z, "name": a.name, "color": a.color, "radius": a.radius
	} for a in bdatoms]

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
	valence_angles = list()
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
			valence_angles.append({
				"id": angle.id,
				"name": angle.name,
				"atom1": buf[0],
				"atom2": buf[1],
				"atom3": buf[2],
				"link1": val[0].link.id,
				"link2": val[1].link.id
			})

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

	clear = False
	if 'clear' in request.GET:
		clear = json.loads(request.GET["clear"])

	file_name = request.GET['filename']
	mol_dir = os.path.abspath(os.path.join("editor", "files", "mols"))
	file_name = os.path.join(mol_dir, file_name)
	atom_list = mol_file_data(file_name)

	active_doc = Document.objects.get(is_active=True)
	if clear:
		Link.objects.filter(document=active_doc).delete()
		Cluster.objects.filter(document=active_doc).delete()
		Atom.objects.filter(document=active_doc).delete()
	mol_cluster = Cluster.objects.create(document=active_doc, caption="mol-file")
	for atom in atom_list:
		atom.save()
		ClusterAtom.objects.create(cluster=mol_cluster, atom=atom)

	return get_active_data(request)


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
	all_atoms = Atom.objects.filter(document=document)

	point1 = Point(x=atom1.x, y=atom1.y, z=atom1.z)
	point2 = Point(x=atom2.x, y=atom2.y, z=atom2.z)
	new_distance = float(request.GET["length"])
	old_distance = point1.distance_to(point2)
	delta = (new_distance - old_distance)/2.0  # двигаем в обе стороны от точки
	middle = Point(
		x=(atom1.x+atom2.x)/2,
		y=(atom1.y+atom2.y)/2,
		z=(atom1.z+atom2.z)/2
	)
	line = Line.from_points(point1, middle)
	plane = Plane.from_line_and_point(line, middle)
	points = [Point(x=atom.x, y=atom.y, z=atom.z) for atom in all_atoms]
	on_top = [point.on_top(plane) for point in points]
	devider = sqrt(line.kx**2 + line.ky**2 + line.kz**2)
	movex = delta * line.kx / devider
	movey = delta * line.ky / devider
	movez = delta * line.kz / devider

	for indx, atom in enumerate(all_atoms):
		if on_top[indx]:
			atom.x += movex
			atom.y += movey
			atom.z += movez
		else:
			atom.x -= movex
			atom.y -= movey
			atom.z -= movez
		atom.save()

	return HttpResponse("OK")







