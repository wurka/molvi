from django.http import FileResponse


def favicon(request):
    file = open('demo/static/favicon.ico', 'br')
    return FileResponse(file)