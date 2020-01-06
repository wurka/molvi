from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from editor.utils.InternalCoordinateConverter import ZReader, FindStringError
import numpy as np
import json
from .models import DemoStorage, get_storage, set_storage
import pickle


# Create your views here.
def demo_viewer(request):
    return render(request, "demo/demo-viewer.html")


# перевести внутренние координаты в декартовы
@csrf_exempt
def internal_to_cartesian(request):
    if 'text' not in request.POST:
        return HttpResponse("there is no text parameter in POST", status=500)

    tmp_file_name = 'temp.txt'

    with open(tmp_file_name, 'wt') as file:
        file.write(request.POST['text'])
        file.seek(0)
        try:
            z_entries = ZReader.read_file(tmp_file_name)
        except FindStringError:
            return HttpResponse("wrong file format", status=500)

    cartesian = ZReader.build_cartesian_coordinates(z_entries)
    ans = {
        'labels': json.dumps([x.symbol for x in z_entries]),
        'cartesian': json.dumps([{
            'x': float(c[0]),
            'y': float(c[1]),
            'z': float(c[2])
        } for c in cartesian])
    }
    return JsonResponse(ans)


@csrf_exempt
def to_3d_view(request):
    # отправить данные на 3D сцену для просмотра
    if 'coordinates' not in request.POST:
        return HttpResponse("please use POST with labels and coordinates parameters", status=500)

    jc = json.loads(request.POST['coordinates'])
    coordinates = np.zeros((len(jc), 3), dtype=np.float32)
    for index, j in enumerate(jc):
        coordinates[index][0] = j['x']
        coordinates[index][1] = j['y']
        coordinates[index][2] = j['z']

    if 'labels' not in request.POST:
        labels = [i+1 for i in range(len(coordinates))]
    else:
        labels = json.loads(request.POST['labels'])

    atoms = [{
        'label': label,
        'color': 0xff00ab,
        'x': float(coord[0]),
        'y': float(coord[1]),
        'z': float(coord[2]),
    } for label, coord in zip(labels, coordinates)]

    data_to_store = {
        'jsonAtoms': json.dumps(atoms)
    }
    set_storage(data_to_store)
    return HttpResponse("OK")


def get_3d_data(request):
    # получить данные для отрисовки в клиенте
    storage = get_storage()
    return JsonResponse(storage)
