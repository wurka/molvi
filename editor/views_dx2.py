from django.http import HttpResponse
import os
from django.conf import settings
from .views import get_with_parameters, post_with_parameters
from .models import Cluster, ClusterAtom
from json import dumps


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

    text = mols[0].text

    return HttpResponse(text)
