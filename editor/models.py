from django.db import models
from math import sqrt


# документ (содержит атомы, кластеры, связи и т.п.)
class Document(models.Model):
	creator = models.TextField(default="Wurka")
	details = models.TextField(default="document details")
	name = models.TextField(default="document name")
	is_active = models.BooleanField(default=False)


# кластер (набор молекул)
class Cluster(models.Model):
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	caption = models.TextField(default="cluster")


# двугранный угол (4 атома вряд, т.е. 3 связи)
class DihedralAngle(models.Model):
	name = models.TextField(default="Двугранный угол")
	document = models.ForeignKey(Document, on_delete=models.CASCADE)


class ValenceAngle(models.Model):
	name = models.TextField(default="Валентный угол")
	value = models.FloatField(default=0)
	document = models.ForeignKey(Document, on_delete=models.CASCADE)


# содержание .mol file-a
class MolFile(models.Model):
	text = models.TextField(default="")


class MatrixZ(models.Model):
	"""
	Матрица Z для документа (мол. файла)
	"""
	owner = models.ForeignKey(MolFile, on_delete=models.CASCADE)  # документ, к которому относится матрица
	coordinates = models.TextField(default="unknown")
	units = models.TextField(default="unknown")
	data = models.BinaryField(default=b"")  # serialised numpy array of data


# Create your models here.
class Atom(models.Model):
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	x = models.FloatField(default=0)
	y = models.FloatField(default=0)
	z = models.FloatField(default=0)
	name = models.TextField(default="atom name")
	color = models.TextField(default="#62A6DA")
	mass = models.FloatField(default=0)  #
	radius = models.FloatField(default=1)  # радиус атома в ангстремах
	molfile = models.ForeignKey(  # содержание .mol файла, из которого взять атом
		MolFile, on_delete=models.CASCADE, null=True)
	molfileindex = models.IntegerField(default=-1)  # индекс атома внутри исходного .mol файла
	documentindex = models.IntegerField(default=0)  # индекс атома внутри документа (виден пользователю)
	mentableindex = models.IntegerField(default=0)  # индекс атома по таблице мендеелеева (водород - 0, углерод-6 )
	valence = models.FloatField(default=1)  # валентность атома


# содержание кластера
class ClusterAtom(models.Model):
	atom = models.ForeignKey(Atom, on_delete=models.CASCADE)
	cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)


# связь между атомами
class Link(models.Model):
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	atom1 = models.ForeignKey(Atom, on_delete=models.CASCADE, related_name="atom1")
	atom2 = models.ForeignKey(Atom, on_delete=models.CASCADE, related_name="atom2")

	def get_length(self):
		ans = (self.atom1.x-self.atom2.x) ** 2
		ans += (self.atom1.y - self.atom2.y) ** 2
		ans += (self.atom1.z - self.atom2.z) ** 2
		ans = sqrt(ans)
		return ans


# контент для валентного угла
class ValenceAngleLink(models.Model):
	angle = models.ForeignKey(ValenceAngle, on_delete=models.CASCADE)
	link = models.ForeignKey(Link, on_delete=models.CASCADE)


# контент для двугранного угла
class DihedralAngleLink(models.Model):
	angle = models.ForeignKey(DihedralAngle, on_delete=models.CASCADE)
	link = models.ForeignKey(Link, on_delete=models.CASCADE)
