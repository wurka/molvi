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
def get_dx2_energy(request):
    cid = request.GET['id']