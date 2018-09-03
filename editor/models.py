from django.db import models
from math import sqrt


# документ (содержит атомы, кластеры, связи и т.п.)
class Document(models.Model):
	creator = models.TextField(default="Wurka")
	details = models.TextField(default="document details")
	name = models.TextField(default="document name")
	is_active = models.BooleanField(default=False)


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


# кластер (набор молекул)
class Cluster(models.Model):
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	caption = models.TextField(default="cluster")


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



