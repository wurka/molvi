from django.http import HttpResponse
import os
from django.conf import settings
from .views import get_with_parameters, post_with_parameters
from .models import Cluster, ClusterAtom, MatrixZ
from json import dumps, loads
import pickle

def get_cwd(request):
	temp_folder = os.path.join(settings.SETTINGS_FOLDER, "temp")

	return HttpResponse(settings.SETTINGS_FOLDER + "<br>OK")


@post_with_parameters("id")
def save_calibration(request):
	cid = request.POST["id"]
	try:
		cluster = Cluster.objects.get(id=cid)
		catoms = ClusterAtom.objects.filter(cluster=cluster)
		atoms_object = [{
			"x": ca.atom.x,
			"y": ca.atom.y,
			"z": ca.atom.z,
		} for ca in catoms]
		atoms_json = dumps(atoms_object)

		if not os.path.isdir(settings.TEMP_FOLDER):
			os.makedirs(settings.TEMP_FOLDER)

		with open(os.path.join(settings.TEMP_FOLDER, "calibration_cluster.txt"), "wt") as file:
			file.write(atoms_json)

	except Cluster.DoesNotExist:
		return HttpResponse(f"There is no cluster with id {cid}", status=500)

	return HttpResponse("OK")


@get_with_parameters("id")
def get_energy(request):
	cid = request.GET['id']
	try:
		cluster = Cluster.objects.get(id=cid)
	except Cluster.DoesNotExist:
		return HttpResponse(f"there si no Cluster with id {cid}", status=500)

	cluster_atoms = ClusterAtom.objects.filter(cluster=cluster)
	mols = [ca.atom.molfile for ca in cluster_atoms]
	if len(mols) == 0:
		return HttpResponse("there is no mol files associated with cluster", status=500)
	for i, item in enumerate(mols[:-1]):
		if item.id != mols[i+1].id:
			return HttpResponse("multiply mol files detected inside one cluster", status=500)

	molfile = mols[0]
	matrix = MatrixZ.objects.filter(owner=molfile)
	if len(matrix) == 0:
		return HttpResponse(
			f"there is no MatrixZ objects associated with this molfile (id: {molfile.id})", status=500)

	if len(matrix) > 1:
		return HttpResponse(
			f"there is multiple MatrixZ objects ({len(matrix)}) associated with molfile", status=500
		)

	zmatrix = pickle.loads(matrix[0].data)

	try:
		with open(os.path.join(settings.TEMP_FOLDER, "calibration_cluster.txt"), "rt") as file:
			txt = file.read()
	except (OSError, IOError):
		return HttpResponse(f"error while reading calibration file. try to recalibrate", status=500)

	calibration = loads(txt)

	e = 0  # энергия
	atoms = list(cluster_atoms)
	atoms.sort(key=lambda catom: catom.atom.documentindex)  # сортировка по индексу в документе

	for i, atom in enumerate(atoms):  # цикл по всем атомам
		for j, atom2 in enumerate(atoms):  # по всем парам атомов
			try:
				f = zmatrix[i, j]
				original = calibration[i]["x"] - calibration[j]["x"]
				new = atom.atom.x - atom2.atom.x
				e += f*(new - original)**2

				original = calibration[i]["y"] - calibration[j]["y"]
				new = atom.atom.y - atom2.atom.y
				e += f * (new - original) ** 2

				original = calibration[i]["z"] - calibration[j]["z"]
				new = atom.atom.z - atom2.atom.z
				e += f * (new - original) ** 2

			except IndexError:
				element = f"[{i}, {j}]"
				return HttpResponse(
					f"wrong zmatrix format element {element} does not exists", status=500)
			except ValueError:
				return HttpResponse(
					f"wrong float format in zmatrix: {zmatrix[i,j]}", status=500
				)

	return HttpResponse(f"energy is: {e}")
