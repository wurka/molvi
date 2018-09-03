from .geom import *
from math import pi
import unittest


class TestGeom(unittest.TestCase):
	def test_1(self):
		q = Quaternion.create_quaternion(1, 0, 0, pi/2)
		self.assertAlmostEqual(q.X, 0.7071099877357483, 5)
		self.assertAlmostEqual(q.Y, 0, 5)
		self.assertAlmostEqual(q.Z, 0, 5)
		self.assertAlmostEqual(q.W, 0.7071099877357483, 5)

	def test_2(self):
		p1 = Point(1, 0, 0)
		q = Quaternion.create_quaternion(0, 0, 1, pi/2)
		p2 = p1.rotate_by_quaternion(q)
		self.assertAlmostEqual(p2.X, 0, 5)
		self.assertAlmostEqual(p2.Y, 1, 5)
		self.assertAlmostEqual(p2.Z, 0, 5)

		q = Quaternion.create_quaternion(0, 0, 1, pi)
		p2 = p1.rotate_by_quaternion(q)
		self.assertAlmostEqual(p2.X, -1, 5)
		self.assertAlmostEqual(p2.Y, 0, 5)
		self.assertAlmostEqual(p2.Z, 0, 5)


if __name__ == "__main__":
	t = TestGeom()
	t.test_1()
	t.test_2()

