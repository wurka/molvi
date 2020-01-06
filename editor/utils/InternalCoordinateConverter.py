import numpy as np
from math import sqrt, sin, cos, radians


class FindStringError(ValueError):
    pass


# класс для описания одного вхождения в ZMatrix
class ZEntry:
    def __init__(self):
        self.symbol = ""
        self.n = 0  # this atom's number
        self.r = 0.0  # distance
        self.a = 0.0  # angle
        self.d = 0.0  # dihedral angle
        # номера атомомов, учавствующих в описании связи
        self.k = 0
        self.l = 0
        self.m = 0

    def __str__(self):
        return "{}#{}: rad: {}, {}, {}, klm: {}, {}, {}".format(
            self.symbol, self.n, self.r, self.a, self.d, self.k, self.l, self.m)


class ZReader:
    @staticmethod
    def find_string(file, target: str, reset=False):
        # finds specified string in file
        target = target.strip().lower()
        skipped = 0

        if reset:
            file.seek(0)

        while 1:
            line = file.readline()
            if line == '':  # end of file
                raise FindStringError("string <" + target + "> not founded in file")

            line = line.strip().lower()

            if target == line:
                return skipped
            else:
                skipped += 1

    @staticmethod
    def read_file(file_name: str):
        # чтение файла и преобразование его в list<ZEntry>
        # если чтение не удалось => raise ValueError
        zvars = dict()

        def get_var(var_name, default_value):
            if var_name in zvars:
                return zvars[var_name]
            else:
                return float(default_value)

        with open(file_name) as file:
            ZReader.find_string(file, "Symbolic Z-matrix:")
            try:

                z_lines = ZReader.find_string(file, "Variables:") - 1  # одна строка там служебная
                while 1:
                    words = file.readline().split()
                    if len(words) != 2:
                        break
                    else:
                        zvars[words[0]] = float(words[1])
            except FindStringError:  # строки Variables: может и не быть в файле
                pass
            ZReader.find_string(file, "Symbolic Z-matrix:", True)
            file.readline()  # там есть линяя строка (Charge=.... и т.п.)
            ans = list()  # список ZEntry - результат чтения файла
            step = -1
            while 1:
                step += 1
                new_entry = ZEntry()
                words = file.readline().split()
                if len(words) < 1 or step >= z_lines:  # найдена пустая строка или все строки обработаны
                    break
                new_entry.symbol = words[0]
                if step == 0:  # у первого элемента считываем только имя
                    ans.append(new_entry)
                    continue

                if len(words) < 3:
                    raise ValueError("Wrong file format")
                new_entry.l = int(words[1])
                new_entry.r = get_var(words[2], words[2])
                if step == 1:
                    ans.append(new_entry)
                    continue

                if len(words) < 5:
                    raise ValueError("Wrong file format")
                new_entry.k = int(words[3])
                new_entry.a = get_var(words[4], words[4])
                if step == 2:
                    ans.append(new_entry)
                    continue

                if len(words) < 7:  # восьмой симов игнорится (там 0)
                    raise ValueError("Wrong file format")
                new_entry.m = int(words[5])
                new_entry.d = get_var(words[6], words[6])
                ans.append(new_entry)

            return ans

    @staticmethod
    def build_cartesian_coordinates(zentries: list):
        def point_minus_normalize(point1, point2):
            ans = np.zeros(3, dtype=np.float32)
            ans[0] = point1[0] - point2[0]
            ans[1] = point1[1] - point2[1]
            ans[2] = point1[2] - point2[2]

            # нормировка
            d = ans[0] ** 2 + ans[1] ** 2 + ans[2] ** 2
            if abs(d) <= 0.00000001:
                return ans
            d = 1.0 / sqrt(d)
            ans[0] *= d
            ans[1] *= d
            ans[2] *= d
            return ans

        def cross_product_normalize(vector1, vector2):
            ans = np.zeros(3, dtype=np.float32)
            ans[0] = vector1[1] * vector2[2] - vector1[2] * vector2[1]
            ans[1] = vector1[2] * vector2[0] - vector1[0] * vector2[2]
            ans[2] = vector1[0] * vector2[1] - vector1[1] * vector2[0]

            # нормировка
            d = ans[0] ** 2 + ans[1] ** 2 + ans[2] ** 2
            if abs(d) <= 0.00000001:
                return ans
            d = 1.0 / sqrt(d)
            ans[0] *= d
            ans[1] *= d
            ans[2] *= d
            return ans

        def scal_prod(point1, point2):
            ans = point1[0] * point2[0] + point1[1] * point2[1] + point1[2] * point2[2]
            return ans

        # ответ - Nx3 массив numpy, где N - количество точек, а ans[i, 0] - х координата
        n = len(zentries)
        for item in zentries:
            if not type(item) is ZEntry:
                raise ValueError("input must be a list of ZEntry class objects")
        ans = np.zeros([n, 3], dtype=np.float32)
        for i in range(n):
            if i == 0:
                continue  # первая точка - всегда имеет координаты (0, 0, 0)
            if i == 1:
                l = zentries[i].l - 1
                ans[i][0] = ans[l][0]
                ans[i][1] = ans[l][1]
                ans[i][2] = ans[l][2] + zentries[i].r
                continue

            if i == 2:
                l, k = zentries[i].l - 1, zentries[i].k - 1
                ans[i][0], ans[i][1], ans[i][2] = ans[l][0], ans[l][1], ans[l][2]
                ans[i][0] += zentries[i].r * sin(radians(zentries[i].a))
                ans[i][0] += zentries[i].r * sin(radians(zentries[i].a))
                continue

            if i == 6:
                i = i

            # general case
            l, k, m = zentries[i].l - 1, zentries[i].k - 1, zentries[i].m - 1
            elk = point_minus_normalize(ans[k], ans[l])
            elm = point_minus_normalize(ans[m], ans[l])
            nklm = cross_product_normalize(elk, elm)

            cos_aklm = scal_prod(elk, elm)
            sin_aklm = sqrt(1.0 - cos_aklm ** 2)
            sin_akln = sin(radians(zentries[i].a))
            cos_akln = cos(radians(zentries[i].a))
            sin_dklmn = sin(radians(zentries[i].d))
            cos_dklmn = cos(radians(zentries[i].d))
            gamma = -zentries[i].r * sin_akln * sin_dklmn
            beta = zentries[i].r * sin_akln / sin_aklm * cos_dklmn
            alpha = zentries[i].r * cos_akln - beta * cos_aklm

            # coo[n] = coo[l] + alpha*elk + beta*elm + gamma*nklm
            for j in range(3):
                ans[i][j] = ans[l][j] + alpha * elk[j] + beta * elm[j] + gamma * nklm[j]

        return ans

    @staticmethod
    def build_internal_coordinates(points: np.ndarray):
        """ zinput must be a list of cartesian points """
        ans = list()

        for i, point in enumerate(points):
            new = ZEntry()
            new.n = i

            if i == 0:
                ans.append(new)
                continue
