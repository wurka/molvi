import numpy as np
from math import sin, cos, radians


def rotate_by_deg(x, y, z, origin_x, origin_y, origin_z, ax, ay, az):
	"""
	Вращение точки x,y,z вокруг origin_x, origin_y, origin_z
	вокруг осей X, Y, Z на угол ax, ay, az соответственно
	:return: (x, y, z) новой точки
	"""
	ax = radians(ax)
	ay = radians(ay)
	az = radians(az)
	mx = np.array([[1, 0, 0], [0, cos(ax), -sin(ax)], [0, sin(ax), cos(ax)]], dtype="float32")
	my = np.array([[cos(ay), 0, sin(ay)], [0, 1, 0], [-sin(ay), 0, cos(ay)]], dtype="float32")
	mz = np.array([[cos(az), -sin(az), 0], [sin(az), cos(az), 0], [0, 0, 1]], dtype="float32")

	nx = x - origin_x
	ny = y - origin_y
	nz = z - origin_z
	npoint = np.array([[nx], [ny], [nz]], dtype="float32")
	npoint = np.dot(mx, npoint)  # поворот вокруг оси Х
	npoint = np.dot(my, npoint)  # поворот вокруг оси Y
	npoint = np.dot(mz, npoint)  # поворот вокруг оси Z
	ans_x = npoint[0][0] + origin_x
	ans_y = npoint[1][0] + origin_y
	ans_z = npoint[2][0] + origin_z
	return ans_x, ans_y, ans_z


if __name__ == "__main__":
	ans = rotate_by_deg(1, 0, 0, 0, 0, 0, 0, 90, 0)
	print(ans)
