from . import views
from django.urls import path

urlpatterns = [
    path('demo-viewer', views.demo_viewer),
    path('internal-to-cartesian', views.internal_to_cartesian),
    path('to-3d-view', views.to_3d_view),
    path('get-3d-data', views.get_3d_data),
]
