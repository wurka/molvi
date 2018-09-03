"""molvi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
	path('molvi.html', views.main_page),
	path('server/open-file-dialog', views.open_file_dialog),
	path('get-last-mol-file', views.get_last_mol_file),
	path('save-document', views.save_document),
	path('get-documents', views.get_documents),
	path('get-mol-files', views.get_mol_files),
	path('get-document', views.get_document),
	path('get-mol-file', views.get_mol_file),
	path('rotate-cluster', views.rotate_cluster),
	path('get-active-data', views.get_active_data),  # получить информацию из активного документа
	path('open-mol-file', views.open_mol_file),  # открыть mol file и поместить информацию из него в активный документ
	path('save-links', views.save_links),  # сохранить на сервере связи (для активного документа)
	path('edit-cluster-move', views.edit_cluster_move),  # переместить кластер
	path('edit-link-set-length', views.edit_link_set_length),  # изменить длину связи
	path('rotate-cluster-around-link', views.rotate_cluster_around_link),  # повернуть кластер вокруг связи
]
