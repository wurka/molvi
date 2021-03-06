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
# from django.contrib import admin
from django.urls import path  # , include
from . import views
from . import optimizer
from . import views2
from . import views_dx2

urlpatterns = [
	path('molvi.html', views.main_page),
	path('server/open-file-dialog', views.open_file_dialog),
	path('get-last-mol-file', views.get_last_mol_file),
	path('save-document', views.save_document),
	path('save-to-active', views.save_to_active),
	path('get-documents', views.get_documents),
	path('get-mol-files', views.get_mol_files),
	path('get-document', views.get_document),
	path('get-mol-file', views.get_mol_file),
	path('rotate-cluster', views.rotate_cluster),
	path('get-active-data', views.get_active_data),  # получить информацию из активного документа
	path('open-mol-file', views.open_mol_file),  # открыть mol file и поместить информацию из него в активный документ
	path('save-mol-file', views.save_mol_file),  # сохранить mol file из активного документа
	path('save-links', views.save_links),  # сохранить на сервере связи (для активного документа)
	path('create-link', views.create_link),  # создать новую связь
	path('edit-cluster-move', views.edit_cluster_move),  # переместить кластер
	path('edit-link-set-length', views.edit_link_set_length),  # изменить длину связи
	path('rotate-cluster-around-link', views.rotate_cluster_around_link),  # повернуть кластер вокруг связи

	path('valence-angles-autotrace', views.valence_angles_autotrace),  # построить автоматически список валентных углов
	path('valence-angles-delete', views.valence_angles_delete),  # удалить валентный угол
	path('valence-angles-change', views.valence_angle_change),  # изменить валентный угол

	path("dihedral-angle-create", views.dihedral_angle_create),  # создать двугранный угол
	path("dihedral-angle-delete", views.dihedral_angle_delete),  # удалить двугранный угол
	path("dihedral-angle-optimize", views.dihedral_angle_optimize),  # оптимизировать двугранный угол

	path('debug-optimizer', optimizer.debug),
	path('optimize', optimizer.optimize),  # оптимизировать молекулу по энергии
	path('get-optimise-sources', optimizer.get_optimise_sources),
	path('save-atoms-to-file', views2.save_atoms_to_file),

	path('save-active-doc', views2.save_active_doc),
	path('load-document', views2.load_document),
	path('delete-document', views2.delete_document),

	path('get-cwd', views_dx2.get_cwd),
	path('dx2/save-calibration', views_dx2.save_calibration),
	path('dx2/get-energy', views_dx2.get_energy),
]
