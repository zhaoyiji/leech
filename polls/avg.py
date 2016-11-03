# -*- encoding: utf-8 -*-

CLOSED = 2


class AvgLine(object):
    def __init__(self, data, count):
        self._data = data
        self._count = count
        self._avg = []

        self.calc()

    def get(self):
        return self._avg

    def calc(self):
        """

        :rtype: []
        """
        if len(self._data) < self._count:
            return []

        total = 0.0
        count = self._count - 1
        for i in range(0, count):
            total += self._data[i][CLOSED]
            self._avg.append(0.0)

        total += self._data[count][CLOSED]
        avg = total / self._count
        self._avg.append(avg)

        count = self._count
        for i in range(count, len(self._data)):
            total += self._data[i][CLOSED]
            total -= self._data[i - count][CLOSED]
            avg = total / count
            self._avg.append(avg)


if __name__ == "__main__":
    print "avg test"
