from django.db import models
import json


# Create your models here.
class DemoStorage(models.Model):
    jsonAtoms = models.TextField(default=json.dumps([{
        'label': "H1",
        'color': 0xCA0030,
        'x': 0,
        'y': 0,
        'z': 0
    }]))


def my_storage():
    all_items = DemoStorage.objects.all()
    if len(all_items) != 1:
        DemoStorage.objects.all().delete()
        ans = DemoStorage.objects.create()
    else:
        ans = all_items[0]
    return ans


def get_storage():
    storage = my_storage()
    ans = {
        'jsonAtoms': storage.jsonAtoms
    }
    return ans


def set_storage(parameters):
    storage = my_storage()
    if 'jsonAtoms' in parameters:
        storage.jsonAtoms = parameters['jsonAtoms']
    storage.save()
