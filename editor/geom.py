from math import sqrt, cos, sin
import numpy as np


class Quaternion:
	X = 0
	Y = 0
	Z = 0
	W = 1

	def __init__(self):
		self.X = 0
		self.Y = 0
		self.Z = 0
		self.W = 1

	def __str__(self):
		return "X: {}, Y: {}, Z: {}, W: {}".format(self.X, self.Y, self.Z, self.W)

	def normalize(self):
		length = sqrt(self.X**2 + self.Y**2 + self.Z**2 + self.W**2)
		self.X /= length
		self.Y /= length
		self.Z /= length
		self.W /= length

	@staticmethod
	def create_quaternion(vx: float, vy: float, vz: float, radians: float):
		vl = sqrt(vx**2+vy**2+vz**2)
		vx, vy, vz = vx/vl, vy/vl, vz/vl
		ans = Quaternion()
		ans.W = cos(radians/2)
		ans.X = vx*sin(radians/2)
		ans.Y = vy*sin(radians/2)
		ans.Z = vz*sin(radians/2)
		return ans


class Point:
	X = 0.0  # type: float
	Y = 0.0  # type: float
	Z = 0.0  # type: float

	def __init__(self, x, y, z):
		self.X = x
		self.Y = y
		self.Z = z

	def __str__(self):
		return "{}, {}, {}".format(self.X, self.Y, self.Z)

	def on_top(self, plane: "Plane"):
		"""Проверка, что точка по некоторую сторону от плоскости"""
		x = plane.A*self.X + plane.B*self.Y + plane.C*self.Z + plane.D
		if x >= 0:
			return True
		else:
			return False

	def distance_to(self, point: "Point"):
		"""Вычисление расстояния до другой точки"""
		ans = (point.X - self.X)**2
		ans += (point.Y - self.Y)**2
		ans += (point.Z - self.Z)**2
		return sqrt(ans)

	def translate(self, gox, goy, goz):
		ansx = self.X + gox
		ansy = self.Y + goy
		ansz = self.Z + goz
		return Point(ansx, ansy, ansz)

	def rotate_by_quaternion(self, q: Quaternion):
		x = q.X
		y = q.Y
		z = q.Z
		w = q.W
		a = (self.X, self.Y, self.Z)
		ansx = a[0] * (1 - 2*y*y - 2*z*z) + a[1] * (2*x*y - 2*z*w) + a[2] * (2*x*z + 2*y*w)
		ansy = a[0] * (2*x*y + 2*z*w) + a[1] * (1 - 2*x*x - 2*z*z) + a[2] * (2*y*z - 2*x*w)
		ansz = a[0] * (2*x*z - 2*y*w) + a[1] * (2*y*z + 2*x*w) + a[2] * (1 - 2*x*x - 2*y*y)
		ans = Point(ansx, ansy, ansz)
		return ans


class Plane:
	"""Плоскость, описываемая уравнением
	Ax+By+Cz+D=0
	"""
	A = 0  # type: float
	B = 0  # type: float
	C = 0  # type: float
	D = 0  # type: float

	def __init__(self, a, b, c, d):
		self.A = a
		self.B = b
		self.C = c
		self.D = d

	@staticmethod
	def from_line_and_point(line: "Line", point: Point):
		"""Плоскость, перпендикулярная прямой line и проходящая через точку point"""
		ans = Plane(
			a=line.kx,
			b=line.ky,
			c=line.kz,
			d=-line.kx*point.X - line.ky*point.Y - line.kz*point.Z
		)
		return ans


class Line:
	"""Прямая. Каноническое уравнение: x-x0/kx = y-y0/ky = z-z0/kz"""
	x0 = 0  # type: float
	y0 = 0  # type: float
	z0 = 0  # type: float
	kx = 0  # type: float
	ky = 0  # type: float
	kz = 0  # type: float

	def __init__(self, x0, y0, z0, kx, ky, kz):
		self.x0 = x0
		self.y0 = y0,
		self.z0 = z0
		self.kx = kx
		self.ky = ky
		self.kz = kz

	@staticmethod
	def from_points(point1: Point, point2: Point):
		ans = Line(
			x0=point1.X,
			y0=point1.Y,
			z0=point1.Z,
			kx=point2.X-point1.X,
			ky=point2.Y-point1.Y,
			kz=point2.Z-point1.Z
		)

		return ans
